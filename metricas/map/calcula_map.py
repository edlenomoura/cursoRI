"""
Programa para calcular MAP (Mean Average Precision)

Este programa calcula a métrica MAP para avaliar a qualidade de sistemas de 
recuperação de informação. O MAP mede a precisão média dos documentos relevantes
considerando suas posições no ranking.

Diferente do NDCG que usa notas graduadas (0, 1, 2), o MAP usa classificação 
binária: relevante (1) ou irrelevante (0).

Conversão das notas:
- Nota = 0 → Irrelevante (0)
- Nota > 0 → Relevante (1)

Autor: Exemplo didático para curso de RI
Data: Março 2026
"""

import json
import sys
import os

# Adiciona o diretório pai ao path para acessar os arquivos de exemplo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def carregar_json(caminho_arquivo):
    """
    Carrega um arquivo JSON e retorna seu conteúdo.
    
    Args:
        caminho_arquivo: Caminho para o arquivo JSON
        
    Returns:
        Dicionário com o conteúdo do arquivo
    """
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)


def criar_mapa_relevancia(query_scores):
    """
    Cria um dicionário que mapeia (query, doc_id) -> relevância binária
    
    IMPORTANTE: Converte notas graduadas em relevância binária:
    - Nota = 0 → Irrelevante (0)
    - Nota > 0 → Relevante (1)
    
    Args:
        query_scores: Dados do arquivo query_scores.json
        
    Returns:
        Dicionário onde a chave é (query, doc_id) e o valor é 0 ou 1
    """
    mapa = {}
    
    for consulta in query_scores['search_queries']:
        query = consulta['query']
        
        # Para cada documento avaliado nesta consulta
        for resultado in consulta['results']:
            doc_id = resultado['doc_id']
            nota = resultado['nota']
            
            # Converte nota para relevância binária
            relevancia = 1 if nota > 0 else 0
            
            # Cria a chave composta (query, doc_id)
            mapa[(query, doc_id)] = relevancia
    
    return mapa


def calcular_precision_at_k(relevancia_ordenada, k):
    """
    Calcula a Precision@k (Precisão nos primeiros k documentos)
    
    Precision@k responde: "Dos k documentos retornados, quantos são relevantes?"
    
    Fórmula: P@k = (número de docs relevantes nos primeiros k) / k
    
    Args:
        relevancia_ordenada: Lista de relevâncias (0 ou 1) na ordem do ranking
        k: Posição onde calcular a precisão
        
    Returns:
        Valor da Precision@k (entre 0 e 1)
    """
    if k > len(relevancia_ordenada) or k <= 0:
        return 0.0
    
    # Conta quantos documentos relevantes existem nos primeiros k
    relevantes_ate_k = sum(relevancia_ordenada[:k])
    
    # Divide pelo total de documentos analisados (k)
    precision = relevantes_ate_k / k
    
    return precision


def calcular_average_precision(relevancia_ordenada):
    """
    Calcula o AP (Average Precision) para uma consulta
    
    O AP mede a qualidade do ranking considerando:
    1. A precisão em cada posição onde há um documento relevante
    2. A posição dos documentos relevantes (quanto mais cedo, melhor)
    
    Fórmula: AP = (Σ (P@k × rel(k))) / total_de_relevantes
    
    Onde:
    - P@k é a precisão nos primeiros k documentos
    - rel(k) é 1 se o documento na posição k é relevante, 0 caso contrário
    - Só somamos quando rel(k) = 1
    
    Exemplo:
    - Ranking: [1, 0, 1, 1, 0]  (1=relevante, 0=irrelevante)
    - Posição 1: P@1 = 1/1 = 1.00, relevante → soma 1.00
    - Posição 2: P@2 = 1/2 = 0.50, irrelevante → soma 0
    - Posição 3: P@3 = 2/3 = 0.67, relevante → soma 0.67
    - Posição 4: P@4 = 3/4 = 0.75, relevante → soma 0.75
    - Posição 5: P@5 = 3/5 = 0.60, irrelevante → soma 0
    - AP = (1.00 + 0.67 + 0.75) / 3 = 0.806
    
    Args:
        relevancia_ordenada: Lista de relevâncias (0 ou 1) na ordem do ranking
        
    Returns:
        Valor do Average Precision (entre 0 e 1)
    """
    # Conta quantos documentos relevantes existem no total
    total_relevantes = sum(relevancia_ordenada)
    
    # Se não há documentos relevantes, AP = 0 por convenção
    if total_relevantes == 0:
        return 0.0
    
    soma_precisoes = 0.0
    
    # Para cada posição no ranking
    for k in range(1, len(relevancia_ordenada) + 1):
        # Verifica se o documento nesta posição é relevante
        if relevancia_ordenada[k - 1] == 1:
            # Calcula a precisão até esta posição
            precision_k = calcular_precision_at_k(relevancia_ordenada, k)
            
            # Adiciona à soma (ponderado por rel(k) que é 1)
            soma_precisoes += precision_k
            
            # (Opcional) Para fins didáticos
            # print(f"    Posição {k}: relevante, P@{k} = {precision_k:.4f}")
    
    # Calcula a média dividindo pelo total de relevantes
    average_precision = soma_precisoes / total_relevantes
    
    return average_precision


def calcular_map(lista_aps):
    """
    Calcula o MAP (Mean Average Precision)
    
    O MAP é simplesmente a média dos Average Precisions de todas as consultas.
    
    Fórmula: MAP = (Σ AP(q)) / número_de_consultas
    
    Args:
        lista_aps: Lista com os AP de cada consulta
        
    Returns:
        Valor do MAP (entre 0 e 1)
    """
    if not lista_aps:
        return 0.0
    
    return sum(lista_aps) / len(lista_aps)


def avaliar_sistema(nome_sistema, arquivo_sistema, mapa_relevancia):
    """
    Avalia um sistema calculando o MAP.
    
    Args:
        nome_sistema: Nome do sistema (para exibição)
        arquivo_sistema: Caminho para o arquivo JSON do sistema
        mapa_relevancia: Dicionário (query, doc_id) -> relevância (0 ou 1)
        
    Returns:
        Lista de APs por consulta e MAP médio
    """
    # Carrega os resultados do sistema
    dados_sistema = carregar_json(arquivo_sistema)
    
    print(f"\n{'='*80}")
    print(f"AVALIANDO {nome_sistema}")
    print(f"{'='*80}\n")
    
    aps = []
    
    # Para cada consulta
    for idx, consulta in enumerate(dados_sistema['search_queries'], 1):
        query = consulta['query']
        resultados = consulta['results']
        
        print(f"Consulta {idx}: {query}")
        print(f"{'-'*80}")
        
        # Obtém as relevâncias dos documentos retornados pelo sistema
        # Ignora documentos que não têm avaliação
        relevancia_ordenada = []
        for pos, resultado in enumerate(resultados, 1):
            doc_id = resultado['doc_id']
            chave = (query, doc_id)
            
            # Verifica se este documento foi avaliado
            if chave in mapa_relevancia:
                relevancia = mapa_relevancia[chave]
                relevancia_ordenada.append(relevancia)
                
                status = "RELEVANTE" if relevancia == 1 else "irrelevante"
                print(f"  Posição {pos}: Doc {doc_id} → {status}")
            else:
                # Documento não avaliado - será ignorado
                print(f"  Posição {pos}: Doc {doc_id} → não avaliado (ignorado)")
        
        print(f"\n  Vetor de relevâncias: {relevancia_ordenada}")
        
        # Conta quantos documentos relevantes existem para esta consulta
        total_relevantes_disponiveis = sum([
            rel for (q, doc), rel in mapa_relevancia.items() if q == query
        ])
        
        total_relevantes_retornados = sum(relevancia_ordenada)
        
        print(f"  Total de relevantes disponíveis: {total_relevantes_disponiveis}")
        print(f"  Total de relevantes retornados: {total_relevantes_retornados}")
        
        # Calcula o Average Precision para esta consulta
        ap = calcular_average_precision(relevancia_ordenada)
        
        print(f"\n  ⭐ Average Precision (AP) = {ap:.4f}")
        
        # Mostra o cálculo detalhado
        if total_relevantes_retornados > 0:
            print(f"\n  📝 Cálculo detalhado:")
            soma = 0.0
            for k in range(1, len(relevancia_ordenada) + 1):
                if relevancia_ordenada[k - 1] == 1:
                    p_at_k = calcular_precision_at_k(relevancia_ordenada, k)
                    soma += p_at_k
                    print(f"     Posição {k} (relevante): P@{k} = {p_at_k:.4f}")
            print(f"     Soma das precisões = {soma:.4f}")
            print(f"     AP = {soma:.4f} / {total_relevantes_retornados} = {ap:.4f}")
        else:
            print(f"     Nenhum documento relevante retornado → AP = 0")
        
        print()
        
        aps.append(ap)
    
    # Calcula o MAP
    map_score = calcular_map(aps)
    
    print(f"{'='*80}")
    print(f"MAP DO {nome_sistema}: {map_score:.4f}")
    print(f"{'='*80}\n")
    
    return aps, map_score


def main():
    """
    Função principal que executa o programa.
    """
    print("="*80)
    print("CALCULADORA DE MAP - Sistema de Recuperação de Informação")
    print("="*80)
    print("\n📖 MAP (Mean Average Precision):")
    print("   • Métrica que avalia rankings usando classificação binária")
    print("   • Relevante (1) ou Irrelevante (0)")
    print("   • Considera a posição dos documentos relevantes")
    print("   • Quanto mais cedo aparecem docs relevantes, melhor o MAP\n")
    print("⚙️  Conversão de notas:")
    print("   • Nota = 0 → Irrelevante (0)")
    print("   • Nota > 0 → Relevante (1)\n")
    print("="*80)
    
    # Define os caminhos dos arquivos (usando os mesmos do NDCG)
    arquivo_scores = '../ndcg/sampleFiles/query_scores.json'
    arquivo_sistema1 = '../ndcg/sampleFiles/sistema1.json'
    arquivo_sistema2 = '../ndcg/sampleFiles/sistema2.json'
    
    # Carrega as avaliações de relevância
    print("\nCarregando avaliações de relevância...")
    query_scores = carregar_json(arquivo_scores)
    
    # Cria um mapa para busca rápida (convertendo para binário)
    print("Criando mapa de relevância binária...")
    mapa_relevancia = criar_mapa_relevancia(query_scores)
    
    # Mostra estatísticas
    total_docs = len(mapa_relevancia)
    total_relevantes = sum(mapa_relevancia.values())
    total_irrelevantes = total_docs - total_relevantes
    
    print(f"\nTotal de documentos avaliados: {total_docs}")
    print(f"  • Relevantes: {total_relevantes}")
    print(f"  • Irrelevantes: {total_irrelevantes}")
    
    # Avalia o Sistema 1
    aps_sistema1, map_sistema1 = avaliar_sistema(
        "SISTEMA 1", 
        arquivo_sistema1, 
        mapa_relevancia
    )
    
    # Avalia o Sistema 2
    aps_sistema2, map_sistema2 = avaliar_sistema(
        "SISTEMA 2", 
        arquivo_sistema2, 
        mapa_relevancia
    )
    
    # Comparação final
    print("\n" + "="*80)
    print("🏆 COMPARAÇÃO FINAL")
    print("="*80)
    print(f"MAP Sistema 1: {map_sistema1:.4f}")
    print(f"MAP Sistema 2: {map_sistema2:.4f}")
    
    if map_sistema1 > map_sistema2:
        diferenca = map_sistema1 - map_sistema2
        print(f"\n✅ Sistema 1 é melhor por {diferenca:.4f} pontos de MAP")
    elif map_sistema2 > map_sistema1:
        diferenca = map_sistema2 - map_sistema1
        print(f"\n✅ Sistema 2 é melhor por {diferenca:.4f} pontos de MAP")
    else:
        print(f"\n⚖️  Ambos os sistemas têm o mesmo MAP")
    
    # Análise por consulta
    print("\n" + "="*80)
    print("📋 COMPARAÇÃO POR CONSULTA")
    print("="*80)
    print(f"{'Consulta':<10} {'Sistema 1':<15} {'Sistema 2':<15} {'Melhor'}")
    print("-"*80)
    
    for i in range(len(aps_sistema1)):
        melhor = ""
        if aps_sistema1[i] > aps_sistema2[i]:
            melhor = "Sistema 1 ✓"
        elif aps_sistema2[i] > aps_sistema1[i]:
            melhor = "Sistema 2 ✓"
        else:
            melhor = "Empate"
        
        print(f"{i+1:<10} {aps_sistema1[i]:<15.4f} {aps_sistema2[i]:<15.4f} {melhor}")
    
    print("="*80)
    
    # Interpretação didática
    print("\n💡 INTERPRETAÇÃO DOS RESULTADOS:")
    print("-"*80)
    
    if map_sistema1 >= 0.8 or map_sistema2 >= 0.8:
        print("• MAP acima de 0.8 indica excelente qualidade de ranking")
    
    if map_sistema1 >= 0.6 or map_sistema2 >= 0.6:
        print("• MAP acima de 0.6 indica boa qualidade de ranking")
    
    if map_sistema1 < 0.5 or map_sistema2 < 0.5:
        print("• MAP abaixo de 0.5 indica que o sistema precisa melhorar")
    
    print("\n📚 SOBRE O MAP:")
    print("• MAP é mais sensível à ordem dos documentos relevantes")
    print("• Penaliza sistemas que colocam relevantes em posições baixas")
    print("• Útil quando todos os documentos relevantes são igualmente importantes")
    print("• Diferente do NDCG, não considera níveis de relevância (apenas binário)")
    
    print("="*80)


if __name__ == "__main__":
    main()
