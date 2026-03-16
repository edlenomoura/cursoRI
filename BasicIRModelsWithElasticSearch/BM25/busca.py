#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT DE EXEMPLOS DE BUSCA NO ELASTICSEARCH
================================================================================

Este script demonstra diferentes tipos de consultas (queries) no ElasticSearch.
É um guia didático para alunos aprenderem a construir buscas efetivas.

TIPOS DE BUSCA DEMONSTRADOS:
1. Busca Simples (match): busca textual básica em um campo
2. Busca Multi-campo (multi_match): busca em vários campos com pesos
3. Busca Booleana (bool): combina múltiplas condições (AND, OR)  
4. Busca com Filtro: restringe resultados por critérios exatos
5. Busca por Frase (match_phrase): encontra frase exata

ALGORITMO BM25:
O ElasticSearch usa BM25 (Best Matching 25) para calcular relevância.
BM25 considera:
- TF (Term Frequency): frequência do termo no documento
- IDF (Inverse Document Frequency): raridade do termo no corpus
- Document Length: normalização pelo tamanho do documento

Score mais alto = documento mais relevante para a consulta

================================================================================
"""

from elasticsearch import Elasticsearch
import json

def conectar_elasticsearch():
    """
    FUNÇÃO: Conecta ao servidor ElasticSearch local
    
    Returns:
        Elasticsearch: Cliente conectado
        
    Raises:
        Exception: Se não conseguir conectar
    """
    # Cria cliente apontando para localhost:9200
    es = Elasticsearch(['http://localhost:9200'])
    
    # Verifica conectividade com ping
    if not es.ping():
        raise Exception("ElasticSearch não está rodando! Execute ./initElastic.sh")
    
    return es

def busca_simples(es, consulta, tamanho=10):
    """
    TIPO 1: BUSCA SIMPLES (Match Query)
    
    A consulta MATCH é o tipo mais básico e comum de busca textual.
    
    COMO FUNCIONA:
    1. A consulta é analisada (tokenizada, lowercase, stopwords removidas)
    2. Os tokens são buscados no campo especificado
    3. Documentos que contêm qualquer um dos tokens são retornados
    4. Score (relevância) é calculado usando BM25
    
    EXEMPLO:
    Consulta: "responsabilidade civil danos morais"
    Tokens: [responsabilidade, civil, danos, morais]
    Retorna: documentos que contêm qualquer um desses termos
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da consulta (string)
        tamanho: Número máximo de resultados (default: 10)
    """
    print(f"\n{'='*80}")
    print(f"BUSCA SIMPLES: '{consulta}'")
    print(f"Tipo: Match Query | Campo: highlight")
    print('='*80)
    
    # Executa a busca no ElasticSearch
    resposta = es.search(
        index='ementas',  # Índice onde buscar
        body={
            'query': {  # Definição da consulta
                'match': {  # Tipo: match (busca textual)
                    'highlight': consulta  # Campo: highlight, valor: consulta
                    # MATCH usa OR por padrão: busca docs com qualquer termo
                }
            },
            'size': tamanho  # Limita número de resultados
        }
    )
    
    exibir_resultados(resposta)

def busca_multi_campo(es, consulta, tamanho=10):
    """
    TIPO 2: BUSCA MULTI-CAMPO (Multi-Match Query)
    
    Busca o mesmo texto em múltiplos campos simultaneamente.
    Útil quando não sabemos em qual campo o termo pode aparecer.
    
    COMO FUNCIONA:
    1. Busca a consulta em todos os campos listados
    2. Aplica BOOST (peso) diferente para cada campo
    3. Combina os scores de todos os campos
    
    BOOST (^):
    - title^2: peso 2x (títulos são mais importantes)
    - highlight: peso 1x (padrão)
    - judging_organ: peso 1x
    
    TYPE 'best_fields':
    - Usa o score do MELHOR campo que teve match
    - Outras opções: 'most_fields' (soma scores), 'cross_fields', 'phrase'
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da consulta
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA MULTI-CAMPO: '{consulta}'")
    print(f"Campos: title (peso 2x), highlight, judging_organ")
    print('='*80)
    
    resposta = es.search(
        index='ementas',
        body={
            'query': {
                'multi_match': {  # Tipo: multi_match (busca em vários campos)
                    'query': consulta,
                    
                    # Lista de campos com pesos (boost)
                    # ^2 significa que matches no title contam 2x mais
                    'fields': ['title^2', 'highlight', 'judging_organ'],
                    
                    # Estratégia de combinação de scores
                    'type': 'best_fields'  # Usa score do melhor campo
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_booleana(es, termos_obrigatorios, termos_opcionais=None, tamanho=10):
    """
    TIPO 3: BUSCA BOOLEANA (Bool Query)
    
    Combina múltiplas condições usando lógica booleana (AND, OR, NOT).
    É a forma mais flexível e poderosa de construir consultas.
    
    CLÁUSULAS BOOLEANAS:
    - MUST: condições OBRIGATÓRIAS (AND)
      * Documento DEVE satisfazer todas as condições must
      * Afeta o score (relevância)
    
    - SHOULD: condições OPCIONAIS (OR)
      * Documento PODE satisfazer (quanto mais, melhor o score)
      * Aumenta relevância mas não é obrigatório
    
    - MUST_NOT: condições de EXCLUSÃO (NOT)
      * Documento NÃO DEVE satisfazer
      * Não afeta score (apenas filtra)
    
    - FILTER: filtros exatos
      * Documento DEVE satisfazer
      * Não afeta score (busca exata, mais rápida, cacheada)
    
    EXEMPLO:
    must=["civil", "danos"] E should=["morais", "materiais"]
    = Documentos que TEM "civil" E "danos", preferencialmente com "morais" ou "materiais"
    
    Args:
        es: Cliente ElasticSearch
        termos_obrigatorios: Lista de termos que DEVEM aparecer (AND)
        termos_opcionais: Lista de termos que PODEM aparecer (aumentam score)
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA BOOLEANA")
    print(f"MUST (obrigatórios): {termos_obrigatorios}")
    print(f"SHOULD (opcionais): {termos_opcionais}")
    print('='*80)
    
    # Constrói cláusulas MUST: uma match query para cada termo obrigatório
    # List comprehension: cria uma lista de dicionários
    must_clauses = [{'match': {'highlight': termo}} for termo in termos_obrigatorios]
    
    # Constrói cláusulas SHOULD: uma match query para cada termo opcional
    should_clauses = [{'match': {'highlight': termo}} for termo in (termos_opcionais or [])]
    
    resposta = es.search(
        index='ementas',
        body={
            'query': {
                'bool': {  # Tipo: bool (consulta booleana)
                    # MUST: todas essas condições devem ser verdadeiras
                    'must': must_clauses,
                    
                    # SHOULD: pelo menos uma aumenta o score (mas não é obrigatória)
                    'should': should_clauses
                    
                    # Outras opções não usadas aqui:
                    # 'must_not': [...],  # Excluir documentos
                    # 'filter': [...],     # Filtros exatos (sem score)
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_com_filtro(es, consulta, tipo_documento=None, tamanho=10):
    """
    TIPO 4: BUSCA COM FILTRO
    
    Combina busca textual (com score) + filtros exatos (sem score).
    
    DIFERENÇA: QUERY vs FILTER
    
    QUERY (must):
    - Calcula relevância (score)
    - Mais lento
    - Use para busca textual
    
    FILTER:
    - NãO calcula score (sim/não)
    - Mais rápido (pode ser cacheado)
    - Use para filtros exatos: datas, números, keywords
    
    TERM Query:
    - Busca valor EXATO (não analisado)
    - Use em campos 'keyword'
    - Case-sensitive, sem tokenização
    
    EXEMPLO:
    Busca textual por "sentença" + filtro exato type="ACORDAO"
    = Busca documentos sobre "sentença" que sejam do tipo ACORDAO
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da busca (com score)
        tipo_documento: Tipo exato para filtrar (sem score)
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA COM FILTRO: '{consulta}'")
    print(f"FILTRO: type = {tipo_documento}")
    print('='*80)
    
    # Constrói a query booleana
    query = {
        'bool': {
            # MUST: busca textual (calcula score)
            'must': [
                {'match': {'highlight': consulta}}
            ]
        }
    }
    
    # Adiciona filtro se especificado
    if tipo_documento:
        # FILTER: filtro exato (não calcula score, mais rápido)
        query['bool']['filter'] = [
            # TERM: busca valor exato (não analisado)
            # Use em campos 'keyword'
            {'term': {'type': tipo_documento}}
        ]
    
    resposta = es.search(
        index='ementas',
        body={
            'query': query,
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_phrase(es, frase, tamanho=10):
    """
    TIPO 5: BUSCA POR FRASE EXATA (Match Phrase Query)
    
    Busca a frase EXATA, mantendo a ordem e proximidade das palavras.
    
    DIFERENÇA: MATCH vs MATCH_PHRASE
    
    MATCH:
    - Busca termos individualmente
    - Ordem não importa
    - "nexo causalidade" encontra "causalidade do nexo"
    
    MATCH_PHRASE:
    - Busca frase exata
    - Ordem importa
    - "nexo de causalidade" encontra apenas essa ordem
    - Pode ter pequena tolerância (slop) para palavras entre termos
    
    USO:
    - Nomes próprios: "João da Silva"
    - Expressões técnicas: "nexo de causalidade"
    - Citações: "trecho exato do texto"
    
    Args:
        es: Cliente ElasticSearch
        frase: Frase exata a buscar
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA POR FRASE EXATA: '{frase}'")
    print(f"Tipo: Match Phrase (ordem importa)")
    print('='*80)
    
    resposta = es.search(
        index='ementas',
        body={
            'query': {
                # MATCH_PHRASE: busca a frase na ordem exata
                'match_phrase': {
                    'highlight': frase
                    # Opção adicional não usada aqui:
                    # 'slop': 2  # Permite até 2 palavras entre os termos
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def exibir_resultados(resposta):
    """
    FUNÇÃO: Exibe resultados da busca de forma formatada
    
    ESTRUTURA DA RESPOSTA:
    resposta = {
        'took': tempo_em_ms,  # Tempo de execução
        'hits': {
            'total': {'value': total_encontrado},  # Total de documentos
            'max_score': maior_score,  # Maior relevância
            'hits': [  # Lista de documentos encontrados
                {
                    '_score': relevância,  # Score BM25 (quanto maior, mais relevante)
                    '_source': {...}  # Documento completo
                }
            ]
        }
    }
    
    SCORE (Relevância):
    - Calculado pelo algoritmo BM25
    - Não tem valor máximo fixo
    - Valores maiores = mais relevante
    - Usado para ordenar resultados
    
    Args:
        resposta: Objeto de resposta do ElasticSearch
    """
    # Extrai informações principais da resposta
    hits = resposta['hits']  # Container dos resultados
    total = hits['total']['value']  # Total de documentos encontrados
    tempo = resposta['took']  # Tempo de execução em milissegundos
    
    print(f"\nTotal de resultados: {total} | Tempo: {tempo}ms")
    print()
    
    # Verifica se encontrou algum resultado
    if total == 0:
        print("Nenhum resultado encontrado.")
        print("Dicas:")
        print("  - Tente termos mais genéricos")
        print("  - Verifique erros de digitação")
        print("  - Em match_phrase, tente match simples")
        return
    
    # Itera sobre os documentos retornados
    # enumerate adiciona contador começando em 1
    for i, hit in enumerate(hits['hits'], 1):
        # SCORE: relevância calculada pelo BM25
        # Quanto maior, mais relevante o documento para a consulta
        score = hit['_score']
        
        # _source: documento original (todos os campos)
        doc = hit['_source']
        
        # Exibe informações do documento
        print(f"{i}. Score: {score:.4f}")  # Score com 4 casas decimais
        print(f"   ID: {doc['id']}")
        print(f"   Título: {doc['title']}")
        print(f"   Órgão: {doc.get('judging_organ', 'N/A')}")  # get() retorna 'N/A' se não existir
        print(f"   Tipo: {doc.get('type', 'N/A')}")
        
        # Exibe trecho do texto (limitado a 200 caracteres para legibilidade)
        highlight_text = doc.get('highlight', '')
        if len(highlight_text) > 200:
            highlight_text = highlight_text[:200] + '...'  # Trunca e adiciona reticências
        print(f"   Texto: {highlight_text}")
        print()  # Linha em branco entre resultados

def estatisticas_indice(es):
    """
    FUNÇÃO: Exibe estatísticas e informações sobre o índice
    
    Demonstra dois conceitos importantes:
    1. COUNT: Contar documentos no índice
    2. AGGREGATIONS: Agrupamentos e estatísticas
    
    AGGREGAÇÕES (Aggregations):
    - Similar a GROUP BY em SQL
    - Permite análises estatísticas dos dados
    - Tipos: terms, stats, date_histogram, etc.
    
    TERMS AGGREGATION:
    - Agrupa por valores únicos de um campo
    - Conta documentos em cada grupo
    - Útil para facetas, filtros, dashboards
    """
    print(f"\n{'='*80}")
    print("ESTATÍSTICAS DO ÍNDICE")
    print('='*80)
    
    # COUNT: Conta total de documentos no índice
    contagem = es.count(index='ementas')
    print(f"Total de documentos: {contagem['count']}")
    
    # AGGREGAÇÃO: Conta documentos por tipo
    resposta = es.search(
        index='ementas',
        body={
            'size': 0,  # Não retorna documentos (só queremos as agregações)
            'aggs': {  # Define agregações
                'tipos': {  # Nome da agregação (pode ser qualquer nome)
                    'terms': {  # Tipo: terms (agrupa por valores únicos)
                        'field': 'type',  # Campo a agrupar (deve ser keyword)
                        'size': 10  # Máximo de grupos a retornar
                    }
                }
            }
        }
    )
    
    print("\nDocumentos por tipo:")
    # Itera sobre os buckets (grupos) da agregação
    for bucket in resposta['aggregations']['tipos']['buckets']:
        # Cada bucket tem 'key' (valor do campo) e 'doc_count' (contagem)
        print(f"  {bucket['key']}: {bucket['doc_count']}")

def main():
    """
    FUNÇÃO PRINCIPAL: Demonstra diferentes tipos de buscas
    
    Este script executa uma série de exemplos didáticos mostrando:
    1. Busca simples (match)
    2. Busca multi-campo (multi_match com boost)
    3. Busca booleana (bool com must/should)
    4. Busca com filtro (bool + filter)
    5. Busca por frase (match_phrase)
    
    PARA ESTUDAR:
    - Execute este script: python busca.py
    - Analise os scores retornados
    - Modifique as consultas de exemplo
    - Experimente criar suas próprias buscas
    """
    print("="*80)
    print("EXEMPLOS DE BUSCA COM BM25 - GUIA DIDÁTICO")
    print("="*80)
    print()
    print("Este script demonstra 5 tipos principais de consulta no ElasticSearch.")
    print("Observe os scores (relevância) e como diferentes consultas afetam os resultados.")
    print()
    
    try:
        # Conecta ao ElasticSearch
        es = conectar_elasticsearch()
        print("✓ Conectado ao ElasticSearch")
        
        # Verifica se o índice existe
        if not es.indices.exists(index='ementas'):
            print("\n❌ Índice 'ementas' não encontrado!")
            print("Execute primeiro: python indexa.py")
            return
        
        # === ESTATÍSTICAS ===
        # Mostra informações gerais sobre o índice
        estatisticas_indice(es)
        
        # === EXEMPLO 1: BUSCA SIMPLES ===
        # Busca textual básica em um campo
        busca_simples(es, "responsabilidade civil danos morais", tamanho=5)
        
        # === EXEMPLO 2: BUSCA MULTI-CAMPO ===
        # Busca em vários campos com pesos diferentes
        busca_multi_campo(es, "apelação", tamanho=5)
        
        # === EXEMPLO 3: BUSCA BOOLEANA ===
        # Combina termos obrigatórios (AND) e opcionais (OR)
        busca_booleana(es, 
                      termos_obrigatorios=["civil", "danos"],  # DEVE ter ambos
                      termos_opcionais=["morais", "materiais"],  # Bom ter (aumenta score)
                      tamanho=5)
        
        # === EXEMPLO 4: BUSCA COM FILTRO ===
        # Busca textual + filtro exato por tipo
        busca_com_filtro(es, "sentença", tipo_documento="ACORDAO", tamanho=5)
        
        # === EXEMPLO 5: BUSCA POR FRASE ===
        # Busca frase exata (ordem das palavras importa)
        busca_phrase(es, "nexo de causalidade", tamanho=5)
        
        # === CONCLUSÃO ===
        print("\n" + "="*80)
        print("✓ EXEMPLOS CONCLUÍDOS!")
        print("="*80)
        print("\nPRÓXIMOS PASSOS:")
        print("  1. Modifique as consultas acima e observe as diferenças nos resultados")
        print("  2. Experimente criar novas buscas combinando os tipos aprendidos")
        print("  3. Analise os scores: por que alguns documentos são mais relevantes?")
        print("  4. Teste com suas próprias consultas relacionadas aos seus dados")
        print()
        print("RECURSOS ÚTEIS:")
        print("  - Documentação oficial: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html")
        print("  - BM25: https://en.wikipedia.org/wiki/Okapi_BM25")
        
    except Exception as e:
        # Captura e exibe erros
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("\nVerifique:")
        print("  - ElasticSearch está rodando? (./initElastic.sh)")
        print("  - Índice foi criado? (python indexa.py)")

if __name__ == "__main__":
    main()
