#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
INDEXAÇÃO COM BERTIMBAU E ELASTICSEARCH
================================================================================

Este script demonstra como usar embeddings do BERTimbau (BERT em português)
para indexação semântica de documentos no ElasticSearch.

BERTIMBAU:
- Modelo BERT treinado em português brasileiro
- Produzido pela equipe Neuralmind
- Base para busca semântica (entende significado, não apenas keywords)

ESTRATÉGIA DE EMBEDDING:

1. Token [CLS] (Classification):
   - Primeiro token de cada sequência BERT
   - Representa contexto completo da sentença
   - Usado como embedding da sentença

2. Textos Longos (> 512 tokens):
   - BERTimbau tem limite de 512 tokens
   - Solução: dividir em chunks de ~500 tokens
   - Gerar embedding [CLS] para cada chunk
   - MÉDIA dos embeddings = embedding do documento

COMPARAÇÃO COM MODELOS TRADICIONAIS:

BM25/TF-IDF (léxicos):
- Baseados em correspondência exata de palavras
- "carro" ≠ "automóvel" ≠ "veículo"
- Rápidos, mas limitados

BERTimbau (semântico):
- Entende similaridade semântica
- "carro" ≈ "automóvel" ≈ "veículo"
- Captura sinônimos e contexto
- Mais lento, mais preciso

================================================================================
"""

import json
import os
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

# Configuração global
BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"
MAX_LENGTH = 512  # Limite do BERT
CHUNK_SIZE = 500  # Tamanho do chunk (deixa margem para tokens especiais)

def carregar_bertimbau():
    """
    FUNÇÃO: Carrega modelo e tokenizer do BERTimbau
    
    BERTimbau: BERT treinado em corpus de 2.7B palavras em português.
    Modelos disponíveis:
    - bert-base-portuguese-cased: 12 layers, case-sensitive
    - bert-large-portuguese-cased: 24 layers, mais pesado
    
    Returns:
        tuple: (tokenizer, model)
    """
    print("\n📥 Carregando BERTimbau...")
    print(f"   Modelo: {BERTIMBAU_MODEL}")
    
    # Tokenizer: converte texto em tokens que o BERT entende
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    
    # Model: rede neural BERT
    model = AutoModel.from_pretrained(BERTIMBAU_MODEL)
    
    # Modo eval: desativa dropout, batch norm, etc.
    model.eval()
    
    # GPU se disponível, senão CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    print(f"   ✓ Modelo carregado")
    print(f"   Device: {device}")
    print(f"   Dimensão dos embeddings: 768")
    
    return tokenizer, model, device

def gerar_embedding_cls(texto, tokenizer, model, device):
    """
    FUNÇÃO: Gera embedding usando token [CLS]
    
    TOKEN [CLS]:
    - Primeiro token de toda sequência BERT
    - Durante pré-treinamento, aprende a representar contexto completo
    - Ideal para classificação e similaridade semântica
    
    PROCESSO:
    1. Tokeniza texto
    2. Passa pelo BERT
    3. Extrai hidden state do token [CLS]
    4. Retorna vetor de 768 dimensões
    
    Args:
        texto: String de entrada
        tokenizer: Tokenizer do BERT
        model: Modelo BERT
        device: 'cuda' ou 'cpu'
        
    Returns:
        numpy.array: Embedding de 768 dimensões
    """
    # Tokeniza com padding e truncate
    # return_tensors='pt': retorna tensors PyTorch
    inputs = tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True
    )
    
    # Move para GPU/CPU
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Inference sem calcular gradientes (mais rápido)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # last_hidden_state: [batch_size, sequence_length, hidden_size]
    # [0]: primeiro item do batch
    # [0]: primeiro token (CLS)
    # .cpu().numpy(): converte para numpy array
    cls_embedding = outputs.last_hidden_state[0][0].cpu().numpy()
    
    return cls_embedding

def gerar_embedding_documento(texto, tokenizer, model, device):
    """
    FUNÇÃO: Gera embedding para documento (pode ser longo)
    
    ESTRATÉGIA PARA TEXTOS LONGOS:
    
    Problema: BERT tem limite de 512 tokens
    Solução: Dividir em chunks e fazer MÉDIA
    
    1. Se texto <= 500 tokens: embedding [CLS] direto
    2. Se texto > 500 tokens:
       a. Divide em chunks de 500 tokens
       b. Gera embedding [CLS] para cada chunk
       c. Calcula MÉDIA dos embeddings
       
    JUSTIFICATIVA DA MÉDIA:
    - Cada chunk captura parte da semântica
    - Média preserva informação de todos os chunks
    - Alternativas: max pooling, weighted average, hierarchical
    
    Args:
        texto: Documento completo (pode ser longo)
        tokenizer: Tokenizer BERT
        model: Modelo BERT
        device: 'cuda' ou 'cpu'
        
    Returns:
        numpy.array: Embedding de 768 dimensões
    """
    # Tokeniza para contar tokens
    tokens = tokenizer.tokenize(texto)
    
    # Caso 1: Texto curto - processa direto
    if len(tokens) <= CHUNK_SIZE:
        return gerar_embedding_cls(texto, tokenizer, model, device)
    
    # Caso 2: Texto longo - divide em chunks
    embeddings = []
    
    # Divide tokens em chunks
    for i in range(0, len(tokens), CHUNK_SIZE):
        chunk_tokens = tokens[i:i + CHUNK_SIZE]
        
        # Converte tokens de volta para texto
        chunk_texto = tokenizer.convert_tokens_to_string(chunk_tokens)
        
        # Gera embedding do chunk
        embedding = gerar_embedding_cls(chunk_texto, tokenizer, model, device)
        embeddings.append(embedding)
    
    # MÉDIA dos embeddings de todos os chunks
    embedding_medio = np.mean(embeddings, axis=0)
    
    return embedding_medio

def conectar_elasticsearch():
    """Conecta ao ElasticSearch"""
    es = Elasticsearch(['http://localhost:9200'])
    
    if es.ping():
        print("\n✓ Conectado ao ElasticSearch")
        info = es.info()
        print(f"  Versão: {info['version']['number']}")
    else:
        raise Exception("ElasticSearch não está rodando!")
    
    return es

def criar_indice_bertimbau(es, nome_indice='ementas_bertimbau'):
    """
    FUNÇÃO: Cria índice com suporte a dense vectors
    
    DENSE_VECTOR:
    - Campo especial do ES para vetores densos
    - Suporta busca kNN (k-Nearest Neighbors)
    - Similaridade: cosine, dot_product, l2_norm
    
    ESTRUTURA:
    - Campos text: busca léxica (BM25)
    - Campo embedding: busca semântica (BERT)
    - Permite busca HÍBRIDA (léxica + semântica)
    
    Args:
        es: Cliente ElasticSearch
        nome_indice: Nome do índice
    """
    if es.indices.exists(index=nome_indice):
        print(f"\n⚠ Índice '{nome_indice}' já existe. Removendo...")
        es.indices.delete(index=nome_indice)
    
    configuracao = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "brazilian_analyzer": {
                        "type": "standard",
                        "stopwords": "_brazilian_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer"
                },
                "highlight": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer"
                },
                "judging_organ": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer"
                },
                "type": {
                    "type": "keyword"
                },
                # === CAMPO EMBEDDING: VETOR DENSO ===
                "embedding_title": {
                    "type": "dense_vector",
                    "dims": 768,  # Dimensão do BERTimbau
                    "index": True,  # Habilita busca kNN
                    "similarity": "cosine"  # Similaridade cosseno
                },
                "embedding_highlight": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    
    es.indices.create(index=nome_indice, body=configuracao)
    print(f"\n✓ Índice '{nome_indice}' criado")
    print(f"  Dense vectors: embedding_title, embedding_highlight (768 dims)")
    print(f"  Similarity: cosine")

def ler_documentos_json(caminho_arquivo):
    """Lê documentos do JSON"""
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    documentos = dados.get('documentos', [])
    print(f"\n✓ Arquivo lido: {len(documentos)} documentos")
    
    return documentos

def indexar_com_bertimbau(es, documentos, tokenizer, model, device, nome_indice='ementas_bertimbau'):
    """
    FUNÇÃO: Indexa documentos com embeddings BERTimbau
    
    PROCESSO:
    1. Para cada documento:
       a. Gera embedding do título
       b. Gera embedding do highlight (pode ser longo)
       c. Indexa texto + embeddings
    
    DICA DE PERFORMANCE:
    - Processar em batches é mais rápido
    - GPU acelera significativamente
    - Pode demorar com muitos documentos
    
    Args:
        es: Cliente ElasticSearch
        documentos: Lista de documentos
        tokenizer, model, device: BERTimbau
        nome_indice: Nome do índice
    """
    print(f"\n📝 Gerando embeddings e indexando...")
    print(f"   Isso pode demorar alguns minutos...")
    
    acoes = []
    
    # Barra de progresso
    for doc in tqdm(documentos, desc="Processando"):
        # Gera embeddings
        title = doc.get('title', '')
        highlight = doc.get('highlight', '')
        
        # Embedding do título (geralmente curto)
        if title:
            emb_title = gerar_embedding_documento(title, tokenizer, model, device)
        else:
            emb_title = np.zeros(768)  # Vetor zero se não houver título
        
        # Embedding do highlight (pode ser longo - usa média de chunks)
        if highlight:
            emb_highlight = gerar_embedding_documento(highlight, tokenizer, model, device)
        else:
            emb_highlight = np.zeros(768)
        
        # Ação de indexação
        acao = {
            "_index": nome_indice,
            "_id": doc.get('id'),
            "_source": {
                "id": doc.get('id'),
                "title": title,
                "highlight": highlight,
                "judging_organ": doc.get('judging_organ'),
                "type": doc.get('type'),
                # Embeddings como listas (ES espera array)
                "embedding_title": emb_title.tolist(),
                "embedding_highlight": emb_highlight.tolist()
            }
        }
        acoes.append(acao)
    
    # Indexação em lote
    print(f"\n📤 Enviando para ElasticSearch...")
    sucesso, erros = bulk(es, acoes, stats_only=True)
    
    print(f"✓ Indexação concluída!")
    print(f"  Documentos indexados: {sucesso}")
    if erros:
        print(f"  ⚠ Erros: {erros}")
    
    es.indices.refresh(index=nome_indice)
    
    contagem = es.count(index=nome_indice)
    print(f"  Total no índice: {contagem['count']}")

def main():
    """Função principal"""
    print("=" * 70)
    print("INDEXAÇÃO COM BERTIMBAU E ELASTICSEARCH")
    print("=" * 70)
    print()
    print("Este script demonstra busca semântica usando embeddings do")
    print("BERTimbau (BERT em português) no ElasticSearch.")
    print()
    
    NOME_INDICE = 'ementas_bertimbau'
    CAMINHO_JSON = '../../dataSetExemplo/exEmentas.json'
    
    try:
        # 1. Carregar BERTimbau
        tokenizer, model, device = carregar_bertimbau()
        
        # 2. Conectar ES
        es = conectar_elasticsearch()
        
        # 3. Criar índice
        criar_indice_bertimbau(es, NOME_INDICE)
        
        # 4. Ler documentos
        documentos = ler_documentos_json(CAMINHO_JSON)
        
        # 5. Gerar embeddings e indexar
        indexar_com_bertimbau(es, documentos, tokenizer, model, device, NOME_INDICE)
        
        print("\n" + "=" * 70)
        print("✓ PROCESSO CONCLUÍDO!")
        print("=" * 70)
        print(f"\nÍndice '{NOME_INDICE}' pronto para buscas semânticas.")
        print(f"Execute: python buscaBertimbauElastic.py")
        print()
        print("DIFERENCIAL:")
        print("  - BM25/TF-IDF: busca léxica (keywords exatas)")
        print("  - BERTimbau: busca semântica (entende significado)")
        print("  - Exemplo: 'veículo' encontra 'carro', 'automóvel', etc.")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("\nDicas:")
        print("  - Instale: pip install transformers torch tqdm")
        print("  - ElasticSearch rodando: cd ../../BasicIRModelsWithElasticSearch/BM25 && ./initElastic.sh")
        print("  - Primeira execução baixa modelo (~400MB)")

if __name__ == "__main__":
    main()
