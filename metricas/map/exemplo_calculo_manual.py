"""
Exemplo Didático: Cálculo Manual do MAP Passo a Passo

Este programa mostra em detalhes como calcular o MAP (Mean Average Precision)
com um exemplo simples e todos os passos explicados.

Ideal para estudantes que querem entender exatamente como funciona cada cálculo.
"""


def exemplo_detalhado():
    """
    Demonstra o cálculo completo do MAP com um exemplo simples.
    """
    print("="*80)
    print("EXEMPLO DIDÁTICO: CÁLCULO MANUAL DO MAP")
    print("="*80)
    
    # Exemplo: ranking retornado por um sistema
    # 1 = relevante, 0 = irrelevante
    ranking_sistema = [1, 0, 1, 1, 0, 1, 0, 0]
    
    print("\n📋 SITUAÇÃO:")
    print(f"   Um sistema retornou 8 documentos para uma consulta.")
    print(f"   A relevância (avaliada por especialistas) de cada documento:")
    print()
    for pos, rel in enumerate(ranking_sistema, 1):
        status = "RELEVANTE ✓" if rel == 1 else "irrelevante"
        print(f"   Posição {pos}: {status}")
    
    print(f"\n   Vetor de relevâncias: {ranking_sistema}")
    
    # Conta documentos relevantes
    total_relevantes = sum(ranking_sistema)
    print(f"   Total de documentos relevantes: {total_relevantes}")
    
    # ===== CÁLCULO DO AVERAGE PRECISION =====
    print("\n" + "="*80)
    print("CÁLCULO DO AVERAGE PRECISION (AP)")
    print("="*80)
    
    print("\n📖 CONCEITO:")
    print("   AP mede a qualidade do ranking considerando:")
    print("   1. A precisão em cada posição onde há um doc relevante")
    print("   2. A posição dos docs relevantes (quanto mais cedo, melhor)")
    
    print("\n🔢 PASSO 1: Calcular Precision@k para cada posição com doc relevante\n")
    
    precisoes = []
    posicoes_relevantes = []
    
    for k in range(1, len(ranking_sistema) + 1):
        # Conta quantos relevantes existem até a posição k
        relevantes_ate_k = sum(ranking_sistema[:k])
        
        # Calcula Precision@k
        precision_k = relevantes_ate_k / k
        
        # Se o documento na posição k é relevante, guardamos essa precisão
        if ranking_sistema[k - 1] == 1:
            precisoes.append(precision_k)
            posicoes_relevantes.append(k)
            
            print(f"   Posição {k}: RELEVANTE")
            print(f"      Documentos relevantes até aqui: {relevantes_ate_k}")
            print(f"      Total de documentos até aqui: {k}")
            print(f"      P@{k} = {relevantes_ate_k}/{k} = {precision_k:.4f} ✓")
            print()
        else:
            print(f"   Posição {k}: irrelevante (não conta no AP)")
    
    print(f"\n   💡 Posições com documentos relevantes: {posicoes_relevantes}")
    print(f"   💡 Precisões correspondentes: {[f'{p:.4f}' for p in precisoes]}")
    
    print("\n🔢 PASSO 2: Calcular a média das precisões\n")
    
    soma_precisoes = sum(precisoes)
    average_precision = soma_precisoes / total_relevantes
    
    print(f"   Soma das precisões = {' + '.join([f'{p:.4f}' for p in precisoes])}")
    print(f"                      = {soma_precisoes:.4f}")
    print()
    print(f"   AP = Soma / Total de relevantes")
    print(f"   AP = {soma_precisoes:.4f} / {total_relevantes}")
    print(f"   💡 AP = {average_precision:.4f}")
    
    # ===== INTERPRETAÇÃO =====
    print("\n" + "="*80)
    print("INTERPRETAÇÃO DO RESULTADO")
    print("="*80)
    
    print(f"\n📊 AP = {average_precision:.4f} ({average_precision*100:.1f}%)")
    
    if average_precision >= 0.9:
        print("   ✅ Excelente! Ranking quase perfeito")
    elif average_precision >= 0.7:
        print("   ✅ Muito bom! A maioria dos relevantes está bem posicionada")
    elif average_precision >= 0.5:
        print("   ⚠️  Regular. Há espaço para melhorar o posicionamento")
    else:
        print("   ❌ Ruim. Documentos relevantes estão mal posicionados")
    
    print(f"\n💡 O QUE ESSE VALOR SIGNIFICA?")
    print(f"   • Os documentos relevantes aparecem em média na posição 'boa'")
    print(f"   • Quanto mais cedo aparecem os relevantes, maior o AP")
    print(f"   • AP = 1.0 só é possível se todos os relevantes vierem primeiro")
    
    # ===== COMPARAÇÃO COM OUTROS RANKINGS =====
    print("\n" + "="*80)
    print("COMPARAÇÃO COM OUTROS RANKINGS POSSÍVEIS")
    print("="*80)
    
    # Ranking perfeito
    ranking_perfeito = [1, 1, 1, 1, 0, 0, 0, 0]  # Todos relevantes primeiro
    print(f"\n1️⃣  RANKING PERFEITO: {ranking_perfeito}")
    
    precisoes_perfeito = []
    for k in range(1, len(ranking_perfeito) + 1):
        if ranking_perfeito[k - 1] == 1:
            p_k = sum(ranking_perfeito[:k]) / k
            precisoes_perfeito.append(p_k)
            print(f"   Posição {k}: P@{k} = {p_k:.4f}")
    
    ap_perfeito = sum(precisoes_perfeito) / total_relevantes
    print(f"   AP perfeito = {ap_perfeito:.4f}")
    
    # Ranking ruim
    ranking_ruim = [0, 0, 0, 0, 1, 1, 1, 1]  # Todos relevantes no final
    print(f"\n2️⃣  RANKING RUIM: {ranking_ruim}")
    
    precisoes_ruim = []
    for k in range(1, len(ranking_ruim) + 1):
        if ranking_ruim[k - 1] == 1:
            p_k = sum(ranking_ruim[:k]) / k
            precisoes_ruim.append(p_k)
            print(f"   Posição {k}: P@{k} = {p_k:.4f}")
    
    ap_ruim = sum(precisoes_ruim) / total_relevantes
    print(f"   AP ruim = {ap_ruim:.4f}")
    
    # Comparação
    print(f"\n3️⃣  NOSSO RANKING: {ranking_sistema}")
    print(f"   AP = {average_precision:.4f}")
    
    print(f"\n📊 COMPARATIVO:")
    print(f"   Melhor possível: {ap_perfeito:.4f}")
    print(f"   Nosso ranking:   {average_precision:.4f} ({average_precision/ap_perfeito*100:.1f}% do ideal)")
    print(f"   Pior caso:       {ap_ruim:.4f}")
    
    # ===== MAP COM MÚLTIPLAS CONSULTAS =====
    print("\n" + "="*80)
    print("E SE HOUVER MÚLTIPLAS CONSULTAS? (MAP)")
    print("="*80)
    
    print("\n📖 CONCEITO:")
    print("   MAP = Mean Average Precision")
    print("   É simplesmente a MÉDIA dos APs de todas as consultas")
    
    # Exemplo com 3 consultas
    consulta1_ranking = [1, 0, 1, 1]
    consulta2_ranking = [0, 1, 0, 1]
    consulta3_ranking = [1, 1, 0, 0]
    
    print(f"\n💡 EXEMPLO COM 3 CONSULTAS:")
    print(f"\n   Consulta 1: {consulta1_ranking}")
    
    ap1_precisoes = []
    for k in range(1, len(consulta1_ranking) + 1):
        if consulta1_ranking[k - 1] == 1:
            p = sum(consulta1_ranking[:k]) / k
            ap1_precisoes.append(p)
    ap1 = sum(ap1_precisoes) / sum(consulta1_ranking)
    print(f"      Precisões: {[f'{p:.2f}' for p in ap1_precisoes]}")
    print(f"      AP₁ = {ap1:.4f}")
    
    print(f"\n   Consulta 2: {consulta2_ranking}")
    ap2_precisoes = []
    for k in range(1, len(consulta2_ranking) + 1):
        if consulta2_ranking[k - 1] == 1:
            p = sum(consulta2_ranking[:k]) / k
            ap2_precisoes.append(p)
    ap2 = sum(ap2_precisoes) / sum(consulta2_ranking)
    print(f"      Precisões: {[f'{p:.2f}' for p in ap2_precisoes]}")
    print(f"      AP₂ = {ap2:.4f}")
    
    print(f"\n   Consulta 3: {consulta3_ranking}")
    ap3_precisoes = []
    for k in range(1, len(consulta3_ranking) + 1):
        if consulta3_ranking[k - 1] == 1:
            p = sum(consulta3_ranking[:k]) / k
            ap3_precisoes.append(p)
    ap3 = sum(ap3_precisoes) / sum(consulta3_ranking)
    print(f"      Precisões: {[f'{p:.2f}' for p in ap3_precisoes]}")
    print(f"      AP₃ = {ap3:.4f}")
    
    map_score = (ap1 + ap2 + ap3) / 3
    print(f"\n   MAP = (AP₁ + AP₂ + AP₃) / 3")
    print(f"   MAP = ({ap1:.4f} + {ap2:.4f} + {ap3:.4f}) / 3")
    print(f"   💡 MAP = {map_score:.4f}")
    
    # ===== EXERCÍCIOS =====
    print("\n" + "="*80)
    print("EXERCÍCIO PARA VOCÊ")
    print("="*80)
    print("\nTente modificar o ranking_sistema no código (linha 21) e observe:")
    print("1. O que acontece se você colocar todos os relevantes no início?")
    print("2. Como fica o AP se os relevantes ficam intercalados [1,0,1,0,1,0,1,0]?")
    print("3. Qual é o pior ranking possível com 4 relevantes em 8 documentos?")
    print("\n💡 DICA IMPORTANTE:")
    print("   MAP valoriza sistemas que colocam documentos relevantes")
    print("   nas PRIMEIRAS posições, não apenas que os retornam!")
    
    print("\n" + "="*80)
    print("DIFERENÇA ENTRE MAP E NDCG")
    print("="*80)
    print("\n📚 MAP:")
    print("   • Usa classificação BINÁRIA (relevante ou não)")
    print("   • Todos os docs relevantes têm o mesmo peso")
    print("   • Sensível à ordem, mas não diferencia níveis de relevância")
    print("\n📚 NDCG:")
    print("   • Usa classificação GRADUADA (notas 0, 1, 2, ...)")
    print("   • Docs muito relevantes valem mais que moderadamente relevantes")
    print("   • Desconto logarítmico penaliza posições baixas")
    print("\n💡 QUANDO USAR CADA UM?")
    print("   • MAP: Quando relevância é binária (sim/não)")
    print("   • NDCG: Quando há diferentes níveis de relevância")
    
    print("="*80)


if __name__ == "__main__":
    exemplo_detalhado()
