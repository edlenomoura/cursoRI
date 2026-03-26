#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT DE INDEXAÇÃO - VECTOR SPACE MODEL (TF-IDF) - ELASTICSEARCH 8.x+
================================================================================

Este script demonstra o TF-IDF clássico de Salton no ElasticSearch 8.x+
usando SCRIPTED SIMILARITY.

CONTEXTO:
O ElasticSearch 8.x removeu a similarity "classic" (TF-IDF tradicional).
Para fins didáticos, implementamos TF-IDF manualmente usando Painless script.

MODELO TF-IDF DE SALTON (1971):

O modelo de espaço vetorial representa documentos como vetores onde:
- Cada dimensão = um termo do vocabulário
- Peso de cada termo = TF × IDF

COMPONENTES:

1. TF (Term Frequency):
   tf = √(freq)
   - Raiz quadrada da frequência do termo no documento (poderia ser a frequencia direto)
   - Suaviza o impacto de repetições

2. IDF (Inverse Document Frequency):
   idf = log((numDocs + 1) / (docFreq + 1)) + 1 (somando 1s pra evitar contas com zeros)
   - Logaritmo do inverso da frequência em documentos
   - Termos raros têm maior peso

3. Normalização:
   norm = 1 / √(numTerms)    (norma aproximada, Não é a da fórmula completa)
   - Ajusta pelo tamanho do documento
   - Evita bias para documentos longos

4. Score Final:
   score = Σ(TF × IDF × queryNorm × fieldNorm)   (norma multiplicando porque já foi criada invertida (1/..))
   - Soma dos produtos TF-IDF para cada termo da consulta

IMPLEMENTAÇÃO NO ES 8.x+:
Usamos "scripted" similarity com script Painless que implementa
exatamente a fórmula de Salton.

================================================================================
"""

# Importações necessárias
import json
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

def conectar_elasticsearch():
    """
    FUNÇÃO: Estabelece conexão com servidor ElasticSearch
    
    Returns:
        Elasticsearch: Cliente conectado
    """
    es = Elasticsearch(['http://localhost:9200'])
    
    if es.ping():
        print("✓ Conectado ao ElasticSearch com sucesso!")
        info = es.info()
        versao = info['version']['number']
        print(f"  Versão: {versao}")
    else:
        raise Exception("Erro ao conectar. Verifique se ElasticSearch está rodando.")
    
    return es

def criar_indice_tfidf(es, nome_indice='ementas_tfidf'):
    """
    FUNÇÃO: Cria índice com TF-IDF usando SCRIPTED SIMILARITY
    
    SCRIPTED SIMILARITY (ES 7.0+):
    Permite implementar qualquer função de scoring usando Painless script.
    Aqui implementamos TF-IDF clássico de Salton.
    
    VANTAGEM DIDÁTICA:
    O código do TF-IDF fica VISÍVEL no script, mostrando exatamente
    como o score é calculado (ao contrário de BM25 que é opaco).
    
    FÓRMULAS IMPLEMENTADAS:
    
    1. TF (Term Frequency):
       tf = Math.sqrt(freq)
       - freq = frequência do termo no documento
       - Raiz quadrada suaviza impacto de repetições
    
    2. IDF (Inverse Document Frequency):
       idf = Math.log((docCount + 1.0) / (docFreq + 1.0)) + 1.0
       - docCount = total de documentos
       - docFreq = documentos que contêm o termo
       - +1 evita divisão por zero e log de zero
    
    3. Norm (Normalização):
       norm = 1.0 / Math.sqrt(length)
       - length = número de termos no campo
       - Normaliza por tamanho do documento
    
    4. Score Final:
       score = weight × norm
       weight = query.boost × sqrt(tf) × idf
    
    Args:
        es: Cliente ElasticSearch
        nome_indice: Nome do índice
    """
    # Remove índice anterior se existir
    if es.indices.exists(index=nome_indice):
        print(f"⚠ Índice '{nome_indice}' já existe. Removendo...")
        es.indices.delete(index=nome_indice)
        print(f"  Índice '{nome_indice}' removido.")
    
    # === SCRIPT PAINLESS: Implementação TF-IDF de Salton ===
    # Este script é executado para cada termo em cada documento durante a busca
    tfidf_script = """
        // Parâmetros disponíveis:
        // - weight: combinação de query.boost × idf
        // - query.boost: peso da consulta
        // - field.docCount: total de documentos
        // - field.sumDocFreq: soma de doc freqs de todos os termos
        // - field.sumTotalTermFreq: soma de term freqs de todos os termos
        // - term.docFreq: documentos que contêm o termo
        // - term.totalTermFreq: total de ocorrências do termo no índice
        // - doc.freq: frequência do termo neste documento
        // - doc.length: número de termos neste campo neste documento
        
        // TF-IDF Clássico de Salton:
        
        // 1. TF (Term Frequency) - raiz quadrada da frequência (poderia ser log ou a fre direta)
        double tf = Math.sqrt(doc.freq);
        
        // 2. IDF (Inverse Document Frequency)
        double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0; //(somando 1s pra evitar contas com zeros)
        
        // 3. Normalização por comprimento do documento
        double norm = 1.0 / Math.sqrt(doc.length);  // (norma não é a da fórmula do vetorial. Apenas uma aproximação simples. NOte que já está invertida)
        
        // 4. Score final: TF × IDF × norm × query.boost
        return query.boost * tf * idf * norm;
    """
    
    # Configuração do índice
    configuracao_indice = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            
            # Analyzer para português
            "analysis": {
                "analyzer": {
                    "brazilian_analyzer": {
                        "type": "standard",
                        "stopwords": "_brazilian_"
                    }
                }
            },
            
            # === SIMILARITY CUSTOMIZADA: TF-IDF via Script ===
            "similarity": {
                "tfidf_salton": {
                    # TYPE "scripted": permite código Painless customizado
                    "type": "scripted",
                    
                    # SCRIPT: implementação TF-IDF de Salton
                    "script": {
                        "source": tfidf_script
                    }
                }
            }
        },
        
        # === MAPPINGS: Campo usa nossa similarity customizada ===
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer",
                    # Aplica TF-IDF de Salton
                    "similarity": "tfidf_salton",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                # CAMPO PRINCIPAL: usa TF-IDF de Salton
                "highlight": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer",
                    # Este campo usará nosso script TF-IDF
                    "similarity": "tfidf_salton"
                },
                "judging_organ": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer",
                    "similarity": "tfidf_salton",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "type": {
                    "type": "keyword"
                }
            }
        }
    }
    
    # Cria o índice
    es.indices.create(index=nome_indice, body=configuracao_indice)
    print(f"✓ Índice '{nome_indice}' criado com sucesso!")
    print(f"  Campos: id, title, highlight, judging_organ, type")
    print(f"  Analyzer: brazilian_analyzer")
    print(f"  Similarity: TF-IDF de Salton (scripted) ⬅️ IMPLEMENTADO VIA PAINLESS!")
    print(f"  Campos: id, title, highlight, judging_organ, type")
    print(f"  Analyzer: brazilian_analyzer")
    print(f"  Similarity: TF-IDF (classic) ⬅️ DIFERENTE DO BM25!")

def ler_documentos_json(caminho_arquivo):
    """
    FUNÇÃO: Lê documentos de um arquivo JSON
    
    Args:
        caminho_arquivo: Caminho para o arquivo JSON
        
    Returns:
        list: Lista de documentos
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    documentos = dados.get('documentos', [])
    print(f"✓ Arquivo lido com sucesso!")
    print(f"  Total de documentos: {len(documentos)}")
    
    return documentos

def gerar_acoes_bulk(documentos, nome_indice='ementas_tfidf'):
    """
    FUNÇÃO GERADORA: Cria ações para indexação em lote
    
    Args:
        documentos: Lista de documentos
        nome_indice: Nome do índice
        
    Yields:
        dict: Ação de indexação
    """
    for doc in documentos:
        yield {
            "_index": nome_indice,
            "_id": doc.get('id'),
            "_source": {
                "id": doc.get('id'),
                "title": doc.get('title'),
                "highlight": doc.get('highlight'),
                "judging_organ": doc.get('judging_organ'),
                "type": doc.get('type')
            }
        }

def indexar_documentos(es, documentos, nome_indice='ementas_tfidf'):
    """
    FUNÇÃO: Indexa documentos usando Bulk API
    
    Args:
        es: Cliente ElasticSearch
        documentos: Lista de documentos
        nome_indice: Nome do índice
    """
    print(f"\n📝 Indexando documentos...")
    
    sucesso, erros = bulk(es, gerar_acoes_bulk(documentos, nome_indice), stats_only=True)
    
    print(f"✓ Indexação concluída!")
    print(f"  Documentos indexados: {sucesso}")
    
    if erros:
        print(f"  ⚠ Erros: {erros}")
    
    # Refresh para buscas imediatas
    es.indices.refresh(index=nome_indice)
    
    contagem = es.count(index=nome_indice)
    print(f"  Total no índice: {contagem['count']} documentos")

def main():
    """
    FUNÇÃO PRINCIPAL: Cria índice TF-IDF e indexa documentos
    
    SCRIPTED SIMILARITY:
    Este script usa "scripted" similarity para implementar TF-IDF de Salton
    via código Painless, permitindo rodar no ElasticSearch 8.x+.
    
    VANTAGEM DIDÁTICA:
    O código TF-IDF é VISÍVEL e EXPLICADO no script Painless, tornando
    claro exatamente como o score é calculado (diferente do BM25 opaco).
    """
    print("=" * 60)
    print("INDEXAÇÃO - VECTOR SPACE MODEL (TF-IDF DE SALTON)")
    print("=" * 60)
    print()
    print("Este script cria um índice usando TF-IDF de Salton (1971)")
    print("implementado via scripted similarity no ElasticSearch 8.x+")
    print()
    
    # Configurações
    NOME_INDICE = 'ementas_tfidf'
    CAMINHO_JSON = '../../dataSetExemplo/exEmentas.json'
    
    try:
        # Passo 1: Conectar
        print("1. Conectando ao ElasticSearch...")
        es = conectar_elasticsearch()
        print()
        
        # Passo 2: Criar índice com TF-IDF via script
        print("2. Criando índice com TF-IDF (scripted similarity)...")
        criar_indice_tfidf(es, NOME_INDICE)
        print()
        
        # Passo 3: Ler documentos
        print("3. Lendo documentos do arquivo JSON...")
        documentos = ler_documentos_json(CAMINHO_JSON)
        print()
        
        # Passo 4: Indexar
        print("4. Indexando documentos...")
        indexar_documentos(es, documentos, NOME_INDICE)
        print()
        
        print("=" * 60)
        print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"\nÍndice '{NOME_INDICE}' disponível para consultas.")
        print(f"Acesse: http://localhost:9200/{NOME_INDICE}/_search")
        print()
        print("COMPARAÇÃO COM BM25:")
        print(f"  - Índice TF-IDF: {NOME_INDICE} (scripted similarity)")
        print(f"  - Índice BM25: ementas (similarity padrão)")
        print()
        print("FÓRMULA do VSM (TF-IDF) IMPLEMENTADA:")
        print("VERSÕES ATUAIS DO ELASTIC NÃO IMPLEMENTAM MAIS VSM. AQUI APENAS PARA DAR UMA IDEIA DE COMO SERIA. FIZ VÁRIAS SIMPLIFICAÇOES, NÃO É O VSM CORRETAMENTE IMPLEMENTADO:")
        print("  tf = √(freq) (poderia ser só freq, ou log(1+freq). Experimente mudar)")
        print("  idf = log((docCount + 1) / (docFreq + 1)) + 1 (os 1s pra evitar contas com zeros)")
        print("  norm = 1 / √(length) (norma aproximada, não é a da fórmula completa)")
        print("  score = query.boost × tf × idf × norm (norma multiplicando porque já foi criada invertida)")
        print()
        print("Próximos passos:")
        print("  - Execute 'python buscaVSM.py' para ver buscas com TF-IDF")
        print("  - Compare resultados com '../BM25/busca.py' (BM25)")
        print("  - Observe diferenças nos scores e ranking")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("\nDicas:")
        print("  - Verifique se ElasticSearch está rodando (../BM25/initElastic.sh)")
        print("  - Verifique o caminho do arquivo JSON")
        print("  - Script similarity requer ES 7.0+")

# Ponto de entrada do script
if __name__ == "__main__":
    main()
