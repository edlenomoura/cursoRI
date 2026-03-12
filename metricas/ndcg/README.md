# Calculadora de NDCG - Métricas de Recuperação de Informação

Este projeto demonstra como calcular o **NDCG (Normalized Discounted Cumulative Gain)** usando **duas fórmulas diferentes**, permitindo uma compreensão didática das variações desta importante métrica para avaliar sistemas de recuperação de informação e ranking.

## 📚 O que é NDCG?

O **NDCG** é uma métrica que avalia a qualidade de um ranking de documentos, levando em consideração:

1. **Relevância dos documentos**: Documentos mais relevantes devem estar melhor posicionados
2. **Posição no ranking**: Documentos relevantes em posições mais altas contribuem mais para o score
3. **Normalização**: O resultado é normalizado entre 0 e 1, facilitando a comparação entre sistemas

## 🔬 Duas Versões de Cálculo

Este programa implementa e compara **duas variações** da fórmula de NDCG:

### 1️⃣ Versão Padrão (Literatura Acadêmica)

**Fórmula:**
```
DCG = Σ((2^rel_i - 1) / log₂(i+1))
```

**Características:**
- ✅ Mais comum na literatura acadêmica
- ✅ Desconto logarítmico: penaliza menos posições intermediárias
- ✅ Ganho exponencial: dá muito mais peso para notas altas (2^rel - 1)
- ✅ Recomendada para comparações com outros trabalhos

**Exemplo prático:**
- Ranking: [nota=2, nota=1, nota=0, nota=1]
- Cálculo:
  - Pos 1: (2²-1) / log₂(2) = 3 / 1.0 = 3.000
  - Pos 2: (2¹-1) / log₂(3) = 1 / 1.585 = 0.631
  - Pos 3: (2⁰-1) / log₂(4) = 0 / 2.0 = 0.000
  - Pos 4: (2¹-1) / log₂(5) = 1 / 2.322 = 0.431
- **DCG = 4.062**

### 2️⃣ Versão Linear (Simplificada)

**Fórmula:**
```
DCG = Σ(rel_i / i)
```

**Características:**
- ✅ Mais simples de calcular e entender
- ✅ Desconto linear: penaliza uniformemente todas as posições
- ✅ Ganho direto: peso proporcional à nota de relevância
- ✅ Útil para fins didáticos e quando se quer penalização uniforme

**Exemplo prático:**
- Ranking: [nota=2, nota=1, nota=0, nota=1]
- Cálculo:
  - Pos 1: 2 / 1 = 2.000
  - Pos 2: 1 / 2 = 0.500
  - Pos 3: 0 / 3 = 0.000
  - Pos 4: 1 / 4 = 0.250
- **DCG = 2.750**

### 🔍 Principais Diferenças

| Aspecto | Versão Padrão | Versão Linear |
|---------|---------------|---------------|
| **Desconto** | Logarítmico (1/log₂(i+1)) | Linear (1/i) |
| **Ganho** | Exponencial (2^rel - 1) | Direto (rel) |
| **Valores DCG** | Geralmente maiores | Geralmente menores |
| **Sensibilidade** | Muito sensível a notas altas | Proporcional às notas |
| **Penalização** | Menos agressiva em posições intermediárias | Mais uniforme |
| **Uso** | Literatura e benchmarks | Didática e casos específicos |

### 📊 Comparação de Resultados

No exemplo dos sistemas fornecidos:

**Sistema 1:**
- NDCG Padrão: 0.7404
- NDCG Linear: 0.7068
- Diferença: +0.0337

**Sistema 2:**
- NDCG Padrão: 0.8011
- NDCG Linear: 0.7762
- Diferença: +0.0249

**Conclusão:** Ambas as métricas concordam que Sistema 2 é melhor! ✅

## 📂 Estrutura dos Arquivos

```
metricas/
├── calcula_ndcg.py          # Programa principal (compara dois sistemas)
├── exemplo_calculo_manual.py # Tutorial passo a passo com um exemplo simples
├── README.md                 # Este arquivo
└── sampleFiles/
    ├── query_scores.json     # Avaliações de relevância (ground truth)
    ├── sistema1.json         # Resultados do Sistema 1
    └── sistema2.json         # Resultados do Sistema 2
```

### Formato dos Arquivos JSON

**query_scores.json** - Contém as avaliações de relevância (0, 1 ou 2):
```json
{
  "search_queries": [
    {
      "query": "exemplo de consulta",
      "results": [
        { "doc_id": 123, "nota": 2 },
        { "doc_id": 456, "nota": 1 }
      ]
    }
  ]
}
```

**sistema1.json / sistema2.json** - Contém os resultados retornados:
```json
{
  "search_queries": [
    {
      "query": "exemplo de consulta",
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

Avalia dois sistemas completos e compara as duas versões do NDCG:

```bash
python calcula_ndcg.py
```

### Exemplo Didático (Cálculo Passo a Passo)

Para entender exatamente como funciona o cálculo, execute o exemplo simplificado:

```bash
python exemplo_calculo_manual.py
```

Este programa mostra cada passo do cálculo de forma detalhada, ideal para quem está aprendendo. Você pode modificar o ranking no código (linha 21) para experimentar com diferentes cenários.

## 📊 Saída do Programa

O programa exibe:

1. **Introdução explicando as duas versões da fórmula**

2. **Para cada consulta de cada sistema:**
   - Lista de documentos com suas notas
   - Documentos não avaliados (ignorados)
   - Comparação entre ranking real e ideal
   - **Valores usando a versão PADRÃO** (DCG, IDCG, NDCG)
   - **Valores usando a versão LINEAR** (DCG, IDCG, NDCG)
   - **Análise das diferenças** entre as duas versões

3. **Resumo por sistema** mostrando NDCG médio em ambas as versões

4. **Comparação final** entre os sistemas com:
   - Resultados de ambas as versões
   - Análise de concordância entre as métricas
   - Diferenças nos valores absolutos
   - Interpretação didática das diferenças
   - Orientações sobre quando usar cada versão

5. **Tabela comparativa** mostrando resultados por consulta de forma estruturada

### Exemplo de Saída

```
Consulta 3: receita de pão de fermentação natural
--------------------------------------------------------------------------------
  Documento 3341: nota = 2
  Documento 4412: nota = 1
  Documento 1109: nota = 1
  Documento 6720: nota = 0

  Notas no ranking do sistema: [2, 1, 1, 0]
  Notas ordenadas idealmente: [2, 1, 1, 0]

  📊 VERSÃO PADRÃO: DCG = Σ((2^rel_i - 1) / log₂(i+1))
     DCG  = 4.1309
     IDCG = 4.1309
     NDCG = 1.0000  ← Ranking perfeito!

  📊 VERSÃO LINEAR: DCG = Σ(rel_i / i)
     DCG  = 2.8333
     IDCG = 2.8333
     NDCG = 1.0000  ← Ranking perfeito!

  🔍 DIFERENÇAS:
     Diferença NDCG: +0.0000 (padrão - linear)
     Diferença DCG:  +1.2976 (valores absolutos)
     → Rankings muito similares nas duas métricas
```

### Tabela Comparativa Final

```
📋 COMPARAÇÃO DETALHADA POR CONSULTA:
Consulta   S1-Padrão    S1-Linear    S2-Padrão    S2-Linear    Observação
--------------------------------------------------------------------------------
1          0.8045       0.7941       0.7003       0.7059       
2          0.5213       0.4000       0.5213       0.4000       ≈ Similares
3          0.7579       0.7647       1.0000       1.0000       
4          0.9871       0.9750       0.9871       0.9750       ≈ Similares
5          0.6313       0.6000       0.7967       0.8000       
```

## 🔍 Entendendo os Resultados

No exemplo fornecido:

**Com Versão Padrão:**
- **Sistema 1**: NDCG médio = 0.7404
- **Sistema 2**: NDCG médio = 0.8011 ✓ (melhor)

**Com Versão Linear:**
- **Sistema 1**: NDCG médio = 0.7068
- **Sistema 2**: NDCG médio = 0.7762 ✓ (melhor)

**Conclusão:** Ambas as métricas concordam que o Sistema 2 é melhor!

### Análise por Consulta

| Consulta | S1-Padrão | S1-Linear | S2-Padrão | S2-Linear | Melhor |
|----------|-----------|-----------|-----------|-----------|--------|
| 1        | 0.8045    | 0.7941    | 0.7003    | 0.7059    | Sistema 1 |
| 2        | 0.5213    | 0.4000    | 0.5213    | 0.4000    | Empate |
| 3        | 0.7579    | 0.7647    | 1.0000    | 1.0000    | Sistema 2 ✓ |
| 4        | 0.9871    | 0.9750    | 0.9871    | 0.9750    | Empate |
| 5        | 0.6313    | 0.6000    | 0.7967    | 0.8000    | Sistema 2 ✓ |

O Sistema 2 teve um ranking **perfeito** (NDCG = 1.0) na consulta 3 em ambas as versões!

## 🎓 Conceitos Importantes

### Por que duas versões de desconto?

**Desconto Logarítmico (versão padrão):**
- `1/log₂(i+1)` diminui mais lentamente
- A diferença entre posição 1 e 2 é grande, mas entre 10 e 11 é pequena
- Reflete melhor o comportamento real dos usuários
- Exemplo: pos1→1.0, pos2→0.63, pos3→0.50, pos10→0.30

**Desconto Linear (versão simplificada):**
- `1/i` diminui uniformemente
- Penaliza mais pesadamente posições mais baixas
- Mais simples de entender e calcular
- Exemplo: pos1→1.0, pos2→0.50, pos3→0.33, pos10→0.10

### Por que duas versões de ganho?

**Ganho Exponencial (versão padrão): `2^rel - 1`**
- Dá peso desproporcional a documentos muito relevantes
- nota=0 → ganho=0, nota=1 → ganho=1, nota=2 → ganho=3, nota=3 → ganho=7
- Enfatiza a importância de ter documentos altamente relevantes no topo
- Usado na maioria dos papers acadêmicos

**Ganho Direto (versão linear): `rel`**
- Proporcional à nota de relevância
- nota=0 → ganho=0, nota=1 → ganho=1, nota=2 → ganho=2, nota=3 → ganho=3
- Mais intuitivo e direto
- Útil quando todas as notas devem ter peso proporcional

### Quando as versões concordam?

As duas versões geralmente **concordam na ordem final** dos sistemas quando:
- As diferenças de qualidade são claras
- Os rankings têm padrões consistentes
- Há documentos relevantes bem posicionados

As versões podem **discordar** quando:
- As diferenças são muito sutis
- Há trade-offs específicos (ex: muitos docs moderadamente relevantes vs poucos muito relevantes)
- Os sistemas têm estratégias de ranking muito diferentes

### Interpretação dos valores NDCG

Ambas as versões normalizam para [0, 1], mas os valores absolutos diferem:

| Faixa | Versão Padrão | Versão Linear | Interpretação |
|-------|---------------|---------------|---------------|
| 0.9-1.0 | Excelente | Excelente | Ranking quase perfeito |
| 0.7-0.9 | Bom | Muito bom | Ranking de qualidade |
| 0.5-0.7 | Regular | Regular | Precisa melhorar |
| 0.0-0.5 | Ruim | Ruim | Ranking inadequado |

### Tratamento de documentos não avaliados

Documentos sem avaliação são **ignorados** nos cálculos em ambas as versões, como se não existissem no ranking. Esta é uma abordagem conservadora que evita penalizar ou beneficiar sistemas por documentos não avaliados.

## 🛠️ Modificações Possíveis

### Usar apenas uma versão do NDCG

Se quiser avaliar com apenas uma das versões, substitua `avaliar_sistema_comparativo` por `avaliar_sistema` em `main()`:

```python
# Para usar apenas a versão padrão
ndcgs_sistema1, ndcg_medio_sistema1 = avaliar_sistema(
    "SISTEMA 1", 
    arquivo_sistema1, 
    mapa_relevancia
)
```

### Calcular NDCG@k

Para avaliar apenas os top-k resultados, modifique as chamadas passando o parâmetro `k`:

```python
# Avaliar apenas os 3 primeiros resultados
(ndcgs_s1_padrao, ndcg_medio_s1_padrao, 
 ndcgs_s1_linear, ndcg_medio_s1_linear) = avaliar_sistema_comparativo(
    "SISTEMA 1", 
    arquivo_sistema1, 
    mapa_relevancia,
    k=3  # ← Adicione este parâmetro
)
```

### Visualização detalhada do cálculo

Descomente as linhas de debug nas funções `calcular_dcg` e `calcular_dcg_linear` (linhas ~104 e ~165) para ver a contribuição de cada posição:

```python
# Em calcular_dcg (linha ~104)
print(f"  Posição {posicao}: nota={nota}, ganho={ganho:.2f}, desconto={desconto:.2f}, contribuição={ganho/desconto:.4f}")

# Em calcular_dcg_linear (linha ~165)
print(f"  Posição {posicao}: nota={nota}, ganho={ganho:.2f}, desconto={desconto:.2f}, contribuição={ganho/desconto:.4f}")
```

Isso produzirá saída detalhada como:
```
Posição 1: nota=2, ganho=3.00, desconto=1.00, contribuição=3.0000
Posição 2: nota=1, ganho=1.00, desconto=1.58, contribuição=0.6309
```

### Implementar outras variações

Você pode criar suas próprias variações experimentando com:

**Outros descontos:**
- Quadrático: `1 / (i²)`
- Raiz quadrada: `1 / sqrt(i)`
- Personalizado: `1 / (1 + i*0.5)`

**Outras funções de ganho:**
- Cúbico: `2^(2*rel) - 1`
- Simplesmente quadrado: `rel²`
- Com threshold: `rel if rel >= 2 else 0`

## 📖 Referências

- Järvelin, K., & Kekäläinen, J. (2002). "Cumulated gain-based evaluation of IR techniques". ACM TOIS.
- [Wikipedia: Discounted cumulative gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)

## 👨‍🎓 Para Estudantes

Este código foi desenvolvido com propósito didático. Recomendo:

### Experimentos Sugeridos

1. **Comparar as duas versões**
   - Execute o programa e observe as diferenças
   - Analise quando as métricas concordam e quando divergem
   - Pense sobre qual versão faz mais sentido para seu caso de uso

2. **Modificar os dados**
   - Altere os arquivos JSON dos sistemas
   - Inverta a ordem de alguns documentos
   - Observe o impacto no NDCG de ambas as versões

3. **Testar edge cases**
   - O que acontece com ranking perfeito? (já temos um exemplo!)
   - O que acontece com ranking completamente invertido?
   - E se todos os documentos tiverem nota 0?

4. **Calcular NDCG@k**
   - Teste com k=1, k=2, k=3
   - Compare NDCG@3 vs NDCG@10
   - Quando faz diferença considerar apenas os top-k?

5. **Analisar situações específicas**
   - Quando a versão padrão dá score maior?
   - Quando a versão linear é mais favorável?
   - Por que documento muito relevante em pos 2 afeta tanto a versão padrão?

6. **Implementar outras métricas**
   - Precision@k
   - MAP (Mean Average Precision)
   - MRR (Mean Reciprocal Rank)
   - Compare todas elas!

### Questões para Reflexão

1. Por que o Sistema 2 foi melhor em ambas as versões?
2. Na consulta 2, qual sistema teve o ranking mais problemático? Por quê?
3. Se você tivesse que escolher apenas uma versão do NDCG, qual escolheria? Por quê?
4. Como você explicaria a diferença entre as duas versões para alguém sem formação técnica?
5. Em que situação a escolha da fórmula poderia mudar a conclusão sobre qual sistema é melhor?

### Desafios Avançados

1. **Implementar NDCG com outras escalas de relevância**
   - Usar escala de 0-4 em vez de 0-2
   - Adaptar as fórmulas

2. **Criar visualizações**
   - Gráficos comparando as duas versões
   - Heatmaps de NDCG por consulta

3. **Análise estatística**
   - Calcular significância estatística das diferenças
   - Usar testes como t-test pareado

4. **Otimização**
   - E se você pudesse reordenar apenas 2 documentos do Sistema 1?
   - Quais reordenações dariam maior ganho de NDCG?

Divirta-se aprendendo sobre métricas de RI! 🚀
