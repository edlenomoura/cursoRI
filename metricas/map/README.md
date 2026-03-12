# Calculadora de MAP - Mean Average Precision

Este projeto demonstra como calcular o **MAP (Mean Average Precision)**, uma métrica fundamental para avaliar sistemas de recuperação de informação que usa **relevância binária** (relevante ou irrelevante).

## 📚 O que é MAP?

O **MAP (Mean Average Precision)** é uma métrica que avalia a qualidade de um ranking considerando:

1. **Posição dos documentos relevantes**: Quanto mais cedo aparecem, melhor
2. **Precisão em cada ponto relevante**: Qual proporção de documentos até ali é relevante
3. **Média entre consultas**: Consolida a performance em múltiplas buscas

### Diferença para o NDCG

| Característica | MAP | NDCG |
|----------------|-----|------|
| **Relevância** | Binária (0 ou 1) | Graduada (0, 1, 2, ...) |
| **Peso dos docs** | Todos iguais | Docs muito relevantes valem mais |
| **Desconto** | Implícito na precisão | Logarítmico explícito |
| **Uso** | Relevância sim/não | Múltiplos níveis de relevância |

### Conversão das Notas

Neste projeto, usamos os mesmos arquivos do NDCG, mas convertemos as notas:

```
Nota = 0  →  Irrelevante (0)
Nota > 0  →  Relevante (1)
```

## 🔬 Como Funciona o MAP?

### 1️⃣ Precision@k

Mede a precisão nos primeiros k documentos:

```
P@k = (número de docs relevantes nos primeiros k) / k
```

**Exemplo:**
- Ranking: [R, I, R, R, I]  (R=relevante, I=irrelevante)
- P@1 = 1/1 = 1.00
- P@2 = 1/2 = 0.50
- P@3 = 2/3 = 0.67
- P@4 = 3/4 = 0.75
- P@5 = 3/5 = 0.60

### 2️⃣ Average Precision (AP)

Média das precisões **apenas nas posições com documentos relevantes**:

```
AP = (Σ(P@k × rel(k))) / total_de_relevantes
```

Onde `rel(k)` é 1 se a posição k tem documento relevante, 0 caso contrário.

**Continuando o exemplo anterior:**
- Posições relevantes: 1, 3, 4
- AP = (1.00 + 0.67 + 0.75) / 3 = 0.806

### 3️⃣ Mean Average Precision (MAP)

Simplesmente a média dos APs de todas as consultas:

```
MAP = (Σ AP(q)) / número_de_consultas
```

## 📊 Exemplo Passo a Passo

### Ranking do Sistema

```
Posição 1: RELEVANTE   → P@1 = 1/1 = 1.000 ✓
Posição 2: irrelevante → (não conta)
Posição 3: RELEVANTE   → P@3 = 2/3 = 0.667 ✓
Posição 4: RELEVANTE   → P@4 = 3/4 = 0.750 ✓
Posição 5: irrelevante → (não conta)
```

### Cálculo do AP

```
Precisões nas posições relevantes: [1.000, 0.667, 0.750]
Total de relevantes: 3
AP = (1.000 + 0.667 + 0.750) / 3 = 0.806
```

### Interpretação

- **AP = 0.806** → Muito bom! (80.6% do ideal)
- Documentos relevantes aparecem cedo no ranking
- Sistema está fazendo um bom trabalho

## 📂 Estrutura dos Arquivos

```
map/
├── calcula_map.py           # Programa principal
├── exemplo_calculo_manual.py # Tutorial passo a passo
└── README.md                 # Este arquivo

(Usa os arquivos de ../ndcg/sampleFiles/)
```

### Arquivos de Dados (compartilhados com NDCG)

**query_scores.json** - Avaliações com notas graduadas:
```json
{
  "search_queries": [
    {
      "query": "exemplo",
      "results": [
        { "doc_id": 123, "nota": 2 },  // Convertido para relevante (1)
        { "doc_id": 456, "nota": 0 }   // Convertido para irrelevante (0)
      ]
    }
  ]
}
```

**sistema1.json / sistema2.json** - Rankings retornados:
```json
{
  "search_queries": [
    {
      "query": "exemplo",
      "results": [
        { "doc_id": 456 },
        { "doc_id": 123 }
      ]
    }
  ]
}
```

## 🚀 Como Executar

### Programa Principal (Comparação de Sistemas)

Avalia dois sistemas completos calculando o MAP:

```bash
python calcula_map.py
```

### Exemplo Didático (Cálculo Passo a Passo)

Para entender exatamente como funciona o cálculo:

```bash
python exemplo_calculo_manual.py
```

Este programa mostra cada passo do cálculo de forma detalhada, perfeito para aprender!

## 📊 Saída do Programa

O programa exibe:

1. **Conversão das notas** para relevância binária

2. **Para cada consulta de cada sistema:**
   - Lista de documentos com relevância binária
   - Vetor de relevâncias
   - Total de relevantes disponíveis vs retornados
   - Cálculo detalhado do AP
   - Precisões em cada posição relevante

3. **MAP de cada sistema**

4. **Comparação final** entre os sistemas

5. **Análise por consulta** em formato de tabela

6. **Interpretação didática** dos resultados

### Exemplo de Saída

```
Consulta 3: receita de pão de fermentação natural
--------------------------------------------------------------------------------
  Posição 1: Doc 3341 → RELEVANTE
  Posição 2: Doc 4412 → RELEVANTE
  Posição 3: Doc 1109 → RELEVANTE
  Posição 4: Doc 6720 → irrelevante

  Vetor de relevâncias: [1, 1, 1, 0]
  Total de relevantes disponíveis: 3
  Total de relevantes retornados: 3

  ⭐ Average Precision (AP) = 1.0000

  📝 Cálculo detalhado:
     Posição 1 (relevante): P@1 = 1.0000
     Posição 2 (relevante): P@2 = 1.0000
     Posição 3 (relevante): P@3 = 1.0000
     Soma das precisões = 3.0000
     AP = 3.0000 / 3 = 1.0000  ← Perfeito!
```

## 🔍 Entendendo os Resultados

### No Exemplo Fornecido

Com os mesmos dados do NDCG, mas usando MAP:

**Comparação dos Sistemas:**
- Sistema 1: MAP ≈ 0.7-0.8 (depende dos dados exatos)
- Sistema 2: MAP ≈ 0.8-0.9 (geralmente melhor)

### Interpretação dos Valores

| Faixa MAP | Qualidade | Interpretação |
|-----------|-----------|---------------|
| 0.9 - 1.0 | Excelente | Relevantes estão muito bem posicionados |
| 0.7 - 0.9 | Muito Bom | Boa colocação dos relevantes |
| 0.5 - 0.7 | Regular | Há espaço para melhorar |
| 0.3 - 0.5 | Ruim | Relevantes mal posicionados |
| 0.0 - 0.3 | Muito Ruim | Sistema precisa de revisão |

### Casos Especiais

- **AP = 1.0**: Todos os documentos relevantes vieram primeiro (ranking perfeito)
- **AP = 0.0**: Nenhum documento relevante foi retornado
- **AP baixo com muitos relevantes retornados**: Relevantes estão em posições ruins

## 🎓 Conceitos Importantes

### Por que usar Average Precision?

O AP captura dois aspectos importantes:

1. **Recall**: Quantos dos relevantes foram encontrados
2. **Ordem**: Em que posições eles aparecem

Exemplo: Retornar 10 relevantes nas posições 1-10 é melhor que nas posições 91-100!

### Diferença entre Precision@k e AP

**Precision@k:**
- Olha apenas para as primeiras k posições
- Valor único para cada k
- Exemplo: P@10 = 0.7

**Average Precision:**
- Considera todas as posições
- Dá mais peso para relevantes no início
- Resume o ranking inteiro em um número

### Por que "Average" no nome?

Porque fazemos média de duas formas:

1. **Dentro de uma consulta**: Média das precisões nas posições relevantes
2. **Entre consultas**: Média dos APs (isso produz o MAP)

### Sensibilidade à Ordem

MAP é **muito sensível** à posição dos relevantes:

```
Ranking A: [R, R, R, I, I]  →  AP = (1.0 + 1.0 + 1.0)/3 = 1.000
Ranking B: [I, I, R, R, R]  →  AP = (0.33 + 0.50 + 0.60)/3 = 0.476
```

Ambos retornam os mesmos 3 relevantes, mas A é muito melhor!

## 🛠️ Modificações Possíveis

### Calcular MAP@k

Para avaliar apenas os top-k resultados, modifique a função `calcular_average_precision`:

```python
def calcular_average_precision(relevancia_ordenada, k=None):
    if k is not None:
        relevancia_ordenada = relevancia_ordenada[:k]
    # ... resto do código
```

### Adicionar Interpolação

MAP interpolado (usado no TREC) calcula de forma ligeiramente diferente:

```python
def calcular_ap_interpolado(relevancia_ordenada):
    # Implementação do AP interpolado
    # Ver referências para detalhes
    pass
```

### Visualizar Curva Precision-Recall

```python
import matplotlib.pyplot as plt

def plotar_precision_recall(relevancia_ordenada):
    recalls = []
    precisions = []
    # ... calcular pontos
    plt.plot(recalls, precisions)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.show()
```

## 👨‍🎓 Para Estudantes

### Experimentos Sugeridos

1. **Comparar MAP com NDCG**
   - Execute ambos os programas
   - Compare os rankings dos sistemas
   - As métricas concordam sobre qual sistema é melhor?

2. **Testar ranking perfeito vs ruim**
   - Modifique os JSONs para criar ranking ideal
   - Crie ranking com relevantes no final
   - Observe como o MAP varia drasticamente

3. **Entender o impacto da posição**
   - Troque a posição de 2 documentos no ranking
   - Recalcule o MAP
   - Quanto mudou? Por quê?

4. **Análise de edge cases**
   - O que acontece se nenhum relevante é retornado?
   - E se todos retornados forem relevantes?
   - E se retornar poucos mas todos relevantes?

5. **Comparar com Precision@k**
   - Calcule P@5, P@10, P@20
   - Compare com o AP
   - Qual métrica é mais informativa?

### Questões para Reflexão

1. Por que MAP é melhor que apenas Precision@10?
2. Quando MAP seria preferível ao NDCG?
3. Como MAP trata documentos não avaliados?
4. É possível ter MAP alto com recall baixo?
5. Qual sistema você escolheria: alto MAP ou alta Precision@5?

### Desafios Avançados

1. **Implementar R-Precision**
   - Precision@R onde R = número de relevantes
   - Compare com MAP

2. **Calcular break-even point**
   - Ponto onde Precision = Recall
   - É sempre informativo?

3. **Análise de significância**
   - As diferenças de MAP são estatisticamente significativas?
   - Use testes como t-test pareado

4. **Otimização de ranking**
   - Dado um conjunto de docs, qual ordem maximiza MAP?
   - É diferente de maximizar NDCG?

## 📊 MAP vs NDCG: Quando Usar Cada Um?

### Use MAP quando:

✅ Relevância é naturalmente binária (documento responde à pergunta ou não)  
✅ Todos os documentos relevantes têm igual importância  
✅ Você quer métrica simples e interpretável  
✅ Tradição na sua área (ex: TREC usa muito MAP)  

### Use NDCG quando:

✅ Há diferentes níveis de relevância (perfeito, bom, ok, ruim)  
✅ Documentos muito relevantes devem pesar mais  
✅ Você quer métrica com desconto logarítmico  
✅ Necessita comparar com literatura que usa NDCG  

### Use ambos quando:

✅ Você quer análise completa  
✅ Avaliar se conclusões são robustas à escolha da métrica  
✅ Diferentes aspectos são importantes (binário vs graduado)  

## 📚 Referências

- Järvelin, K., & Kekäläinen, J. (2002). IR evaluation methods
- Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval
- TREC: Text REtrieval Conference - https://trec.nist.gov/
- Wikipedia: Information retrieval metrics

## ✨ Próximos Passos

Após dominar MAP e NDCG, considere estudar:

1. **P@k, R@k**: Métricas mais simples mas úteis
2. **MRR (Mean Reciprocal Rank)**: Para tarefas de "primeiro relevante"
3. **ERR (Expected Reciprocal Rank)**: Modelo probabilístico
4. **NDPM**: Variação do NDCG
5. **α-NDCG**: NDCG com fator de novidade

---

**Desenvolvido com propósito didático para o Curso de Recuperação de Informação**  
*Março 2026*
