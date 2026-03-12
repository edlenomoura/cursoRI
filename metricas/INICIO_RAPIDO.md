# 🚀 Guia de Início Rápido - Métricas de RI

## 📋 Checklist: O que você tem agora

✅ **Diretório NDCG** com:
- Programa principal calculando 2 versões do NDCG
- Exemplo didático passo a passo
- Documentação completa
- Arquivos de dados de exemplo

✅ **Diretório MAP** com:
- Programa principal calculando MAP
- Exemplo didático passo a passo  
- Documentação completa
- Usa os mesmos arquivos de dados

✅ **README principal** explicando toda a estrutura

## 🎯 Começo Rápido (5 minutos)

### 1. Entenda MAP com exemplo simples (2 min)

```bash
cd map
python exemplo_calculo_manual.py
```

**O que você verá:**
- Cálculo passo a passo de MAP
- Exemplo com 8 documentos
- Explicação de cada etapa
- Comparação com rankings perfeito e ruim

### 2. Entenda NDCG com exemplo simples (2 min)

```bash
cd ../ndcg
python exemplo_calculo_manual.py
```

**O que você verá:**
- Cálculo passo a passo de NDCG
- Duas versões (padrão e linear)
- Exemplo com 4 documentos
- Comparação entre as versões

### 3. Rode nos dados reais (1 min)

```bash
# MAP
cd ../map
python calcula_map.py

# NDCG
cd ../ndcg
python calcula_ndcg.py
```

## 📚 Roteiro de Estudo Sugerido

### Dia 1: MAP (Mais Simples)
1. ⏱️ 10 min: Leia `map/README.md` seções principais
2. ⏱️ 15 min: Execute `exemplo_calculo_manual.py` e entenda cada passo
3. ⏱️ 10 min: Execute `calcula_map.py` nos dados reais
4. ⏱️ 15 min: Faça exercício: calcule MAP manualmente no papel
5. ⏱️ 10 min: Modifique um ranking e veja o impacto

**Conceitos dominados:** ✓ Precision@k, ✓ AP, ✓ MAP

### Dia 2: NDCG (Mais Sofisticado)
1. ⏱️ 15 min: Leia `ndcg/README.md` sobre as duas versões
2. ⏱️ 15 min: Execute `exemplo_calculo_manual.py` 
3. ⏱️ 15 min: Execute `calcula_ndcg.py` nos dados reais
4. ⏱️ 15 min: Compare resultados NDCG padrão vs linear

**Conceitos dominados:** ✓ DCG, ✓ IDCG, ✓ NDCG, ✓ Variações

### Dia 3: Comparação
1. ⏱️ 20 min: Execute ambos programas lado a lado
2. ⏱️ 20 min: Compare: as métricas concordam?
3. ⏱️ 20 min: Analise consultas onde divergem

**Conceitos dominados:** ✓ Diferenças MAP/NDCG, ✓ Quando usar cada um

## 🎓 Para Professores

### Aula 1: Introdução ao MAP (50 min)

**Preparação:**
- Projete o output de `exemplo_calculo_manual.py`

**Plano:**
1. **10 min**: Apresente conceito de Precision@k
2. **15 min**: Execute exemplo passo a passo (projetar tela)
3. **10 min**: Calcule junto com turma no quadro
4. **10 min**: Discuta: por que posição importa?
5. **5 min**: Exercício: prever MAP de novo ranking

### Aula 2: Introdução ao NDCG (50 min)

**Preparação:**
- Já tendo visto MAP, introduza relevância graduada

**Plano:**
1. **10 min**: Limitação do MAP (só binário)
2. **15 min**: Apresente NDCG e suas duas versões
3. **15 min**: Execute exemplo comparativo
4. **10 min**: Discuta diferenças entre versões

### Aula 3: Comparação Prática (50 min)

**Preparação:**
- Execute ambos programas antes da aula

**Plano:**
1. **15 min**: Resultados MAP nos dois sistemas
2. **15 min**: Resultados NDCG nos dois sistemas
3. **15 min**: Discussão: métricas concordam?
4. **5 min**: Quando usar cada métrica?

## 🔥 Desafios Rápidos

### Desafio 1: Ranking Perfeito
🎯 **Objetivo:** Criar sistema3.json com MAP = 1.0

**Dica:** Todos relevantes devem vir primeiro

### Desafio 2: Divergência
🎯 **Objetivo:** Criar ranking onde MAP é alto mas NDCG baixo

**Dica:** Coloque docs nota=1 primeiro, note=2 depois

### Desafio 3: Otimização
🎯 **Objetivo:** Melhorar Sistema 1 trocando só 2 documentos

**Dica:** Qual troca dá maior ganho de MAP?

## 🐛 Troubleshooting

### Erro: "No module named 'json'"
**Solução:** Você está usando Python 3.6+? JSON é padrão.

### Erro: "File not found: sampleFiles"
**Solução:** Execute a partir do diretório `map/` ou `ndcg/`

```bash
cd map
python calcula_map.py  # ✅ correto
```

### Erro: "Permission denied"
**Solução:** Adicione permissão de execução

```bash
chmod +x calcula_map.py
```

### Output está truncado
**Solução:** Redirecione para arquivo

```bash
python calcula_map.py > resultados.txt
cat resultados.txt
```

## 📊 Interpretação Rápida de Resultados

### MAP

| Valor | Interpretação |
|-------|---------------|
| 0.9-1.0 | Excelente! Relevantes muito bem posicionados |
| 0.7-0.9 | Muito bom! Boa colocação dos relevantes |
| 0.5-0.7 | Regular. Há espaço para melhorar |
| 0.3-0.5 | Ruim. Relevantes mal posicionados |
| 0.0-0.3 | Muito ruim. Sistema precisa revisão |

### NDCG

| Valor | Interpretação |
|-------|---------------|
| 0.9-1.0 | Excelente! Ranking quase perfeito |
| 0.7-0.9 | Bom! Ranking de qualidade |
| 0.5-0.7 | Regular. Precisa melhorar |
| 0.0-0.5 | Ruim. Ranking inadequado |

## 🎯 Objetivos de Aprendizagem

Após completar este material, você será capaz de:

- [x] Explicar o que é MAP e como calculá-lo
- [x] Explicar o que é NDCG e suas variações
- [x] Calcular ambas métricas manualmente
- [x] Implementar em código
- [x] Escolher métrica apropriada para seu problema
- [x] Interpretar e comparar resultados
- [x] Entender trade-offs entre métricas

## 🚀 Próximos Passos

Depois de dominar MAP e NDCG:

1. **MRR (Mean Reciprocal Rank)**: Para "primeiro resultado útil"
2. **Precision@k e Recall@k**: Métricas simples mas importantes
3. **F1-score**: Balanceando precision e recall
4. **ERR (Expected Reciprocal Rank)**: Modelo probabilístico
5. **Curvas Precision-Recall**: Visualização completa

## 📞 Ajuda

Caso tenha dúvidas:

1. Leia os README.md detalhados
2. Execute os exemplos manuais linha por linha
3. Leia os comentários no código
4. Tente calcular no papel
5. Compare seu resultado com o do programa

## ✨ Bônus: One-liner Úteis

```bash
# Ver só os MAPs finais
python calcula_map.py | grep "MAP DO SISTEMA"

# Comparar MAP vs NDCG lado a lado
cd map && python calcula_map.py > ../map_results.txt && \
cd ../ndcg && python calcula_ndcg.py > ../ndcg_results.txt

# Contar quantos relevantes foram retornados
cat ../ndcg/sampleFiles/sistema1.json | grep doc_id | wc -l
```

---

**Boa sorte nos estudos! 🎓**

Lembre-se: a melhor forma de aprender é **fazendo**. Execute os programas, modifique os dados, calcule no papel, compare resultados!
