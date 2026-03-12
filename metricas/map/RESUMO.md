# 📊 Resumo: Calculadora de MAP (Mean Average Precision)

## ✅ O que foi criado

Implementação didática completa do cálculo de MAP para avaliar sistemas de recuperação de informação usando **relevância binária**.

## 📁 Arquivos Criados no Diretório `map/`

### 1. **calcula_map.py** - Programa Principal
**Funcionalidades:**
- ✅ Converte notas graduadas (0, 1, 2) em binário (0 = irrelevante, >0 = relevante)
- ✅ Calcula Precision@k para cada posição
- ✅ Calcula Average Precision (AP) por consulta
- ✅ Calcula MAP (média dos APs)
- ✅ Compara Sistema 1 vs Sistema 2
- ✅ Mostra cálculo detalhado para cada consulta
- ✅ Análise por consulta e interpretação dos resultados
- ✅ Código extremamente comentado

**Execução:**
```bash
cd map
python calcula_map.py
```

### 2. **exemplo_calculo_manual.py** - Tutorial Interativo
**Funcionalidades:**
- ✅ Exemplo com ranking de 8 documentos
- ✅ Mostra CADA PASSO do cálculo
- ✅ Explica Precision@k em cada posição relevante
- ✅ Demonstra cálculo do AP
- ✅ Compara com ranking perfeito e ruim
- ✅ Exemplo de MAP com múltiplas consultas
- ✅ Explica diferenças entre MAP e NDCG
- ✅ Exercícios sugeridos

**Execução:**
```bash
cd map
python exemplo_calculo_manual.py
```

### 3. **README.md** - Documentação Completa
**Conteúdo:**
- ✅ Explicação detalhada do MAP
- ✅ Comparação MAP vs NDCG
- ✅ Fórmulas e exemplos passo a passo
- ✅ Interpretação dos valores
- ✅ Conceitos importantes (P@k, AP, MAP)
- ✅ Modificações possíveis
- ✅ Exercícios e desafios para estudantes
- ✅ Quando usar MAP vs NDCG

## 🎯 Principais Características

### Fórmulas Implementadas

#### Precision@k
```
P@k = (documentos relevantes até posição k) / k
```

#### Average Precision (AP)
```
AP = Σ(P@k × rel(k)) / total_de_relevantes

onde rel(k) = 1 se posição k tem doc relevante, 0 caso contrário
```

#### Mean Average Precision (MAP)
```
MAP = Σ AP(q) / número_de_consultas
```

### Conversão de Notas

O programa usa os **mesmos arquivos JSON** do NDCG, mas converte as notas:

```
Nota original → Relevância binária
     0        →        0 (irrelevante)
     1        →        1 (relevante)
     2        →        1 (relevante)
```

## 📊 Exemplo de Cálculo

### Entrada
```
Ranking: [1, 0, 1, 1, 0]
         (R, I, R, R, I)
```

### Cálculo Passo a Passo

```
Posição 1: RELEVANTE → P@1 = 1/1 = 1.000 ✓
Posição 2: irrelevante (não conta)
Posição 3: RELEVANTE → P@3 = 2/3 = 0.667 ✓
Posição 4: RELEVANTE → P@4 = 3/4 = 0.750 ✓
Posição 5: irrelevante (não conta)

Precisões coletadas: [1.000, 0.667, 0.750]
Total de relevantes: 3
AP = (1.000 + 0.667 + 0.750) / 3 = 0.806
```

### Interpretação
- **AP = 0.806** significa 80.6% de eficiência
- Documentos relevantes estão bem posicionados
- Sistema faz um bom trabalho

## 🔍 MAP vs NDCG: Comparação Rápida

| Aspecto | MAP | NDCG |
|---------|-----|------|
| **Relevância** | Binária (0/1) | Graduada (0,1,2,...) |
| **Todos docs iguais?** | Sim | Não, docs mais relevantes valem mais |
| **Desconto** | Implícito via precisão | Logarítmico explícito |
| **Melhor para** | Relevância sim/não | Múltiplos níveis |
| **Interpretação** | Mais intuitiva | Mais sofisticada |

## 💡 Quando Usar MAP?

### Use MAP quando:
- ✅ Relevância é naturalmente binária
- ✅ Todos documentos relevantes têm igual importância
- ✅ Você quer métrica simples de entender
- ✅ Precisa comparar com trabalhos que usam MAP

### Use NDCG quando:
- ✅ Há diferentes graus de relevância
- ✅ Docs muito relevantes devem pesar mais
- ✅ Você quer desconto logarítmico sofisticado

### Use AMBOS quando:
- ✅ Quer análise robusta
- ✅ Precisa validar conclusões
- ✅ Quer perspectivas complementares

## 🎓 Valor Pedagógico

### Para Iniciantes
- ✅ Conceito mais simples que NDCG
- ✅ Fácil de calcular manualmente
- ✅ Interpretação intuitiva
- ✅ Bom ponto de partida para métricas de RI

### Para Intermediários
- ✅ Entender trade-offs entre métricas
- ✅ Comparar com NDCG no mesmo dataset
- ✅ Análise de quando métricas concordam/divergem

### Para Avançados
- ✅ Base para outras métricas (R-Precision, etc)
- ✅ Fundamento para curvas Precision-Recall
- ✅ Extensível para variações (interpolated MAP, etc)

## 📖 Estrutura do Código

### calcula_map.py
```
main()
  ↓
carregar_json() → Lê arquivos
  ↓
criar_mapa_relevancia() → Converte notas para binário
  ↓
avaliar_sistema() → Para cada sistema
  ↓
  └─ Para cada consulta:
       calcular_precision_at_k() → P@1, P@2, ...
       calcular_average_precision() → AP
  ↓
calcular_map() → Média dos APs
```

### Principais Funções

1. **calcular_precision_at_k(relevancia, k)**
   - Calcula P@k
   - Entrada: lista de 0s e 1s, posição k
   - Saída: precisão até k

2. **calcular_average_precision(relevancia)**
   - Calcula AP para uma consulta
   - Entrada: lista de 0s e 1s (ordem do ranking)
   - Saída: AP entre 0 e 1

3. **calcular_map(lista_aps)**
   - Calcula MAP
   - Entrada: lista de APs
   - Saída: MAP (média simples)

## 🚀 Como Começar

### 1. Entender o Conceito
```bash
python exemplo_calculo_manual.py
```
Veja o cálculo passo a passo com exemplo simples.

### 2. Executar nos Dados Reais
```bash
python calcula_map.py
```
Avalie os dois sistemas com os dados do NDCG.

### 3. Comparar com NDCG
```bash
cd ../ndcg
python calcula_ndcg.py
cd ../map
python calcula_map.py
```
Compare os resultados: as métricas concordam?

### 4. Experimentar
- Modifique os JSONs em `../ndcg/sampleFiles/`
- Troque ordem de documentos
- Observe impacto no MAP
- Compare com impacto no NDCG

## 📊 Saída Esperada

### Exemplo de Saída (resumida)

```
================================================================================
CALCULADORA DE MAP - Sistema de Recuperação de Informação
================================================================================

📖 MAP (Mean Average Precision):
   • Métrica que avalia rankings usando classificação binária
   • Relevante (1) ou Irrelevante (0)
   • Considera a posição dos documentos relevantes
   
⚙️  Conversão de notas:
   • Nota = 0 → Irrelevante (0)
   • Nota > 0 → Relevante (1)

================================================================================
AVALIANDO SISTEMA 1
================================================================================

Consulta 1: melhores práticas para agricultura regenerativa
  Posição 1: Doc 4829 → RELEVANTE
  Posição 2: Doc 7732 → RELEVANTE
  Posição 3: Doc 3190 → irrelevante
  Posição 4: Doc 1054 → RELEVANTE

  Vetor de relevâncias: [1, 1, 0, 1]
  ⭐ Average Precision (AP) = 0.9444

  📝 Cálculo detalhado:
     Posição 1 (relevante): P@1 = 1.0000
     Posição 2 (relevante): P@2 = 1.0000
     Posição 4 (relevante): P@4 = 0.7500
     AP = 2.7500 / 3 = 0.9444

[... outras consultas ...]

================================================================================
MAP DO SISTEMA 1: 0.8XXX
================================================================================

[Sistema 2...]

🏆 COMPARAÇÃO FINAL
MAP Sistema 1: 0.8XXX
MAP Sistema 2: 0.8XXX
```

## ✨ Próximos Passos Sugeridos

1. Executar ambos programas (MAP e NDCG) e comparar
2. Analisar se as métricas concordam sobre qual sistema é melhor
3. Investigar consultas onde as métricas divergem
4. Experimentar com modificações nos rankings
5. Implementar outras métricas (MRR, P@k, Recall@k)
6. Criar visualizações (curvas Precision-Recall)

## 🔗 Arquivos Relacionados

- **Dados de entrada**: `../ndcg/sampleFiles/*.json`
- **Programa NDCG**: `../ndcg/calcula_ndcg.py`
- **Documentação NDCG**: `../ndcg/README.md`

---

**Projeto Didático de Métricas de Recuperação de Informação**  
*MAP implementado em Março 2026*
