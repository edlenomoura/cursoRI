#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BUSCA SEMÂNTICA COM BERTIMBAU E ELASTICSEARCH
================================================================================

Este script demonstra busca semântica usando embeddings do BERTimbau.

BUSCA SEMÂNTICA vs BUSCA LÉXICA:

BUSCA LÉXICA (BM25, TF-IDF):
- Correspondência exata de palavras
- "carro" não encontra "automóvel" ou "veículo"
- Rápida, mas limitada
- Não entende sinônimos ou contexto

BUSCA SEMÂNTICA (BERT):
- Baseada em similaridade de significado
- "carro" ≈ "automóvel" ≈ "veículo" ≈ "carro"
- Entende sinônimos, contexto, paráfrases
- Mais lenta, mais precisa para queries complexas

TIPOS DE BUSCA DEMONSTRADOS:

1. kNN (k-Nearest Neighbors):
   - Busca os k vetores mais próximos
   - Usa índice HNSW (Hierarchical Navigable Small World)
   - Muito rápido, aproximado

2. Script Score com Cosine:
   - Calcula similaridade cosseno exata
   - Mais lento, mais preciso
   - Permite combinar com filtros

3. Busca Híbrida:
   - Combina busca léxica (BM25) + semântica (BERT)
   - Usa RRF (Reciprocal Rank Fusion) ou weighted sum
   - Melhor dos dois mundos

================================================================================
"""

from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import json
import warnings

# Suprimir warning de resume_download deprecated
warnings.filterwarnings("ignore", message=".*resume_download.*", category=FutureWarning)

# Mesmo modelo usado na indexação
BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"

def carregar_bertimbau():
    """Carrega BERTimbau para gerar embeddings das consultas"""
    print("\n📥 Carregando BERTimbau...")
    
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    model = AutoModel.from_pretrained(BERTIMBAU_MODEL)
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    print(f"   ✓ Modelo carregado ({device})")
    
    return tokenizer, model, device

def gerar_embedding_consulta(consulta, tokenizer, model, device):
    """
    FUNÇÃO: Gera embedding para consulta do usuário
    
    Consultas geralmente são curtas, então não precisa chunking.
    Usa token [CLS] para representar a consulta.
    
    Args:
        consulta: String da consulta
        tokenizer, model, device: BERTimbau
        
    Returns:
        numpy.array: Embedding de 768 dimensões
    """
    inputs = tokenizer(
        consulta,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Embedding do token [CLS]
    cls_embedding = outputs.last_hidden_state[0][0].cpu().numpy()
    
    return cls_embedding

def conectar_elasticsearch():
    """Conecta ao ElasticSearch"""
    es = Elasticsearch(['http://localhost:9200'])
    
    if not es.ping():
        raise Exception("ElasticSearch não está rodando!")
    
    return es

def busca_knn(es, consulta_embedding, campo='embedding_highlight', k=10):
    """
    TIPO 1: BUSCA kNN (k-Nearest Neighbors)
    
    kNN no ElasticSearch:
    - Usa algoritmo HNSW (Hierarchical Navigable Small World)
    - Busca APROXIMADA (não exata, mas muito rápida)
    - Ideal para grandes volumes de dados
    - Retorna k documentos mais similares
    
    SIMILARIDADE COSSENO:
    - Mede ângulo entre vetores
    - score = 1 + cosine(query_vector, doc_vector) / 2
    - Range: [0, 1], onde 1 = idêntico
    
    Args:
        es: Cliente ElasticSearch
        consulta_embedding: Vetor da consulta
        campo: Campo do embedding ('embedding_title' ou 'embedding_highlight')
        k: Número de resultados
        
    Returns:
        dict: Resposta do ElasticSearch
    """
    query = {
        "knn": {
            "field": campo,
            "query_vector": consulta_embedding.tolist(),
            "k": k,
            "num_candidates": 100  # Quantos candidatos avaliar (trade-off velocidade/qualidade)
        }
    }
    
    resposta = es.search(
        index='ementas_bertimbau',
        body=query,
        size=k
    )
    
    return resposta

def busca_script_score(es, consulta_embedding, campo='embedding_highlight', tamanho=10):
    """
    TIPO 2: BUSCA com SCRIPT SCORE (Similaridade Cosseno Exata)
    
    SCRIPT SCORE:
    - Calcula score customizado via Painless script
    - Similaridade cosseno EXATA (não aproximada)
    - Mais lento que kNN
    - Permite combinar com filtros booleanos
    
    FÓRMULA COSSENO:
    cosineSimilarity(query_vector, doc_vector) + 1.0
    - Retorna valor entre 0 e 2
    - Quanto maior, mais similar
    
    Args:
        es: Cliente ElasticSearch
        consulta_embedding: Vetor da consulta
        campo: Campo do embedding
        tamanho: Número de resultados
    """
    query = {
        "script_score": {
            # Match all: considera todos documentos
            "query": {"match_all": {}},
            
            # Script Painless para calcular similaridade
            "script": {
                "source": f"cosineSimilarity(params.query_vector, '{campo}') + 1.0",
                "params": {
                    "query_vector": consulta_embedding.tolist()
                }
            }
        }
    }
    
    resposta = es.search(
        index='ementas_bertimbau',
        body={"query": query, "size": tamanho}
    )
    
    return resposta

def busca_hibrida(es, consulta_texto, consulta_embedding, campo_texto='highlight', 
                  campo_embedding='embedding_highlight', tamanho=10, peso_lexico=0.5):
    """
    TIPO 3: BUSCA HÍBRIDA (Léxica + Semântica)
    
    COMBINAÇÃO DE SCORES:
    - Score léxico (BM25): captura keywords exatas
    - Score semântico (BERT): captura significado
    - Score final = peso × léxico + (1-peso) × semântico
    
    QUANDO USAR:
    - Léxico: importante para nomes próprios, termos técnicos
    - Semântico: importante para conceitos, sinônimos
    - Híbrido: melhor de ambos
    
    Args:
        es: Cliente ElasticSearch
        consulta_texto: Texto da consulta (para busca léxica)
        consulta_embedding: Vetor da consulta (para busca semântica)
        campo_texto: Campo text para BM25
        campo_embedding: Campo vector para BERT
        tamanho: Número de resultados
        peso_lexico: Peso da busca léxica (0.0 a 1.0)
    """
    peso_semantico = 1.0 - peso_lexico
    
    query = {
        "bool": {
            "should": [
                # Componente LÉXICO (BM25)
                {
                    "match": {
                        campo_texto: {
                            "query": consulta_texto,
                            "boost": peso_lexico
                        }
                    }
                },
                # Componente SEMÂNTICO (BERT cosine)
                {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": f"{peso_semantico} * (cosineSimilarity(params.query_vector, '{campo_embedding}') + 1.0)",
                            "params": {
                                "query_vector": consulta_embedding.tolist()
                            }
                        }
                    }
                }
            ]
        }
    }
    
    resposta = es.search(
        index='ementas_bertimbau',
        body={"query": query, "size": tamanho}
    )
    
    return resposta

def exibir_resultados(resposta, titulo):
    """Exibe resultados formatados"""
    print(f"\n{'='*80}")
    print(titulo)
    print('='*80)
    
    hits = resposta['hits']
    total = hits['total']['value']
    tempo = resposta['took']
    
    print(f"\nTotal: {total} | Tempo: {tempo}ms\n")
    
    if total == 0:
        print("Nenhum resultado encontrado.")
        return
    
    for i, hit in enumerate(hits['hits'], 1):
        score = hit['_score']
        doc = hit['_source']
        
        print(f"{i}. Score: {score:.4f}")
        print(f"   ID: {doc.get('id', 'N/A')}")
        print(f"   Título: {doc.get('title', 'N/A')[:100]}")
        print(f"   Órgão: {doc.get('judging_organ', 'N/A')}")
        
        highlight = doc.get('highlight', '')
        if len(highlight) > 200:
            highlight = highlight[:200] + '...'
        print(f"   Texto: {highlight}")
        print()

def comparar_buscas(es, consulta, tokenizer, model, device):
    """
    FUNÇÃO ESPECIAL: Compara busca semântica vs léxica
    
    Executa a mesma consulta com:
    1. BM25 puro (léxico)
    2. BERTimbau puro (semântico)
    3. Híbrido (50% cada)
    
    Mostra diferenças práticas entre abordagens.
    """
    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO: LÉXICA vs SEMÂNTICA vs HÍBRIDA")
    print(f"Consulta: '{consulta}'")
    print('='*80)
    
    # Gera embedding da consulta
    consulta_embedding = gerar_embedding_consulta(consulta, tokenizer, model, device)
    
    # 1. Busca LÉXICA (BM25 puro)
    print("\n📖 BUSCA LÉXICA (BM25):")
    resp_lexico = es.search(
        index='ementas_bertimbau',
        body={
            "query": {"match": {"highlight": consulta}},
            "size": 5
        }
    )
    
    # 2. Busca SEMÂNTICA (BERT puro)
    print("🧠 BUSCA SEMÂNTICA (BERTimbau):")
    resp_semantico = busca_knn(es, consulta_embedding, k=5)
    
    # 3. Busca HÍBRIDA (50/50)
    print("🔀 BUSCA HÍBRIDA (BM25 + BERT):")
    resp_hibrido = busca_hibrida(es, consulta, consulta_embedding, tamanho=5, peso_lexico=0.5)
    
    # Comparação lado a lado
    print("\n📊 TOP 3 RESULTADOS:\n")
    print(f"{'Pos':<5} {'Léxica (BM25)':<30} {'Semântica (BERT)':<30} {'Híbrida':<30}")
    print("-" * 100)
    
    for i in range(min(3, len(resp_lexico['hits']['hits']))):
        lex = resp_lexico['hits']['hits'][i] if i < len(resp_lexico['hits']['hits']) else None
        sem = resp_semantico['hits']['hits'][i] if i < len(resp_semantico['hits']['hits']) else None
        hyb = resp_hibrido['hits']['hits'][i] if i < len(resp_hibrido['hits']['hits']) else None
        
        lex_id = lex['_source']['id'][:25] if lex else "N/A"
        sem_id = sem['_source']['id'][:25] if sem else "N/A"
        hyb_id = hyb['_source']['id'][:25] if hyb else "N/A"
        
        lex_score = f"{lex['_score']:.2f}" if lex else "N/A"
        sem_score = f"{sem['_score']:.2f}" if sem else "N/A"
        hyb_score = f"{hyb['_score']:.2f}" if hyb else "N/A"
        
        print(f"{i+1:<5} {lex_id[:25]:<30} {sem_id[:25]:<30} {hyb_id[:25]:<30}")
        print(f"      Score: {lex_score:<20} Score: {sem_score:<20} Score: {hyb_score:<20}")
        print()
    
    print("\n🔍 OBSERVAÇÕES:")
    print("  - Léxica: melhor para nomes próprios e termos exatos")
    print("  - Semântica: melhor para sinônimos e conceitos")
    print("  - Híbrida: combina pontos fortes de ambas")

def estatisticas_indice(es):
    """Exibe estatísticas do índice"""
    print(f"\n{'='*80}")
    print("ESTATÍSTICAS DO ÍNDICE BERTIMBAU")
    print('='*80)
    
    contagem = es.count(index='ementas_bertimbau')
    print(f"Total de documentos: {contagem['count']}")
    
    # Agregação por tipo
    resposta = es.search(
        index='ementas_bertimbau',
        body={
            'size': 0,
            'aggs': {
                'tipos': {
                    'terms': {
                        'field': 'type',
                        'size': 10
                    }
                }
            }
        }
    )
    
    print("\nDocumentos por tipo:")
    for bucket in resposta['aggregations']['tipos']['buckets']:
        print(f"  {bucket['key']}: {bucket['doc_count']}")

def main():
    """Função principal com exemplos de buscas"""
    print("="*80)
    print("BUSCA SEMÂNTICA COM BERTIMBAU")
    print("="*80)
    print()
    print("Este script demonstra busca semântica usando embeddings do BERTimbau.")
    print()
    
    try:
        # Carregar modelo
        tokenizer, model, device = carregar_bertimbau()
        
        # Conectar ES
        es = conectar_elasticsearch()
        print("✓ Conectado ao ElasticSearch")
        
        # Verifica índice
        if not es.indices.exists(index='ementas_bertimbau'):
            print("\n❌ Índice 'ementas_bertimbau' não encontrado!")
            print("Execute primeiro: python indexaBertimbauElastic.py")
            return
        
        # Estatísticas
        estatisticas_indice(es)
        
        # === EXEMPLOS DE BUSCAS ===
        
        # Exemplo 1: kNN
        print("\n" + "="*80)
        print("EXEMPLO 1: BUSCA kNN (k-Nearest Neighbors)")
        print("="*80)
        consulta1 = "responsabilidade civil por danos morais"
        print(f"Consulta: '{consulta1}'")
        emb1 = gerar_embedding_consulta(consulta1, tokenizer, model, device)
        resp1 = busca_knn(es, emb1, k=5)
        exibir_resultados(resp1, "Resultados kNN (Top 5)")
        
        # Exemplo 2: Script Score
        print("\n" + "="*80)
        print("EXEMPLO 2: BUSCA com SCRIPT SCORE (Cosine exato)")
        print("="*80)
        consulta2 = "indenização por acidente de trânsito"
        print(f"Consulta: '{consulta2}'")
        emb2 = gerar_embedding_consulta(consulta2, tokenizer, model, device)
        resp2 = busca_script_score(es, emb2, tamanho=5)
        exibir_resultados(resp2, "Resultados Script Score (Top 5)")
        
        # Exemplo 3: Busca Híbrida
        print("\n" + "="*80)
        print("EXEMPLO 3: BUSCA HÍBRIDA (Léxica + Semântica)")
        print("="*80)
        consulta3 = "nexo de causalidade"
        print(f"Consulta: '{consulta3}'")
        emb3 = gerar_embedding_consulta(consulta3, tokenizer, model, device)
        resp3 = busca_hibrida(es, consulta3, emb3, tamanho=5, peso_lexico=0.5)
        exibir_resultados(resp3, "Resultados Híbridos (Top 5)")
        
        # Comparação direta
        comparar_buscas(es, "responsabilidade civil", tokenizer, model, device)
        
        print("\n" + "="*80)
        print("✓ EXEMPLOS CONCLUÍDOS!")
        print("="*80)
        print("\n🎓 EXERCÍCIOS SUGERIDOS:")
        print("  1. Teste consultas com sinônimos (ex: 'veículo' vs 'carro')")
        print("  2. Compare busca semântica com BM25 puro")
        print("  3. Ajuste peso_lexico na busca híbrida")
        print("  4. Experimente consultas em linguagem natural")
        print()
        print("📚 PARA ENTENDER MELHOR:")
        print("  - BERTimbau: https://github.com/neuralmind-ai/portuguese-bert")
        print("  - BERT paper: https://arxiv.org/abs/1810.04805")
        print("  - Dense Vectors ES: https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
