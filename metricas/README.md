# 📊 Métricas de Avaliação em Recuperação de Informação

Projeto didático com implementações detalhadas e comentadas das principais métricas para avaliar sistemas de recuperação de informação.

## 📂 Estrutura do Projeto

```
metricas/
├── README.md                    # Este arquivo (visão geral)
│
├── ndcg/                        # NDCG (Normalized Discounted Cumulative Gain)
│   ├── calcula_ndcg.py         # Programa principal (2 versões do NDCG)
│   ├── exemplo_calculo_manual.py
│   ├── README.md               # Documentação completa do NDCG
│   ├── RESUMO.md
│   └── sampleFiles/
│       ├── query_scores.json   # Avaliações de relevância (ground truth)
│       ├── sistema1.json       # Resultados do Sistema 1
│       └── sistema2.json       # Resultados do Sistema 2
│
└── map/                         # MAP (Mean Average Precision)
    ├── calcula_map.py          # Programa principal
    ├── exemplo_calculo_manual.py
    ├── README.md               # Documentação completa do MAP
    └── RESUMO.md
```

## 🎯 Métricas Implementadas

### 1️⃣ NDCG (Normalized Discounted Cumulative Gain)

**Diretório:** `ndcg/`

**Características:**
- ✅ Usa relevância **graduada** (notas: 0, 1, 2, ...)
- ✅ Documentos muito relevantes valem mais
- ✅ Desconto logarítmico por posição
- ✅ **Duas implementações**: versão padrão e versão linear

**Fórmulas:**
```
Versão Padrão:  DCG = Σ((2^rel_i - 1) / log₂(i+1))
Versão Linear:  DCG = Σ(rel_i / i)
NDCG = DCG / IDCG
```

**Quando usar:**
- Há diferentes níveis de relevância
- Docs muito relevantes devem ter peso maior
- Precisão em posições altas é crítica

### 2️⃣ MAP (Mean Average Precision)

**Diretório:** `map/`

**Características:**
- ✅ Usa relevância **binária** (0 = irrelevante, 1 = relevante)
- ✅ Todos docs relevantes têm peso igual
- ✅ Considera posição dos relevantes
- ✅ Fácil de interpretar

**Fórmulas:**
```
P@k = (relevantes até k) / k
AP = Σ(P@k × rel(k)) / total_relevantes
MAP = média dos APs
```

**Quando usar:**
- Relevância é naturalmente binária
- Todos relevantes têm igual importância
- Quer métrica simples e intuitiva

## 📊 Comparação Rápida: NDCG vs MAP

| Característica | NDCG | MAP |
|----------------|------|-----|
| **Tipo de relevância** | Graduada (0,1,2,...) | Binária (0,1) |
| **Peso dos docs** | Variável por relevância | Igual para todos |
| **Desconto posição** | Logarítmico explícito | Implícito via precisão |
| **Complexidade** | Mais sofisticado | Mais simples |
| **Interpretação** | Requer contexto | Mais intuitiva |
| **Uso acadêmico** | Muito comum | Muito comum |

## 🚀 Como Usar Este Projeto

### Para Aprender NDCG

```bash
cd ndcg

# 1. Comece com o exemplo simples
python exemplo_calculo_manual.py

# 2. Execute o programa completo
python calcula_ndcg.py

# 3. Leia o README.md
cat README.md
```

### Para Aprender MAP

```bash
cd map

# 1. Comece com o exemplo simples
python exemplo_calculo_manual.py

# 2. Execute o programa completo
python calcula_map.py

# 3. Leia o README.md
cat README.md
```

### Para Comparar as Métricas

```bash
# Execute NDCG
cd ndcg
python calcula_ndcg.py > ../resultados_ndcg.txt

# Execute MAP
cd ../map
python calcula_map.py > ../resultados_map.txt

# Compare os resultados
# Ambas concordam sobre qual sistema é melhor?
```

## 📚 Dados de Exemplo

Os programas usam os mesmos arquivos JSON (em `ndcg/sampleFiles/`):

### query_scores.json
Contém avaliações de relevância para 5 consultas:
- Agricultura regenerativa
- Criptografia quântica
- Pão de fermentação natural
- Pontos turísticos de Quioto
- Exercícios para lombar

**Formato:**
```json
{
  "query": "...",
  "results": [
    { "doc_id": 123, "nota": 2 }  // 0=irrelevante, 1=ok, 2=muito relevante
  ]
}
```

### sistema1.json e sistema2.json
Rankings retornados pelos sistemas para as mesmas 5 consultas.

**Conversão para MAP:**
- NDCG usa: nota original (0, 1, 2)
- MAP usa: nota > 0 → relevante (1), nota = 0 → irrelevante (0)

## 🎓 Valor Pedagógico

### Nível Iniciante
1. ✅ Comece pelo exemplo manual do MAP (mais simples)
2. ✅ Entenda Precision@k
3. ✅ Depois vá para o exemplo manual do NDCG
4. ✅ Entenda o conceito de desconto

### Nível Intermediário
1. ✅ Execute ambos programas principais
2. ✅ Compare os resultados
3. ✅ Analise quando concordam/divergem
4. ✅ Modifique os dados e observe mudanças

### Nível Avançado
1. ✅ Implemente variações (MAP@k, NDCG@k)
2. ✅ Adicione outras métricas (MRR, ERR)
3. ✅ Faça análise estatística
4. ✅ Crie visualizações

## 💡 Exercícios Sugeridos

### Exercício 1: Entender Individualmente
- Execute `exemplo_calculo_manual.py` de cada métrica
- Calcule manualmente no papel
- Verifique se chegou no mesmo resultado

### Exercício 2: Comparar Sistemas
- Execute ambos `calcula_*.py`
- As métricas concordam sobre qual sistema é melhor?
- Por quê ou por que não?

### Exercício 3: Modificar Rankings
- Edite `sistema1.json` ou `sistema2.json`
- Troque ordem de 2 documentos
- Recalcule: qual métrica mudou mais?

### Exercício 4: Ranking Perfeito
- Crie um sistema3.json com ranking ideal
- MAP = 1.0 e NDCG = 1.0?
- O que é necessário para isso?

### Exercício 5: Análise de Consulta
- Escolha uma consulta
- Sistema 1 é melhor em uma métrica, Sistema 2 em outra
- Por que as métricas discordam?

## 📖 Conceitos Abordados

### No NDCG
- [x] DCG (Discounted Cumulative Gain)
- [x] IDCG (Ideal DCG)
- [x] Normalização
- [x] Desconto logarítmico vs linear
- [x] Ganho exponencial vs linear
- [x] Trade-offs entre formulações

### No MAP
- [x] Precision@k
- [x] Average Precision (AP)
- [x] Mean Average Precision (MAP)
- [x] Relevância binária
- [x] Sensibilidade à ordem
- [x] Relação com curvas Precision-Recall

### Conceitos Gerais
- [x] Avaliação de rankings
- [x] Ground truth / gold standard
- [x] Métricas orientadas a posição
- [x] Trade-offs entre métricas
- [x] Quando usar cada métrica

## 🛠️ Extensões Possíveis

### Métricas Adicionais
- [ ] **MRR** (Mean Reciprocal Rank)
- [ ] **P@k** (Precision at k)
- [ ] **R@k** (Recall at k)
- [ ] **F1@k** (F1-score at k)
- [ ] **ERR** (Expected Reciprocal Rank)
- [ ] **RBP** (Rank-Biased Precision)

### Visualizações
- [ ] Gráficos de barra comparando sistemas
- [ ] Curvas Precision-Recall
- [ ] Heatmaps de performance por consulta
- [ ] Gráficos de DCG acumulado

### Análises Avançadas
- [ ] Testes de significância estatística
- [ ] Análise de correlação entre métricas
- [ ] Otimização de rankings
- [ ] Ensemble de sistemas

### Recursos Interativos
- [ ] Interface web (Streamlit/Flask)
- [ ] Jupyter notebooks
- [ ] Calculadora interativa
- [ ] Quiz sobre métricas

## 📚 Referências

### Artigos Fundamentais
- Järvelin, K., & Kekäläinen, J. (2002). "Cumulated gain-based evaluation of IR techniques"
- Manning, C. D., et al. (2008). "Introduction to Information Retrieval"
- Voorhees, E. M. (2001). "The Philosophy of Information Retrieval Evaluation"

### Recursos Online
- [Wikipedia: Evaluation measures (information retrieval)](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))
- [TREC: Text REtrieval Conference](https://trec.nist.gov/)
- [CLEF: Conference and Labs of the Evaluation Forum](https://www.clef-initiative.eu/)

### Livros
- "Information Retrieval" - C. D. Manning, P. Raghavan, H. Schütze
- "Search Engines: Information Retrieval in Practice" - W. B. Croft et al.
- "Modern Information Retrieval" - R. Baeza-Yates, B. Ribeiro-Neto

## 🤝 Contribuindo

Este é um projeto didático. Sugestões de melhorias:

1. **Novos exemplos**: Adicione casos de uso específicos
2. **Mais métricas**: Implemente MRR, ERR, etc.
3. **Visualizações**: Crie gráficos ilustrativos
4. **Traduções**: Ajude a traduzir comentários
5. **Exercícios**: Proponha novos desafios

## 📝 Licença

Projeto desenvolvido para fins educacionais.
Sinta-se livre para usar e adaptar para suas aulas e estudos.

## 👥 Autores

Desenvolvido como material didático para curso de Recuperação de Informação.

---

**Última atualização:** Março 2026

**Status:** ✅ Completo (NDCG e MAP implementados)

**Próximas adições planejadas:** MRR, Precision@k, Recall@k
