#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT DE INDEXAÇÃO DE EMENTAS NO ELASTICSEARCH
================================================================================

Este script foi criado para fins educacionais e demonstra como:
1. Conectar-se a um servidor ElasticSearch
2. Criar um índice com configurações apropriadas
3. Definir mapeamentos de campos (schema dos documentos)
4. Ler documentos de um arquivo JSON
5. Indexar documentos em lote (bulk indexing)

CONCEITOS IMPORTANTES:
- ElasticSearch: Sistema de busca e análise distribuído baseado em Apache Lucene
- Índice: Coleção de documentos com características similares (como uma "tabela" em BD)
- Documento: Unidade básica de informação que pode ser indexada (como uma "linha")
- Mapeamento: Define como os documentos e seus campos são armazenados e indexados
- Analyzer: Processa o texto (tokenização, remoção de stopwords, stemming, etc.)
- BM25: Algoritmo de ranking usado por padrão pelo ElasticSearch (Best Matching 25)

================================================================================
"""

# Importações necessárias
import json  # Para ler e processar arquivos JSON
import os    # Para operações com sistema de arquivos
from elasticsearch import Elasticsearch  # Cliente oficial do ElasticSearch para Python
from elasticsearch.helpers import bulk   # Função helper para indexação em lote (mais eficiente)

def conectar_elasticsearch():
    """
    FUNÇÃO: Estabelece conexão com o servidor ElasticSearch local
    
    O ElasticSearch é acessado via HTTP REST API na porta padrão 9200.
    Esta função cria um cliente que será usado para todas as operações.
    
    Returns:
        Elasticsearch: Objeto cliente configurado e conectado
    
    Raises:
        Exception: Se não conseguir conectar ao servidor
    """
    # Cria o cliente ElasticSearch apontando para servidor local
    # Lista de URLs permite configurar múltiplos nós (nodes) em um cluster
    es = Elasticsearch(['http://localhost:9200'])
    
    # PING: Verifica se o servidor está respondendo
    # Retorna True se conseguir conectar, False caso contrário
    if es.ping():
        print("✓ Conectado ao ElasticSearch com sucesso!")
        
        # Obtém informações sobre o cluster (versão, nome, etc.)
        info = es.info()
        print(f"  Versão: {info['version']['number']}")
    else:
        # Se não conseguir conectar, lança exceção
        # Possíveis causas: ElasticSearch não está rodando, porta errada, firewall
        raise Exception("Erro ao conectar ao ElasticSearch. Verifique se o servidor está rodando.")
    
    return es

def criar_indice(es, nome_indice='ementas'):
    """
    FUNÇÃO: Cria o índice ElasticSearch com configurações e mapeamentos
    
    Um ÍNDICE no ElasticSearch é similar a uma "tabela" em bancos relacionais.
    Ele armazena documentos com estrutura similar e define como indexá-los.
    
    Args:
        es: Cliente ElasticSearch conectado
        nome_indice: Nome do índice a ser criado (padrão: 'ementas')
    
    IMPORTANTE:
    - Mapeamento define o tipo de cada campo (text, keyword, date, etc.)
    - Analyzer define como o texto será processado para busca
    - Settings definem configurações do índice (shards, replicas, analyzers)
    """
    # PASSO 1: Remove índice anterior se já existir
    # Isso garante que começamos com configuração limpa
    if es.indices.exists(index=nome_indice):
        print(f"⚠ Índice '{nome_indice}' já existe. Removendo...")
        es.indices.delete(index=nome_indice)
        print(f"  Índice '{nome_indice}' removido.")
    
    # PASSO 2: Define a configuração completa do índice
    configuracao_indice = {
        # === SETTINGS: Configurações gerais do índice ===
        "settings": {
            # SHARDS: Divisões do índice para distribuição e paralelização
            # 1 shard é suficiente para desenvolvimento e datasets pequenos
            "number_of_shards": 1,
            
            # REPLICAS: Cópias dos shards para alta disponibilidade
            # 0 réplicas é OK para desenvolvimento (não há redundância)
            "number_of_replicas": 0,
            
            # ANALYSIS: Define como o texto será processado
            "analysis": {
                # Criamos um analyzer customizado para português brasileiro
                "analyzer": {
                    "brazilian_analyzer": {
                        # Tipo standard: tokeniza por espaços e pontuação, lowercase
                        "type": "standard",
                        
                        # Stopwords: palavras comuns que podem ser ignoradas (o, a, de, para, etc.)
                        # "_brazilian_" usa lista pré-definida de stopwords em português
                        "stopwords": "_brazilian_"
                    }
                }
            }
        },
        # === MAPPINGS: Define o schema dos documentos ===
        "mappings": {
            "properties": {
                # Campo ID: identificador único do documento
                "id": {
                    # KEYWORD: armazenado exato, não analisado (não tokenizado)
                    # Usado para filtros exatos, agregações, ordenação
                    "type": "keyword"
                },
                
                # Campo TITLE: título da ementa/processo
                "title": {
                    # TEXT: campo analisado, tokenizado, para busca textual
                    "type": "text",
                    
                    # Usa nosso analyzer com stopwords em português
                    "analyzer": "brazilian_analyzer",
                    
                    # MULTI-FIELD: também armazena como keyword para ordenação/agregação
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # Versão não analisada do mesmo campo
                        }
                    }
                },
                
                # Campo HIGHLIGHT: texto completo da ementa (principal campo de busca)
                "highlight": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer"
                },
                
                # Campo JUDGING_ORGAN: órgão julgador (Câmara, Turma, etc.)
                "judging_organ": {
                    "type": "text",
                    "analyzer": "brazilian_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # Para filtros exatos
                        }
                    }
                },
                
                # Campo TYPE: tipo do documento (ACORDAO, SENTENÇA, etc.)
                "type": {
                    # KEYWORD porque tem valores fixos e limitados
                    "type": "keyword"
                }
            }
        }
    }
    
    # PASSO 3: Cria o índice no ElasticSearch com as configurações definidas
    # O método create envia uma requisição PUT para o ElasticSearch
    es.indices.create(index=nome_indice, body=configuracao_indice)
    
    print(f"✓ Índice '{nome_indice}' criado com sucesso!")
    print(f"  Campos: id, title, highlight, judging_organ, type")
    print(f"  Analyzer: brazilian_analyzer (com stopwords em português)")

def ler_documentos_json(caminho_arquivo):
    """
    FUNÇÃO: Lê documentos de um arquivo JSON
    
    O arquivo deve ter a estrutura:
    {
        "documentos": [
            {"id": "...", "title": "...", "highlight": "...", ...},
            ...
        ]
    }
    
    Args:
        caminho_arquivo: Caminho absoluto ou relativo para o arquivo JSON
        
    Returns:
        list: Lista de dicionários, cada um representando um documento
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    # Verifica se o arquivo existe antes de tentar abrir
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    # Abre e lê o arquivo JSON
    # 'r' = modo leitura, encoding='utf-8' para suportar acentuação
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        # json.load() converte o JSON em estruturas Python (dict, list)
        dados = json.load(f)
    
    # Extrai a lista de documentos do JSON
    # Se não existir a chave 'documentos', retorna lista vazia
    documentos = dados.get('documentos', [])
    
    print(f"✓ Arquivo lido com sucesso!")
    print(f"  Total de documentos: {len(documentos)}")
    
    return documentos

def gerar_acoes_bulk(documentos, nome_indice='ementas'):
    """
    FUNÇÃO GERADORA: Cria ações para indexação em lote (bulk)
    
    BULK API: Método mais eficiente para indexar múltiplos documentos.
    Em vez de enviar uma requisição HTTP por documento (lento),
    envia todos em uma única requisição (rápido).
    
    Esta é uma FUNÇÃO GERADORA (usa yield) que:
    - Não carrega todos os documentos na memória de uma vez
    - Gera um documento por vez conforme necessário (memory-efficient)
    
    Args:
        documentos: Lista de dicionários com os documentos originais
        nome_indice: Nome do índice onde indexar
        
    Yields:
        dict: Estrutura de ação para a Bulk API com _index, _id e _source
    """
    # Itera sobre cada documento da lista
    for doc in documentos:
        # YIELD: retorna um dict por vez (não cria lista completa na memória)
        yield {
            # _index: nome do índice destino
            "_index": nome_indice,
            
            # _id: identificador único do documento
            # Se não fornecido, ElasticSearch gera um ID aleatório
            "_id": doc.get('id'),
            
            # _source: conteúdo completo do documento que será armazenado
            # Este é o documento que será retornado nas buscas
            "_source": {
                "id": doc.get('id'),
                "title": doc.get('title'),
                "highlight": doc.get('highlight'),
                "judging_organ": doc.get('judging_organ'),
                "type": doc.get('type')
            }
        }

def indexar_documentos(es, documentos, nome_indice='ementas'):
    """
    FUNÇÃO: Indexa documentos no ElasticSearch usando Bulk API
    
    INDEXAÇÃO: Processo de adicionar documentos ao índice.
    Durante a indexação, o ElasticSearch:
    1. Analisa o texto usando o analyzer configurado
    2. Cria estruturas de dados invertidas para busca rápida
    3. Armazena o documento original (_source)
    
    BULK API: Indexa múltiplos documentos em uma só requisição.
    É MUITO mais eficiente que indexar um por um.
    
    Args:
        es: Cliente ElasticSearch
        documentos: Lista de documentos a indexar
        nome_indice: Nome do índice destino
    """
    print(f"\n📝 Indexando documentos...")
    
    # bulk(): Função helper que gerencia a indexação em lote
    # - Envia documentos em batches (padrão: 500 por vez)
    # - Trata erros automaticamente
    # - stats_only=True: retorna apenas estatísticas (não detalhes de cada doc)
    sucesso, erros = bulk(es, gerar_acoes_bulk(documentos, nome_indice), stats_only=True)
    
    print(f"✓ Indexação concluída!")
    print(f"  Documentos indexados: {sucesso}")
    
    if erros:
        print(f"  ⚠ Erros: {erros}")
    
    # REFRESH: Força o índice a atualizar para buscas imediatas
    # Por padrão, ElasticSearch atualiza a cada 1 segundo
    # Refresh garante que documentos fiquem visíveis imediatamente
    es.indices.refresh(index=nome_indice)
    
    # COUNT: Verifica quantos documentos existem no índice
    # Útil para confirmar que tudo foi indexado corretamente
    contagem = es.count(index=nome_indice)
    print(f"  Total no índice: {contagem['count']} documentos")

def main():
    """
    FUNÇÃO PRINCIPAL: Orquestra todo o processo de indexação
    
    FLUXO DE EXECUÇÃO:
    1. Conecta ao ElasticSearch
    2. Cria o índice com configurações e mapeamentos
    3. Lê documentos do arquivo JSON
    4. Indexa todos os documentos usando Bulk API
    5. Exibe estatísticas e informações
    """
    print("=" * 60)
    print("INDEXAÇÃO DE EMENTAS NO ELASTICSEARCH")
    print("=" * 60)
    print()
    
    # === CONFIGURAÇÕES ===
    # Defina aqui os parâmetros que podem mudar
    NOME_INDICE = 'ementas'  # Nome do índice a ser criado
    CAMINHO_JSON = '../../dataSetExemplo/exEmentas.json'  # Caminho do arquivo de dados
    
    try:
        # === PASSO 1: CONECTAR ===
        print("1. Conectando ao ElasticSearch...")
        es = conectar_elasticsearch()
        print()
        
        # === PASSO 2: CRIAR ÍNDICE ===
        print("2. Criando índice...")
        criar_indice(es, NOME_INDICE)
        print()
        
        # === PASSO 3: LER DADOS ===
        print("3. Lendo documentos do arquivo JSON...")
        documentos = ler_documentos_json(CAMINHO_JSON)
        print()
        
        # === PASSO 4: INDEXAR ===
        print("4. Indexando documentos...")
        indexar_documentos(es, documentos, NOME_INDICE)
        print()
        
        # === SUCESSO ===
        print("=" * 60)
        print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"\nÍndice '{NOME_INDICE}' disponível para consultas.")
        print(f"Acesse: http://localhost:9200/{NOME_INDICE}/_search")
        print("\nPróximos passos:")
        print("  - Execute 'python busca.py' para ver exemplos de buscas")
        print(f"  - Acesse http://localhost:9200/{NOME_INDICE}/_count para ver total de docs")
        
    except Exception as e:
        # Captura qualquer erro que ocorra durante a execução
        print(f"\n❌ ERRO: {e}")
        # Exibe o traceback completo para debugging
        import traceback
        traceback.print_exc()
        print("\nDicas para resolver:")
        print("  - Verifique se o ElasticSearch está rodando (./initElastic.sh)")
        print("  - Verifique o caminho do arquivo JSON")
        print("  - Verifique a conexão de rede na porta 9200")

# Ponto de entrada do script
# __name__ == "__main__" é True quando executado diretamente (python indexa.py)
# É False quando importado como módulo (import indexa)
if __name__ == "__main__":
    main()
