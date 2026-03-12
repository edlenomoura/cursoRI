"""
Programa para calcular NDCG (Normalized Discounted Cumulative Gain)

Este programa calcula a métrica NDCG para avaliar a qualidade de sistemas de 
recuperação de informação. O NDCG mede o quão bem um sistema ranqueia documentos
comparado com um ranking ideal.

Autor: Exemplo didático para curso de RI
Data: Março 2026
"""

import json
import math


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
    Cria um dicionário que mapeia (query, doc_id) -> nota de relevância
    
    Isso facilita a busca rápida da nota de um documento específico
    para uma consulta específica.
    
    Args:
        query_scores: Dados do arquivo query_scores.json
        
    Returns:
        Dicionário onde a chave é (query, doc_id) e o valor é a nota
    """
    mapa = {}
    
    for consulta in query_scores['search_queries']:
        query = consulta['query']
        
        # Para cada documento avaliado nesta consulta
        for resultado in consulta['results']:
            doc_id = resultado['doc_id']
            nota = resultado['nota']
            
            # Cria a chave composta (query, doc_id)
            mapa[(query, doc_id)] = nota
    
    return mapa


def calcular_dcg(notas_ordenadas, k=None):
    """
    Calcula o DCG (Discounted Cumulative Gain)
    
    O DCG mede o ganho acumulado considerando a posição dos documentos.
    Documentos relevantes em posições mais altas contribuem mais para o score.
    
    Fórmula: DCG@k = Σ((2^rel_i - 1) / log₂(i+1)) para i de 1 até k
    
    Onde:
    - rel_i é a nota de relevância do documento na posição i
    - log₂(i+1) é o fator de desconto (penaliza posições mais baixas)
    - 2^rel_i - 1 transforma a nota de relevância em ganho
    
    Args:
        notas_ordenadas: Lista de notas na ordem em que aparecem no ranking
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do DCG
    """
    if k is None:
        k = len(notas_ordenadas)
    
    dcg = 0.0
    
    # Itera sobre as primeiras k posições
    for i in range(min(k, len(notas_ordenadas))):
        nota = notas_ordenadas[i]
        posicao = i + 1  # Posições começam em 1, não em 0
        
        # Calcula o ganho para esta posição
        # 2^nota - 1 transforma a nota em ganho
        ganho = (2 ** nota) - 1
        
        # log₂(posicao + 1) é o fator de desconto
        # Quanto maior a posição, menor o ganho
        desconto = math.log2(posicao + 1)
        
        # Adiciona a contribuição desta posição ao DCG
        dcg += ganho / desconto
        
        # (Opcional) Imprimir para fins didáticos
        # print(f"  Posição {posicao}: nota={nota}, ganho={ganho:.2f}, desconto={desconto:.2f}, contribuição={ganho/desconto:.4f}")
    
    return dcg


def calcular_idcg(notas_disponiveis, k=None):
    """
    Calcula o IDCG (Ideal Discounted Cumulative Gain)
    
    O IDCG é o melhor DCG possível, obtido quando ordenamos os documentos
    de forma ideal (do mais relevante para o menos relevante).
    
    Args:
        notas_disponiveis: Lista de todas as notas disponíveis
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do IDCG
    """
    # Ordena as notas em ordem decrescente (melhor ranking possível)
    notas_ideais = sorted(notas_disponiveis, reverse=True)
    
    # Calcula o DCG deste ranking ideal
    return calcular_dcg(notas_ideais, k)


def calcular_ndcg(notas_ordenadas, notas_disponiveis, k=None):
    """
    Calcula o NDCG (Normalized Discounted Cumulative Gain)
    
    O NDCG normaliza o DCG dividindo pelo IDCG, resultando em um valor entre 0 e 1.
    - NDCG = 1.0 significa ranking perfeito
    - NDCG = 0.0 significa ranking muito ruim
    
    Fórmula: NDCG = DCG / IDCG
    
    Args:
        notas_ordenadas: Lista de notas na ordem do ranking do sistema
        notas_disponiveis: Lista de todas as notas disponíveis
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do NDCG (entre 0 e 1)
    """
    # Calcula o DCG do ranking atual
    dcg = calcular_dcg(notas_ordenadas, k)
    
    # Calcula o DCG do ranking ideal
    idcg = calcular_idcg(notas_disponiveis, k)
    
    # Se IDCG é zero, não há documentos relevantes
    # Neste caso, retornamos 0.0 por convenção
    if idcg == 0:
        return 0.0
    
    # Normaliza o DCG
    ndcg = dcg / idcg
    
    return ndcg


def calcular_dcg_linear(notas_ordenadas, k=None):
    """
    Calcula o DCG (Discounted Cumulative Gain) com DESCONTO LINEAR
    
    Esta é uma versão alternativa e mais simples do DCG, que usa:
    - Desconto linear (i) em vez de logarítmico
    - Ganho direto (rel_i) em vez de exponencial
    
    Fórmula: DCG@k = Σ(rel_i / i) para i de 1 até k
    
    Onde:
    - rel_i é a nota de relevância do documento na posição i
    - i é o fator de desconto linear (penaliza posições mais baixas)
    
    Diferenças em relação ao DCG padrão:
    - Mais simples de calcular e entender
    - Penaliza menos as posições intermediárias
    - Não dá tanto peso extra para documentos muito relevantes
    
    Args:
        notas_ordenadas: Lista de notas na ordem em que aparecem no ranking
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do DCG linear
    """
    if k is None:
        k = len(notas_ordenadas)
    
    dcg = 0.0
    
    # Itera sobre as primeiras k posições
    for i in range(min(k, len(notas_ordenadas))):
        nota = notas_ordenadas[i]
        posicao = i + 1  # Posições começam em 1, não em 0
        
        # Calcula o ganho para esta posição
        # Usa diretamente a nota (sem transformação exponencial)
        ganho = nota
        
        # Usa a posição diretamente como desconto (linear)
        desconto = posicao
        
        # Adiciona a contribuição desta posição ao DCG
        dcg += ganho / desconto
        
        # (Opcional) Imprimir para fins didáticos
        # print(f"  Posição {posicao}: nota={nota}, ganho={ganho:.2f}, desconto={desconto:.2f}, contribuição={ganho/desconto:.4f}")
    
    return dcg


def calcular_idcg_linear(notas_disponiveis, k=None):
    """
    Calcula o IDCG (Ideal DCG) usando a versão linear
    
    O IDCG é o melhor DCG possível com desconto linear,
    obtido ordenando os documentos de forma ideal.
    
    Args:
        notas_disponiveis: Lista de todas as notas disponíveis
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do IDCG linear
    """
    # Ordena as notas em ordem decrescente (melhor ranking possível)
    notas_ideais = sorted(notas_disponiveis, reverse=True)
    
    # Calcula o DCG linear deste ranking ideal
    return calcular_dcg_linear(notas_ideais, k)


def calcular_ndcg_linear(notas_ordenadas, notas_disponiveis, k=None):
    """
    Calcula o NDCG usando a fórmula linear simplificada
    
    Esta versão usa a fórmula: DCG = Σ(rel_i / i)
    
    Diferenças em relação ao NDCG padrão:
    - Valores absolutos de DCG geralmente menores
    - Distribuição diferente de scores
    - Pode ter interpretação diferente do que é "bom"
    
    Args:
        notas_ordenadas: Lista de notas na ordem do ranking do sistema
        notas_disponiveis: Lista de todas as notas disponíveis
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Valor do NDCG linear (entre 0 e 1)
    """
    # Calcula o DCG linear do ranking atual
    dcg = calcular_dcg_linear(notas_ordenadas, k)
    
    # Calcula o DCG linear do ranking ideal
    idcg = calcular_idcg_linear(notas_disponiveis, k)
    
    # Se IDCG é zero, não há documentos relevantes
    if idcg == 0:
        return 0.0
    
    # Normaliza o DCG
    ndcg = dcg / idcg
    
    return ndcg


def avaliar_sistema(nome_sistema, arquivo_sistema, mapa_relevancia, k=None):
    """
    Avalia um sistema calculando o NDCG para cada consulta.
    
    Args:
        nome_sistema: Nome do sistema (para exibição)
        arquivo_sistema: Caminho para o arquivo JSON do sistema
        mapa_relevancia: Dicionário (query, doc_id) -> nota
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Lista de NDCGs por consulta e NDCG médio
    """
    # Carrega os resultados do sistema
    dados_sistema = carregar_json(arquivo_sistema)
    
    print(f"\n{'='*80}")
    print(f"AVALIANDO {nome_sistema}")
    print(f"{'='*80}\n")
    
    ndcgs = []
    
    # Para cada consulta
    for idx, consulta in enumerate(dados_sistema['search_queries'], 1):
        query = consulta['query']
        resultados = consulta['results']
        
        print(f"Consulta {idx}: {query}")
        print(f"{'-'*80}")
        
        # Obtém as notas dos documentos retornados pelo sistema
        # Ignora documentos que não têm avaliação
        notas_ordenadas = []
        for resultado in resultados:
            doc_id = resultado['doc_id']
            chave = (query, doc_id)
            
            # Verifica se este documento foi avaliado
            if chave in mapa_relevancia:
                nota = mapa_relevancia[chave]
                notas_ordenadas.append(nota)
                print(f"  Documento {doc_id}: nota = {nota}")
            else:
                # Documento não avaliado - será ignorado
                print(f"  Documento {doc_id}: não avaliado (ignorado)")
        
        # Obtém todas as notas disponíveis para esta consulta
        # (para calcular o IDCG)
        notas_disponiveis = [nota for (q, doc), nota in mapa_relevancia.items() if q == query]
        
        print(f"\n  Notas no ranking do sistema: {notas_ordenadas}")
        print(f"  Notas ordenadas idealmente: {sorted(notas_disponiveis, reverse=True)}")
        
        # Calcula DCG, IDCG e NDCG (versão mais comum com log)
        dcg = calcular_dcg(notas_ordenadas, k)
        idcg = calcular_idcg(notas_disponiveis, k)
        ndcg = calcular_ndcg(notas_ordenadas, notas_disponiveis, k)
        
        print(f"\n  DCG  = {dcg:.4f}")
        print(f"  IDCG = {idcg:.4f}")
        print(f"  NDCG = {ndcg:.4f}")
        print()
        
        ndcgs.append(ndcg)
    
    # Calcula o NDCG médio
    ndcg_medio = sum(ndcgs) / len(ndcgs) if ndcgs else 0.0
    
    print(f"{'='*80}")
    print(f"NDCG MÉDIO DO {nome_sistema}: {ndcg_medio:.4f}")
    print(f"{'='*80}\n")
    
    return ndcgs, ndcg_medio


def avaliar_sistema_comparativo(nome_sistema, arquivo_sistema, mapa_relevancia, k=None):
    """
    Avalia um sistema calculando AMBAS as versões do NDCG para comparação.
    
    Calcula:
    1. NDCG padrão mais encontrado: usando (2^rel - 1) / log₂(i+1)
    2. NDCG linear: usando rel / i
    
    Args:
        nome_sistema: Nome do sistema (para exibição)
        arquivo_sistema: Caminho para o arquivo JSON do sistema
        mapa_relevancia: Dicionário (query, doc_id) -> nota
        k: Número de documentos a considerar (None = todos)
        
    Returns:
        Tupla com (ndcgs_padrao, ndcg_medio_padrao, ndcgs_linear, ndcg_medio_linear)
    """
    # Carrega os resultados do sistema
    dados_sistema = carregar_json(arquivo_sistema)
    
    print(f"\n{'='*80}")
    print(f"AVALIANDO {nome_sistema} - COMPARAÇÃO ENTRE FÓRMULAS DE NDCG")
    print(f"{'='*80}\n")
    
    ndcgs_padrao = []
    ndcgs_linear = []
    
    # Para cada consulta
    for idx, consulta in enumerate(dados_sistema['search_queries'], 1):
        query = consulta['query']
        resultados = consulta['results']
        
        print(f"Consulta {idx}: {query}")
        print(f"{'-'*80}")
        
        # Obtém as notas dos documentos retornados pelo sistema
        notas_ordenadas = []
        for resultado in resultados:
            doc_id = resultado['doc_id']
            chave = (query, doc_id)
            
            if chave in mapa_relevancia:
                nota = mapa_relevancia[chave]
                notas_ordenadas.append(nota)
                print(f"  Documento {doc_id}: nota = {nota}")
            else:
                print(f"  Documento {doc_id}: não avaliado (ignorado)")
        
        # Obtém todas as notas disponíveis para esta consulta
        notas_disponiveis = [nota for (q, doc), nota in mapa_relevancia.items() if q == query]
        
        print(f"\n  Notas no ranking do sistema: {notas_ordenadas}")
        print(f"  Notas ordenadas idealmente: {sorted(notas_disponiveis, reverse=True)}")
        
        # ===== VERSÃO PADRÃO (Logarítmica com ganho exponencial) =====
        print(f"\n  📊 VERSÃO PADRÃO MAIS POPULAR: DCG = Σ((2^rel_i - 1) / log₂(i+1))")
        dcg_padrao = calcular_dcg(notas_ordenadas, k)
        idcg_padrao = calcular_idcg(notas_disponiveis, k)
        ndcg_padrao = calcular_ndcg(notas_ordenadas, notas_disponiveis, k)
        
        print(f"     DCG  = {dcg_padrao:.4f}")
        print(f"     IDCG = {idcg_padrao:.4f}")
        print(f"     NDCG = {ndcg_padrao:.4f}")
        
        # ===== VERSÃO LINEAR (Desconto linear com ganho direto) =====
        print(f"\n  📊 VERSÃO LINEAR: DCG = Σ(rel_i / i)")
        dcg_linear = calcular_dcg_linear(notas_ordenadas, k)
        idcg_linear = calcular_idcg_linear(notas_disponiveis, k)
        ndcg_linear = calcular_ndcg_linear(notas_ordenadas, notas_disponiveis, k)
        
        print(f"     DCG  = {dcg_linear:.4f}")
        print(f"     IDCG = {idcg_linear:.4f}")
        print(f"     NDCG = {ndcg_linear:.4f}")
        
        # Comparação
        diferenca_ndcg = ndcg_padrao - ndcg_linear
        diferenca_dcg = dcg_padrao - dcg_linear
        
        print(f"\n  🔍 DIFERENÇAS:")
        print(f"     Diferença NDCG: {diferenca_ndcg:+.4f} (padrão - linear)")
        print(f"     Diferença DCG:  {diferenca_dcg:+.4f} (valores absolutos)")
        
        if abs(diferenca_ndcg) < 0.01:
            print(f"     → Rankings muito similares nas duas métricas")
        elif diferenca_ndcg > 0:
            print(f"     → Versão padrão avalia este ranking como melhor")
        else:
            print(f"     → Versão linear avalia este ranking como melhor")
        
        print()
        
        ndcgs_padrao.append(ndcg_padrao)
        ndcgs_linear.append(ndcg_linear)
    
    # Calcula os NDCG médios
    ndcg_medio_padrao = sum(ndcgs_padrao) / len(ndcgs_padrao) if ndcgs_padrao else 0.0
    ndcg_medio_linear = sum(ndcgs_linear) / len(ndcgs_linear) if ndcgs_linear else 0.0
    
    print(f"{'='*80}")
    print(f"RESUMO {nome_sistema}")
    print(f"{'='*80}")
    print(f"NDCG Médio (Versão Padrão): {ndcg_medio_padrao:.4f}")
    print(f"NDCG Médio (Versão Linear): {ndcg_medio_linear:.4f}")
    print(f"Diferença: {ndcg_medio_padrao - ndcg_medio_linear:+.4f}")
    print(f"{'='*80}\n")
    
    return ndcgs_padrao, ndcg_medio_padrao, ndcgs_linear, ndcg_medio_linear


def main():
    """
    Função principal que executa o programa.
    """
    print("="*80)
    print("CALCULADORA DE NDCG - Sistema de Recuperação de Informação")
    print("COMPARAÇÃO ENTRE DUAS FÓRMULAS DE CÁLCULO")
    print("="*80)
    print("\n📖 Este programa compara duas formas de calcular NDCG:\n")
    print("   1️⃣  VERSÃO DITA PADRÃO (mais comum na literatura, mas não necessariamente a única proposta dos autores):")
    print("       DCG = Σ((2^rel_i - 1) / log₂(i+1))")
    print("       • Desconto logarítmico: penaliza menos posições intermediárias")
    print("       • Ganho exponencial: dá muito mais peso para notas altas\n")
    print("   2️⃣  VERSÃO LINEAR (mais simples):")
    print("       DCG = Σ(rel_i / i)")
    print("       • Desconto linear: penaliza uniformemente")
    print("       • Ganho direto: peso proporcional à nota\n")
    print("="*80)
    
    # Define os caminhos dos arquivos
    arquivo_scores = 'sampleFiles/query_scores.json'
    arquivo_sistema1 = 'sampleFiles/sistema1.json'
    arquivo_sistema2 = 'sampleFiles/sistema2.json'
    
    # Carrega as avaliações de relevância
    print("\nCarregando avaliações de relevância...")
    query_scores = carregar_json(arquivo_scores)
    
    # Cria um mapa para busca rápida de notas
    print("Criando mapa de relevância...")
    mapa_relevancia = criar_mapa_relevancia(query_scores)
    
    print(f"\nTotal de documentos avaliados: {len(mapa_relevancia)}")
    
    # Avalia o Sistema 1 com ambas as versões
    (ndcgs_s1_padrao, ndcg_medio_s1_padrao, 
     ndcgs_s1_linear, ndcg_medio_s1_linear) = avaliar_sistema_comparativo(
        "SISTEMA 1", 
        arquivo_sistema1, 
        mapa_relevancia
    )
    
    # Avalia o Sistema 2 com ambas as versões
    (ndcgs_s2_padrao, ndcg_medio_s2_padrao,
     ndcgs_s2_linear, ndcg_medio_s2_linear) = avaliar_sistema_comparativo(
        "SISTEMA 2", 
        arquivo_sistema2, 
        mapa_relevancia
    )
    
    # ===== COMPARAÇÃO FINAL DETALHADA =====
    print("\n" + "="*80)
    print("🏆 COMPARAÇÃO FINAL ENTRE OS SISTEMAS")
    print("="*80)
    
    print("\n📊 RESULTADOS COM VERSÃO PADRÃO:")
    print(f"   NDCG Médio Sistema 1: {ndcg_medio_s1_padrao:.4f}")
    print(f"   NDCG Médio Sistema 2: {ndcg_medio_s2_padrao:.4f}")
    
    if ndcg_medio_s1_padrao > ndcg_medio_s2_padrao:
        diferenca = ndcg_medio_s1_padrao - ndcg_medio_s2_padrao
        print(f"   ✅ Sistema 1 é melhor por {diferenca:.4f} pontos")
    elif ndcg_medio_s2_padrao > ndcg_medio_s1_padrao:
        diferenca = ndcg_medio_s2_padrao - ndcg_medio_s1_padrao
        print(f"   ✅ Sistema 2 é melhor por {diferenca:.4f} pontos")
    else:
        print(f"   ⚖️  Empate técnico")
    
    print("\n📊 RESULTADOS COM VERSÃO LINEAR:")
    print(f"   NDCG Médio Sistema 1: {ndcg_medio_s1_linear:.4f}")
    print(f"   NDCG Médio Sistema 2: {ndcg_medio_s2_linear:.4f}")
    
    if ndcg_medio_s1_linear > ndcg_medio_s2_linear:
        diferenca = ndcg_medio_s1_linear - ndcg_medio_s2_linear
        print(f"   ✅ Sistema 1 é melhor por {diferenca:.4f} pontos")
    elif ndcg_medio_s2_linear > ndcg_medio_s1_linear:
        diferenca = ndcg_medio_s2_linear - ndcg_medio_s1_linear
        print(f"   ✅ Sistema 2 é melhor por {diferenca:.4f} pontos")
    else:
        print(f"   ⚖️  Empate técnico")
    
    # Análise de concordância
    print("\n" + "="*80)
    print("🔍 ANÁLISE COMPARATIVA DAS DUAS FÓRMULAS")
    print("="*80)
    
    print("\n💡 CONCORDÂNCIA ENTRE AS MÉTRICAS:")
    vencedor_padrao = "Sistema 2" if ndcg_medio_s2_padrao > ndcg_medio_s1_padrao else "Sistema 1"
    vencedor_linear = "Sistema 2" if ndcg_medio_s2_linear > ndcg_medio_s1_linear else "Sistema 1"
    
    if vencedor_padrao == vencedor_linear:
        print(f"   ✅ Ambas as métricas concordam: {vencedor_padrao} é melhor")
        print(f"   → Isso indica que a conclusão é robusta à escolha da fórmula")
    else:
        print(f"   ⚠️  As métricas discordam!")
        print(f"   → Versão padrão favorece: {vencedor_padrao}")
        print(f"   → Versão linear favorece: {vencedor_linear}")
        print(f"   → Considere analisar as consultas individualmente")
    
    print("\n💡 DIFERENÇAS NOS VALORES ABSOLUTOS:")
    print(f"   Sistema 1 - Diferença: {ndcg_medio_s1_padrao - ndcg_medio_s1_linear:+.4f} (padrão - linear)")
    print(f"   Sistema 2 - Diferença: {ndcg_medio_s2_padrao - ndcg_medio_s2_linear:+.4f} (padrão - linear)")
    
    print("\n💡 INTERPRETAÇÃO DIDÁTICA:")
    print("   • A versão PADRÃO é mais sensível a documentos muito relevantes")
    print("     nas primeiras posições (por causa de 2^rel - 1)")
    print("   • A versão LINEAR penaliza mais uniformemente todas as posições")
    print("     (desconto de 1/i é mais agressivo que 1/log(i+1))")
    print("   • Valores de NDCG podem ser diferentes, mas a ORDEM dos sistemas")
    print("     geralmente é preservada se os rankings são realmente diferentes")
    
    print("\n💡 QUANDO USAR CADA UMA?")
    print("   • VERSÃO PADRÃO: Recomendada comparações com outros trabalhos")
    print("      por ser bem popular (é a mais usada )")
    print("   • VERSÃO LINEAR: Útil para entender o conceito de forma mais simples")
    print("     ou quando se quer penalizar mais uniformemente as posições")
    print("     lembrar que os autores não propuseram uma fúrmula fechada para o NDCG.")
    
    print("\n" + "="*80)
    
    # Detalhamento por consulta
    print("\n📋 COMPARAÇÃO DETALHADA POR CONSULTA:")
    print("="*80)
    print(f"{'Consulta':<10} {'S1-Padrão':<12} {'S1-Linear':<12} {'S2-Padrão':<12} {'S2-Linear':<12} {'Observação'}")
    print("-"*80)
    
    for i in range(len(ndcgs_s1_padrao)):
        obs = ""
        # Verifica se há inversão de ranking nesta consulta
        if (ndcgs_s1_padrao[i] > ndcgs_s2_padrao[i] and ndcgs_s1_linear[i] < ndcgs_s2_linear[i]) or \
           (ndcgs_s1_padrao[i] < ndcgs_s2_padrao[i] and ndcgs_s1_linear[i] > ndcgs_s2_linear[i]):
            obs = "⚠️ Discordam"
        elif abs(ndcgs_s1_padrao[i] - ndcgs_s2_padrao[i]) < 0.01:
            obs = "≈ Similares"
        
        print(f"{i+1:<10} {ndcgs_s1_padrao[i]:<12.4f} {ndcgs_s1_linear[i]:<12.4f} "
              f"{ndcgs_s2_padrao[i]:<12.4f} {ndcgs_s2_linear[i]:<12.4f} {obs}")
    
    print("="*80)


if __name__ == "__main__":
    main()
