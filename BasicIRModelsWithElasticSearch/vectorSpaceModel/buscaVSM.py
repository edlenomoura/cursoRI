#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT DE BUSCAS - VECTOR SPACE MODEL (TF-IDF DE SALTON)
================================================================================

Este script demonstra buscas usando TF-IDF (Term Frequency - Inverse Document
Frequency) de Salton implementado via SCRIPTED SIMILARITY no ES 8.x+.

TF-IDF - MODELO DE ESPAÇO VETORIAL (SALTON, 1971):

CONCEITO:
Documentos e consultas são representados como vetores em um espaço 
multidimensional. A similaridade é medida pela fórmula TF-IDF.

IMPLEMENTAÇÃO NO ES 8.x+:
Como o ES 8.x removeu similarity "classic", implementamos TF-IDF via
SCRIPTED SIMILARITY usando código Painless* que calcula:
*O
Painless é a linguagem de script padrão projetada especificamente para o Elasticsearch. 
Introduzido na versão 5.0, ele substituiu outras linguagens de script. Em geral 
você não vai precisar dele. Usamos aqui pra implementar uma formula parecida com a do VSM, 
que não é mais suportado pelo elasticSearch desde a versão 7. 
1. TF (Term Frequency):
   - tf = √(freq)
   - Raiz quadrada da frequência do termo. Veja que poderia ter usado a freq diretamente
   - Suaviza impacto de repetições

2. IDF (Inverse Document Frequency):
   - idf = log((docCount + 1) / (docFreq + 1)) + 1  # esses +1s são pra evitar zeros na conta
   - Mede raridade do termo no corpus
   - Termos raros têm maior peso

3. Normalização:
   - norm = 1 / √(length)  (note que a norma aqui é uma aproximação simples, não a norma completa da fórmula. )
   - Ajusta pelo tamanho do documento

4. Score Final:
   - score = query.boost × tf × idf × norm  (nossa norma foi criada pra ser 1/√(length)), por isso tá multiplicando ao invés de dividindo

COMPARAÇÃO COM BM25:

TF-IDF (Salton):
✓ Mais simples e intuitivo
✓ Base teórica sólida (espaço vetorial)
✓ Crescimento suave de TF (raiz quadrada)
✗ Pode supervalorizar documentos longos

BM25:
✓ Saturação de frequência (diminishing returns)
✓ Normalização de comprimento mais sofisticada
✓ Parâmetros ajustáveis (k1, b)
✓ Geralmente melhor performance

================================================================================
"""

from elasticsearch import Elasticsearch
import json

def conectar_elasticsearch():
    """
    FUNÇÃO: Conecta ao servidor ElasticSearch
    
    Returns:
        Elasticsearch: Cliente conectado
    """
    es = Elasticsearch(['http://localhost:9200'])
    
    if not es.ping():
        raise Exception("ElasticSearch não está rodando! Execute ../BM25/initElastic.sh")
    
    return es

def busca_simples(es, consulta, tamanho=10):
    """
    TIPO 1: BUSCA SIMPLES usando TF-IDF
    
    COMO O TF-IDF CALCULA O SCORE:
    
    Para cada termo da consulta:
    1. Calcula TF no documento: √(frequência)
    2. Calcula IDF no corpus: 1 + log(N / df)
    3. Multiplica: TF × IDF
    4. Normaliza pelo tamanho do documento
    5. Soma scores de todos os termos
    
    EXEMPLO:
    Consulta: "responsabilidade civil"
    Doc1: contém "responsabilidade" 4x, "civil" 2x
    Doc2: contém "responsabilidade" 1x, "civil" 1x
    
    TF-IDF dará score maior para Doc1 devido às frequências maiores.
    BM25 daria scores mais próximos devido à saturação.
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da consulta
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA SIMPLES TF-IDF: '{consulta}'")
    print(f"Índice: ementas_tfidf | Similarity: classic (TF-IDF)")
    print('='*80)
    
    resposta = es.search(
        index='ementas_tfidf',  # Índice com TF-IDF
        body={
            'query': {
                'match': {
                    'highlight': consulta
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_multi_campo(es, consulta, tamanho=10):
    """
    TIPO 2: BUSCA MULTI-CAMPO com TF-IDF
    
    TF-IDF EM MÚLTIPLOS CAMPOS:
    - Calcula score TF-IDF independentemente em cada campo
    - Aplica boost (multiplicador de peso)
    - Combina scores usando estratégia escolhida
    
    BOOST IMPACT NO TF-IDF:
    title^2 significa: score_title × 2
    Matches no título contam duplamente.
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da consulta
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA MULTI-CAMPO TF-IDF: '{consulta}'")
    print(f"Campos: title^2, highlight, judging_organ")
    print('='*80)
    
    resposta = es.search(
        index='ementas_tfidf',
        body={
            'query': {
                'multi_match': {
                    'query': consulta,
                    'fields': ['title^2', 'highlight', 'judging_organ'],
                    'type': 'best_fields'
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_booleana(es, termos_obrigatorios, termos_opcionais=None, tamanho=10):
    """
    TIPO 3: BUSCA BOOLEANA com TF-IDF
    
    SCORE EM CONSULTAS BOOLEANAS COM TF-IDF:
    
    MUST (obrigatórios):
    - Score = soma dos TF-IDF de cada termo must
    - Documento DEVE conter todos
    
    SHOULD (opcionais):
    - Score adicional = soma dos TF-IDF de termos should presentes
    - Aumenta relevância mas não obriga presença
    
    EXEMPLO:
    must=["civil", "danos"] e should=["morais"]
    - Doc com "civil" e "danos": retornado
    - Doc com "civil", "danos" e "morais": score maior (preferido)
    
    Args:
        es: Cliente ElasticSearch
        termos_obrigatorios: Lista de termos MUST (AND)
        termos_opcionais: Lista de termos SHOULD (aumentam score)
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA BOOLEANA TF-IDF")
    print(f"MUST (obrigatórios): {termos_obrigatorios}")
    print(f"SHOULD (opcionais): {termos_opcionais}")
    print('='*80)
    
    must_clauses = [{'match': {'highlight': termo}} for termo in termos_obrigatorios]
    should_clauses = [{'match': {'highlight': termo}} for termo in (termos_opcionais or [])]
    
    resposta = es.search(
        index='ementas_tfidf',
        body={
            'query': {
                'bool': {
                    'must': must_clauses,
                    'should': should_clauses
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_com_filtro(es, consulta, tipo_documento=None, tamanho=10):
    """
    TIPO 4: BUSCA COM FILTRO usando TF-IDF
    
    FILTRO NÃO AFETA SCORE TF-IDF:
    - Query (must): calcula TF-IDF normalmente
    - Filter: apenas filtra (sim/não), não afeta score
    - Score final = apenas TF-IDF da query
    
    VANTAGEM:
    - Filtros são mais rápidos (cacheados)
    - Use para restrições exatas (datas, tipos, categorias)
    
    Args:
        es: Cliente ElasticSearch
        consulta: Texto da busca
        tipo_documento: Filtro exato de tipo
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA COM FILTRO TF-IDF: '{consulta}'")
    print(f"FILTRO: type = {tipo_documento}")
    print('='*80)
    
    query = {
        'bool': {
            'must': [
                {'match': {'highlight': consulta}}
            ]
        }
    }
    
    if tipo_documento:
        query['bool']['filter'] = [
            {'term': {'type': tipo_documento}}
        ]
    
    resposta = es.search(
        index='ementas_tfidf',
        body={
            'query': query,
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def busca_phrase(es, frase, tamanho=10):
    """
    TIPO 5: BUSCA POR FRASE EXATA com TF-IDF
    
    TF-IDF EM MATCH_PHRASE:
    - Calcula TF-IDF considerando a frase como unidade
    - Ordem das palavras importa
    - Proximidade entre termos afeta score
    
    DIFERENÇA vs MATCH:
    match: "nexo causalidade" → busca termos separadamente
    match_phrase: "nexo de causalidade" → busca frase exata
    
    Args:
        es: Cliente ElasticSearch
        frase: Frase exata a buscar
        tamanho: Número de resultados
    """
    print(f"\n{'='*80}")
    print(f"BUSCA POR FRASE TF-IDF: '{frase}'")
    print(f"Tipo: Match Phrase (ordem importa)")
    print('='*80)
    
    resposta = es.search(
        index='ementas_tfidf',
        body={
            'query': {
                'match_phrase': {
                    'highlight': frase
                }
            },
            'size': tamanho
        }
    )
    
    exibir_resultados(resposta)

def exibir_resultados(resposta):
    """
    FUNÇÃO: Exibe resultados formatados
    
    INTERPRETANDO SCORES TF-IDF:
    - Scores não têm valor máximo fixo
    - Quanto maior, mais relevante
    - Valores dependem de: TF, IDF, normalização
    - Compare scores relativos (entre documentos)
    
    COMPARAÇÃO COM BM25:
    - TF-IDF tende a dar scores maiores para docs longos com repetições
    - BM25 satura, dando scores mais equilibrados
    - Experimente mesma query nos dois índices para comparar!
    
    Args:
        resposta: Resposta do ElasticSearch
    """
    hits = resposta['hits']
    total = hits['total']['value']
    tempo = resposta['took']
    
    print(f"\nTotal de resultados: {total} | Tempo: {tempo}ms")
    print()
    
    if total == 0:
        print("Nenhum resultado encontrado.")
        return
    
    for i, hit in enumerate(hits['hits'], 1):
        # SCORE TF-IDF: calculado conforme explicado acima
        score = hit['_score']
        doc = hit['_source']
        
        print(f"{i}. Score TF-IDF: {score:.4f}")
        print(f"   ID: {doc['id']}")
        print(f"   Título: {doc['title']}")
        print(f"   Órgão: {doc.get('judging_organ', 'N/A')}")
        print(f"   Tipo: {doc.get('type', 'N/A')}")
        
        highlight_text = doc.get('highlight', '')
        if len(highlight_text) > 200:
            highlight_text = highlight_text[:200] + '...'
        print(f"   Texto: {highlight_text}")
        print()

def estatisticas_indice(es):
    """
    FUNÇÃO: Exibe estatísticas do índice TF-IDF
    """
    print(f"\n{'='*80}")
    print("ESTATÍSTICAS DO ÍNDICE TF-IDF")
    print('='*80)
    
    contagem = es.count(index='ementas_tfidf')
    print(f"Total de documentos: {contagem['count']}")
    
    # Agregação por tipo
    resposta = es.search(
        index='ementas_tfidf',
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

def comparar_com_bm25(es, consulta):
    """
    FUNÇÃO ESPECIAL: Compara resultados TF-IDF vs BM25
    
    Executa a mesma busca nos dois índices e mostra diferenças.
    Útil para entender impacto prático da escolha do algoritmo.
    
    Args:
        es: Cliente ElasticSearch
        consulta: Consulta a comparar
    """
    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO: TF-IDF vs BM25")
    print(f"Consulta: '{consulta}'")
    print('='*80)
    
    # Busca com TF-IDF
    resp_tfidf = es.search(
        index='ementas_tfidf',
        body={'query': {'match': {'highlight': consulta}}, 'size': 5}
    )
    
    # Busca com BM25 (se o índice existir)
    try:
        resp_bm25 = es.search(
            index='ementas',
            body={'query': {'match': {'highlight': consulta}}, 'size': 5}
        )
        
        print("\n📊 TOP 5 RESULTADOS:\n")
        print(f"{'Posição':<10} {'TF-IDF Score':<15} {'BM25 Score':<15} {'ID Documento'}")
        print("-" * 80)
        
        for i in range(min(5, len(resp_tfidf['hits']['hits']))):
            tfidf_hit = resp_tfidf['hits']['hits'][i]
            bm25_hit = resp_bm25['hits']['hits'][i] if i < len(resp_bm25['hits']['hits']) else None
            
            tfidf_score = tfidf_hit['_score']
            bm25_score = bm25_hit['_score'] if bm25_hit else 0
            doc_id = tfidf_hit['_source']['id'][:30]
            
            print(f"{i+1:<10} {tfidf_score:<15.4f} {bm25_score:<15.4f} {doc_id}")
        
        print("\n🔍 OBSERVAÇÕES:")
        print("  - Scores TF-IDF tendem a ser maiores que BM25")
        print("  - Ranking pode ser diferente entre os algoritmos")
        print("  - TF-IDF favorece documentos longos com repetições")
        print("  - BM25 é mais equilibrado com saturação de frequência")
        
    except Exception as e:
        print(f"\n⚠ Índice BM25 não encontrado. Execute ../BM25/indexa.py primeiro.")

def main():
    """
    FUNÇÃO PRINCIPAL: Demonstra buscas com TF-IDF de Salton
    """
    print("="*80)
    print("EXEMPLOS DE BUSCA - VECTOR SPACE MODEL (TF-IDF DE SALTON)")
    print("="*80)
    print()
    print("Este script demonstra buscas usando TF-IDF de Salton (1971)")
    print("implementado via SCRIPTED SIMILARITY no ElasticSearch 8.x+")
    print()
    print("FÓRMULA: score = query.boost × √(freq) × idf × (1/√(length))")
    print()
    
    try:
        es = conectar_elasticsearch()
        print("✓ Conectado ao ElasticSearch")
        
        # Verifica se índice existe
        if not es.indices.exists(index='ementas_tfidf'):
            print("\n❌ Índice 'ementas_tfidf' não encontrado!")
            print("Execute primeiro: python indexa.py")
            return
        
        # Estatísticas
        estatisticas_indice(es)
        
        # Exemplos de buscas
        busca_simples(es, "responsabilidade civil danos morais", tamanho=5)
        
        busca_multi_campo(es, "apelação", tamanho=5)
        
        busca_booleana(es, 
                      termos_obrigatorios=["civil", "danos"], 
                      termos_opcionais=["morais", "materiais"],
                      tamanho=5)
        
        busca_com_filtro(es, "sentença", tipo_documento="ACORDAO", tamanho=5)
        
        busca_phrase(es, "nexo de causalidade", tamanho=5)
        
        # COMPARAÇÃO DIRETA
        comparar_com_bm25(es, "responsabilidade civil")
        
        print("\n" + "="*80)
        print("✓ EXEMPLOS CONCLUÍDOS!")
        print("="*80)
        print("\n🎓 EXERCÍCIOS SUGERIDOS:")
        print("  1. Compare mesmas buscas em ../BM25/busca.py")
        print("  2. Observe diferenças nos scores e rankings")
        print("  3. Teste com consultas que repetem termos")
        print("  4. Experimente com documentos longos vs curtos")
        print("  5. Modifique o script Painless para experimentar variações")
        print()
        print("📚 PARA ENTENDER MELHOR:")
        print("  - TF-IDF (Salton, 1971): https://en.wikipedia.org/wiki/Tf-idf")
        print("  - Vector Space Model: https://en.wikipedia.org/wiki/Vector_space_model")
        print("  - Scripted Similarity: https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

# Ponto de entrada
if __name__ == "__main__":
    main()
