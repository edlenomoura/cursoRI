"""
Exemplo Didático: Cálculo Manual do NDCG Passo a Passo

Este programa mostra em detalhes como calcular o NDCG usando as duas fórmulas,
com um exemplo simples e todos os passos explicados.

Ideal para estudantes que querem entender exatamente como funciona cada cálculo.
"""

import math


def exemplo_detalhado():
    """
    Demonstra o cálculo completo do NDCG com um exemplo simples.
    """
    print("="*80)
    print("EXEMPLO DIDÁTICO: CÁLCULO MANUAL DO NDCG")
    print("="*80)
    
    # Exemplo: ranking retornado por um sistema
    ranking_sistema = [2, 1, 0, 1]
    print("\n📋 SITUAÇÃO:")
    print(f"   Um sistema retornou 4 documentos para uma consulta.")
    print(f"   As notas de relevância (avaliadas por especialistas) são:")
    print(f"   Posição 1: nota = {ranking_sistema[0]}")
    print(f"   Posição 2: nota = {ranking_sistema[1]}")
    print(f"   Posição 3: nota = {ranking_sistema[2]}")
    print(f"   Posição 4: nota = {ranking_sistema[3]}")
    
    # Ranking ideal
    ranking_ideal = sorted(ranking_sistema, reverse=True)
    print(f"\n   Ranking ideal (melhor possível): {ranking_ideal}")
    print(f"   Ranking do sistema: {ranking_sistema}")
    
    print("\n" + "="*80)
    print("CÁLCULO DA VERSÃO PADRÃO: DCG = Σ((2^rel_i - 1) / log₂(i+1))")
    print("="*80)
    
    # ===== VERSÃO PADRÃO =====
    print("\n🔢 PASSO 1: Calcular o DCG do ranking do sistema\n")
    
    dcg_padrao = 0.0
    for i, nota in enumerate(ranking_sistema):
        posicao = i + 1
        ganho = (2 ** nota) - 1
        desconto = math.log2(posicao + 1)
        contribuicao = ganho / desconto
        dcg_padrao += contribuicao
        
        print(f"   Posição {posicao} (nota = {nota}):")
        print(f"      Ganho     = 2^{nota} - 1 = {ganho}")
        print(f"      Desconto  = log₂({posicao}+1) = log₂({posicao+1}) = {desconto:.4f}")
        print(f"      Contribuição = {ganho} / {desconto:.4f} = {contribuicao:.4f}")
        print()
    
    print(f"   💡 DCG (sistema) = {dcg_padrao:.4f}")
    
    print("\n🔢 PASSO 2: Calcular o IDCG (ranking ideal)\n")
    
    idcg_padrao = 0.0
    for i, nota in enumerate(ranking_ideal):
        posicao = i + 1
        ganho = (2 ** nota) - 1
        desconto = math.log2(posicao + 1)
        contribuicao = ganho / desconto
        idcg_padrao += contribuicao
        
        print(f"   Posição {posicao} (nota = {nota}):")
        print(f"      Ganho     = 2^{nota} - 1 = {ganho}")
        print(f"      Desconto  = log₂({posicao}+1) = {desconto:.4f}")
        print(f"      Contribuição = {ganho} / {desconto:.4f} = {contribuicao:.4f}")
        print()
    
    print(f"   💡 IDCG (ideal) = {idcg_padrao:.4f}")
    
    print("\n🔢 PASSO 3: Calcular o NDCG\n")
    
    ndcg_padrao = dcg_padrao / idcg_padrao
    print(f"   NDCG = DCG / IDCG")
    print(f"   NDCG = {dcg_padrao:.4f} / {idcg_padrao:.4f}")
    print(f"   💡 NDCG = {ndcg_padrao:.4f}")
    
    print(f"\n   📊 Interpretação: {ndcg_padrao:.1%} do ranking ideal")
    if ndcg_padrao >= 0.9:
        print(f"   ✅ Ranking excelente!")
    elif ndcg_padrao >= 0.7:
        print(f"   ✅ Ranking bom!")
    elif ndcg_padrao >= 0.5:
        print(f"   ⚠️  Ranking regular")
    else:
        print(f"   ❌ Ranking ruim")
    
    # ===== VERSÃO LINEAR =====
    print("\n" + "="*80)
    print("CÁLCULO DA VERSÃO LINEAR: DCG = Σ(rel_i / i)")
    print("="*80)
    
    print("\n🔢 PASSO 1: Calcular o DCG do ranking do sistema\n")
    
    dcg_linear = 0.0
    for i, nota in enumerate(ranking_sistema):
        posicao = i + 1
        ganho = nota
        desconto = posicao
        contribuicao = ganho / desconto
        dcg_linear += contribuicao
        
        print(f"   Posição {posicao} (nota = {nota}):")
        print(f"      Ganho     = {nota}")
        print(f"      Desconto  = {posicao}")
        print(f"      Contribuição = {ganho} / {desconto} = {contribuicao:.4f}")
        print()
    
    print(f"   💡 DCG (sistema) = {dcg_linear:.4f}")
    
    print("\n🔢 PASSO 2: Calcular o IDCG (ranking ideal)\n")
    
    idcg_linear = 0.0
    for i, nota in enumerate(ranking_ideal):
        posicao = i + 1
        ganho = nota
        desconto = posicao
        contribuicao = ganho / desconto
        idcg_linear += contribuicao
        
        print(f"   Posição {posicao} (nota = {nota}):")
        print(f"      Ganho     = {nota}")
        print(f"      Desconto  = {posicao}")
        print(f"      Contribuição = {ganho} / {desconto} = {contribuicao:.4f}")
        print()
    
    print(f"   💡 IDCG (ideal) = {idcg_linear:.4f}")
    
    print("\n🔢 PASSO 3: Calcular o NDCG\n")
    
    ndcg_linear = dcg_linear / idcg_linear
    print(f"   NDCG = DCG / IDCG")
    print(f"   NDCG = {dcg_linear:.4f} / {idcg_linear:.4f}")
    print(f"   💡 NDCG = {ndcg_linear:.4f}")
    
    print(f"\n   📊 Interpretação: {ndcg_linear:.1%} do ranking ideal")
    if ndcg_linear >= 0.9:
        print(f"   ✅ Ranking excelente!")
    elif ndcg_linear >= 0.7:
        print(f"   ✅ Ranking bom!")
    elif ndcg_linear >= 0.5:
        print(f"   ⚠️  Ranking regular")
    else:
        print(f"   ❌ Ranking ruim")
    
    # ===== COMPARAÇÃO =====
    print("\n" + "="*80)
    print("COMPARAÇÃO ENTRE AS DUAS VERSÕES")
    print("="*80)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Versão Padrão:    NDCG = {ndcg_padrao:.4f}")
    print(f"   Versão Linear:    NDCG = {ndcg_linear:.4f}")
    print(f"   Diferença:               {ndcg_padrao - ndcg_linear:+.4f}")
    
    print(f"\n💡 POR QUE SÃO DIFERENTES?")
    print(f"   1. Desconto:")
    print(f"      • Padrão usa log₂(i+1), que decresce mais lentamente")
    print(f"      • Linear usa i, que decresce uniformemente")
    print(f"      • Compare: pos2 → padrão=1.585 vs linear=2.0")
    
    print(f"\n   2. Ganho:")
    print(f"      • Padrão usa 2^nota - 1, favorecendo notas altas")
    print(f"      • Linear usa nota diretamente")
    print(f"      • Compare: nota=2 → padrão=3 vs linear=2")
    
    print(f"\n   3. Efeito Combinado:")
    print(f"      • Padrão dá muito mais peso para docs muito relevantes no topo")
    print(f"      • Linear é mais 'justo' mas penaliza mais as posições baixas")
    
    if abs(ndcg_padrao - ndcg_linear) < 0.05:
        print(f"\n   ✅ Neste exemplo, as diferenças são pequenas")
        print(f"      Ambas as métricas avaliam o ranking de forma similar")
    else:
        print(f"\n   ⚠️  Neste exemplo, as diferenças são significativas")
        print(f"      A escolha da fórmula pode afetar a avaliação")
    
    print("\n" + "="*80)
    print("EXERCÍCIO PARA VOCÊ")
    print("="*80)
    print("\nTente modificar o ranking_sistema no código e observe:")
    print("1. O que acontece se você colocar o doc de nota 2 na posição 1?")
    print("2. Como ficaria o NDCG se o ranking fosse perfeito [2, 1, 1, 0]?")
    print("3. E se fosse o pior possível [0, 1, 1, 2]?")
    print("\nDica: Mude a linha 21 para experimentar!")
    print("="*80)


if __name__ == "__main__":
    exemplo_detalhado()
