# BERTimbau - Vetorização Contextualizada

Demonstração de vetorização de sentenças usando BERTimbau, um modelo BERT pré-treinado em português brasileiro.

## O que é BERTimbau?

BERTimbau é uma versão do BERT (Bidirectional Encoder Representations from Transformers) treinada especificamente em português brasileiro. Diferente do Word2Vec, BERT gera vetores contextualizados.

## Características

- **Vetores contextualizados** - Mesma palavra pode ter diferentes vetores dependendo do contexto
- **Pré-treinado** - Não requer treinamento adicional
- **768 dimensões** - Vetores de alta dimensionalidade
- **~110 milhões de parâmetros**

## Requisitos de sistema

- **RAM**: 2-4GB disponível
- **Espaço em disco**: ~500MB (modelo + dependências)
- **CPU**: Recomendado 4+ cores (funciona em qualquer processador moderno)
- **GPU**: Opcional (acelera processamento, mas não é necessária)

## Instalação

Este projeto possui seu próprio ambiente virtual Python (venv) para garantir isolamento de dependências.

### Ativando o ambiente virtual

```bash
# No diretório BERT
source venv/bin/activate
```

### Instalando dependências (caso necessário)

```bash
pip install -r requirements.txt
```

**Nota**: Na primeira execução, o modelo será baixado automaticamente (~400MB).

## Como executar

```bash
# Com o ambiente virtual ativado
python bertimbau_demo.py
```

## Desativando o ambiente virtual

```bash
deactivate
```

## O que o programa faz

1. **Carrega BERTimbau** - Modelo `neuralmind/bert-base-portuguese-cased`
2. **Tokeniza sentenças** - Usa tokenização WordPiece (subpalavras)
3. **Gera vetores** - 768 dimensões por sentença usando token [CLS]
4. **Calcula similaridades** - Compara sentenças semanticamente
5. **Explica diferenças** - Compara Word2Vec vs BERT

## Estratégias de vetorização

O programa usa o **vetor [CLS]** como representação da sentença:
- Token [CLS] é adicionado no início de cada sentença
- BERT é treinado para que [CLS] represente a sentença toda
- Alternativa: pooling (média de todos os tokens)

## Exemplo de contextualização

Uma das principais vantagens do BERT é a contextualização:

```
Palavra: "banco"

Word2Vec: sempre o mesmo vetor

BERTimbau:
- "Sentei no banco da praça" → vetor A (mobiliário)
- "Fui ao banco sacar dinheiro" → vetor B (instituição financeira)
- A ≠ B (vetores diferentes!)
```

## Compatibilidade de versões

Este programa foi testado com:
- `transformers==4.40.2` (compatível com PyTorch 2.2.2)
- `torch<=2.2.2` (disponível no Nexus corporativo)
- `numpy<2.0.0` (NumPy 1.x para compatibilidade)

## Otimização GPU (opcional)

Se você tiver GPU NVIDIA com CUDA:

```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Melhor para

- Classificação de textos jurídicos
- Análise de sentimento
- Perguntas e respostas (Q&A)
- Named Entity Recognition (NER)
- Tarefas complexas de NLP em português
- Busca semântica de documentos

## Vantagens sobre Word2Vec

✅ Captura nuances contextuais  
✅ Pré-treinado em grande corpus  
✅ Estado da arte em NLP  
✅ Não requer corpus de treinamento  

## Desvantagens vs Word2Vec

❌ Mais lento (segundos vs milissegundos)  
❌ Requer mais memória (~400MB vs ~MB)  
❌ Maior complexidade computacional  

---

# 🚀 INTEGRAÇÃO COM ELASTICSEARCH

Esta seção documenta os scripts de **busca semântica** usando BERTimbau com ElasticSearch.

## 📁 Novos Arquivos

- **`indexaBertimbauElastic.py`**: Indexa documentos com embeddings do BERTimbau
- **`buscaBertimbauElastic.py`**: Busca semântica em 3 modos (kNN, Script Score, Híbrido)

## 🧠 Busca Semântica vs Léxica

### Busca Léxica (BM25, TF-IDF)
- Correspondência **exata** de palavras
- "carro" **não encontra** "automóvel"
- Rápida, mas limitada

### Busca Semântica (BERT)
- Baseada em **similaridade de significado**
- "carro" ≈ "automóvel" ≈ "veículo"
- Entende sinônimos, contexto, paráfrases

## 🏃 Início Rápido - Busca Semântica

### 1. Iniciar ElasticSearch

```bash
cd ../../BasicIRModelsWithElasticSearch/BM25
./initElastic.sh
```

### 2. Indexar com embeddings

```bash
python indexaBertimbauElastic.py
```

**O que faz:**
1. Carrega BERTimbau
2. Lê `../../dataSetExemplo/exEmentas.json`
3. Gera embeddings usando **token [CLS]**
4. Para textos longos (>512 tokens):
   - Divide em chunks de 500 tokens
   - Extrai CLS de cada chunk
   - Calcula **média dos embeddings**
5. Indexa como `dense_vector` (768 dimensões)

**Tempo:** ~5-10 minutos

### 3. Buscar semanticamente

```bash
python buscaBertimbauElastic.py
```

**Demonstra 3 tipos de busca:**
1. **kNN** - k-Nearest Neighbors (rápido, aproximado)
2. **Script Score** - Similaridade cosseno exata
3. **Híbrido** - Combina BM25 + BERT

## 🎯 Estratégia de Embeddings

### Token [CLS] para Sentenças

```
[CLS] Este é um texto [SEP]
  ↑
  └─ Representa toda a sentença (768 dims)
```

### Documentos Longos (>512 tokens)

```
Documento grande (2000 tokens)
    ↓
Dividir em chunks (500 tokens)
    ↓
chunk1 → [CLS] embed1
chunk2 → [CLS] embed2
chunk3 → [CLS] embed3
chunk4 → [CLS] embed4
    ↓
embedding_final = média(embed1, embed2, embed3, embed4)
```

## 📊 Tipos de Busca

### 1. kNN (k-Nearest Neighbors)

```python
# Rápido, aproximado, ideal para produção
busca_knn(es, consulta_embedding, k=10)
```

- ✅ Muito rápido (usa índice HNSW)
- ⚠️ Aproximado (não exato)
- ✅ Escalável para milhões de docs

### 2. Script Score

```python
# Exato, permite filtros
busca_script_score(es, consulta_embedding)
```

- ✅ Cosseno exato
- ✅ Combina com filtros
- ⚠️ Mais lento

### 3. Híbrido (BM25 + BERT)

```python
# Melhor dos dois mundos
busca_hibrida(es, texto, embedding, peso_lexico=0.5)
```

- ✅ Keywords exatas + significado
- ✅ Resultados superiores
- 📊 Ajuste pesos conforme caso

## 📈 Exemplo Comparativo

```
Consulta: "veículo automotor"

BM25 (Léxica):
  ✅ "veículo automotor"
  ✅ "veículo de transporte"  
  ❌ "automóvel usado" (não tem "veículo")

BERT (Semântica):
  ✅ "veículo automotor"
  ✅ "automóvel usado" (entende sinônimo)
  ✅ "carro particular" (conceito similar)
```

## 🎓 Quando Usar?

| Cenário | Recomendação |
|---------|-------------|
| Nomes próprios | BM25 |
| Termos técnicos exatos | BM25 |
| Sinônimos | BERT |
| Conceitos abstratos | BERT |
| Queries complexas | BERT |
| **Produção geral** | **Híbrido (50/50)** |

## ⚙️ Configurações

### indexaBertimbauElastic.py

```python
MAX_TOKENS_PER_CHUNK = 500  # Chunks para docs longos
campos_embedding = ['title', 'highlight']  # Campos indexados
EMBEDDING_DIMS = 768  # BERT base
```

### buscaBertimbauElastic.py

```python
k = 10  # Resultados kNN
num_candidates = 100  # Trade-off velocidade/qualidade
peso_lexico = 0.5  # Híbrido: 0.0=só BERT, 1.0=só BM25
```

## 🔧 Troubleshooting

### "CUDA out of memory"

```python
device = "cpu"  # Forçar CPU
```

### Busca lenta

1. Use **kNN** ao invés de Script Score
2. Aumente `num_candidates` gradualmente
3. Cache queries frequentes

### Resultados ruins

1. Ajuste `peso_lexico` na busca híbrida
2. Teste campos: `embedding_title` vs `embedding_highlight`
3. BERTimbau é específico para **português**

## 📚 Referências ElasticSearch

- [Dense Vectors](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html)
- [kNN Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [Script Score](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-score-query.html)

## 🎓 Exercícios

1. Compare busca "veículo" vs "carro"
2. Execute mesma query em índices BM25 e BERT
3. Ajuste pesos hibridos: teste 0.3, 0.5, 0.7
4. Teste queries em linguagem natural
5. Compare campos `title` vs `highlight`

---

**Para mais detalhes**, veja os comentários extensivos nos scripts Python!
