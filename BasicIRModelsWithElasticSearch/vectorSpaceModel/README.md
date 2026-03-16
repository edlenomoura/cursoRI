# Vector Space Model (TF-IDF) com ElasticSearch 8.x+

Este diretório contém scripts para indexação e busca usando **TF-IDF de Salton (1971)** implementado via **SCRIPTED SIMILARITY** no ElasticSearch 8.x+.

## 🎯 Implementação Moderna

**Funciona com ElasticSearch 8.x+** usando scripted similarity!

### Por que Scripted Similarity?

O ElasticSearch 8.x **removeu** a similarity "classic" (TF-IDF tradicional). 

**Nossa solução didática**:
- ✅ Implementamos TF-IDF via **código Painless** (scripted similarity)
- ✅ Funciona no **ES 8.x+ moderno**
- ✅ Código TF-IDF **visível e editável**
- ✅ Fórmula de Salton **explícita no script**
- ✅ Didático: estudantes VÊM como o score é calculado

## 📚 Conceito: Vector Space Model de Salton

O **Modelo de Espaço Vetorial** (VSM) é um modelo clássico de recuperação de informação proposto por Gerard Salton nos anos 1970.

### Ideia Principal

- Documentos e consultas são representados como **vetores** em espaço multidimensional
- Cada dimensão representa um termo do vocabulário
- Peso de cada termo calculado por **TF-IDF**
- Similaridade medida pela fórmula de Salton

## 🔧 Implementação: Scripted Similarity

### Código Painless que Implementa TF-IDF

```painless
// TF (Term Frequency) - raiz quadrada da frequência
double tf = Math.sqrt(doc.freq);

// IDF (Inverse Document Frequency) - log do inverso
double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0;

// Normalização por tamanho do documento
double norm = 1.0 / Math.sqrt(doc.length);

// Score final: TF × IDF × norm × query boost
return query.boost * tf * idf * norm;
```

### Por que isso é Didático?

1. **Código Visível**: Estudantes VÊM exatamente como TF-IDF funciona
2. **Modificável**: Podem experimentar variações da fórmula
3. **Comparável**: Lado a lado com BM25 (caixa preta)
4. **Moderno**: Funciona no ES 8.x+ atual

### Componentes do TF-IDF

#### 1. TF (Term Frequency)
Frequência do termo no documento.

```
TF(t,d) = √(freq(t,d))
```

- Raiz quadrada da frequência no Lucene
- Termos mais frequentes têm maior peso
- **Problema**: crescimento linear favorece repetições excessivas

#### 2. IDF (Inverse Document Frequency)
Mede a raridade do termo no corpus.

```
IDF(t) = 1 + log(numDocs / (docFreq + 1))
```

- Termos raros têm maior peso
- Termos comuns (ex: "o", "de") têm peso menor
- Penaliza termos que aparecem em muitos documentos

#### 3. Normalização
Ajusta pelo tamanho do documento.

```
norm(d) = 1 / √(numTerms)
```

- Evita que documentos longos dominem resultados
- Normalização mais simples que BM25

#### 4. Score Final

```
score(q,d) = Σ [TF(t,d) × IDF(t) × norm(d)]
```

Soma dos produtos TF-IDF de cada termo da consulta.

## 🔄 TF-IDF vs BM25

| Aspecto | TF-IDF (Classic) | BM25 (Padrão ES) |
|---------|------------------|------------------|
| **Época** | Anos 1970 | Anos 1990 |
| **Base** | Modelo vetorial algébrico | Modelo probabilístico |
| **TF** | Crescimento contínuo (√freq) | Saturação (diminishing returns) |
| **Normalização** | Simples (1/√len) | Sofisticada (parâmetro b) |
| **Parâmetros** | Fixos | Ajustáveis (k1, b) |
| **Performance** | Boa | Geralmente melhor |
| **Intuição** | Mais simples | Mais complexa |
| **Uso** | Didático, clássico | Produção moderna |

### Exemplo Prático

**Consulta**: "responsabilidade civil"

**Doc1**: Contém "responsabilidade" 4x e "civil" 2x (documento longo)
**Doc2**: Contém "responsabilidade" 1x e "civil" 1x (documento curto)

**TF-IDF**: Favorece Doc1 (mais repetições = score maior)
**BM25**: Scores mais equilibrados (saturação de frequência)

## 📁 Arquivos

- **indexa.py** - Cria índice com similarity "classic" (TF-IDF)
- **buscaVSM.py** - Exemplos de buscas usando TF-IDF
- **requirements.txt** - Dependências Python

## 🚀 Uso

### 1. Iniciar ElasticSearch

```bash
cd ../BM25
./initElastic.sh
```

### 2. Instalar Dependências

```bash
cd ../vectorSpaceModel
pip install -r requirements.txt
```

### 3. Indexar com TF-IDF

```bash
python indexa.py
```

Cria o índice `ementas_tfidf` com similarity "classic".

### 4. Executar Buscas

```bash
python buscaVSM.py
```

Demonstra 5 tipos de busca + comparação com BM25.

## 🔬 Experimentação

### Comparar TF-IDF vs BM25

Os dois índices coexistem no mesmo ElasticSearch:

- **ementas_tfidf** → usa TF-IDF (classic)
- **ementas** → usa BM25 (padrão)

Execute a mesma consulta nos dois:

```bash
# TF-IDF
python buscaVSM.py

# BM25 
cd ../BM25
python busca.py
```

### Observações Esperadas

1. **Scores Absolutos**
   - TF-IDF: valores geralmente maiores
   - BM25: valores menores e mais controlados

2. **Ranking**
   - Pode diferir entre algoritmos
   - TF-IDF favorece documentos longos
   - BM25 é mais equilibrado

3. **Repetições**
   - TF-IDF: termo repetido 10x vs 5x = grande diferença
   - BM25: diferença menor (saturação)

## 📊 Configuração Técnica

### Mapeamento com Scripted Similarity (ES 8.x+)

```json
{
  "settings": {
    "similarity": {
      "tfidf_salton": {
        "type": "scripted",
        "script": {
          "source": "
            double tf = Math.sqrt(doc.freq);
            double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0;
            double norm = 1.0 / Math.sqrt(doc.length);
            return query.boost * tf * idf * norm;
          "
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "highlight": {
        "type": "text",
        "similarity": "tfidf_salton"
      }
    }
  }
}
```

### Como Funciona

**Em tempo de indexação**:
- Documentos são analisados e tokenizados
- Estatísticas são coletadas (freq, docFreq, docCount, length)

**Em tempo de busca**:
- Para cada termo da consulta em cada documento:
  1. Script Painless é executado
  2. Calcula TF, IDF, norm
  3. Retorna score parcial
- Scores de todos os termos são somados

### Parâmetros Disponíveis no Script

```painless
// Estatísticas do campo
field.docCount        // Total de documentos
field.sumDocFreq      // Soma de docFreqs
field.sumTotalTermFreq // Soma de termFreqs

// Estatísticas do termo
term.docFreq          // Docs que contêm o termo
term.totalTermFreq    // Total de ocorrências

// Estatísticas do documento
doc.freq              // Frequência neste doc
doc.length            // Tamanho do campo

// Parâmetros da consulta
query.boost           // Peso da consulta
```

### Tipos de Similarity no ElasticSearch

- **BM25** (padrão): Okapi BM25, estado da arte
- **scripted**: **Qualquer função via Painless** ⬅️ O que usamos!
- **boolean**: Apenas verifica presença (sem score)
- **DFR**: Divergence from Randomness
- **DFI**: Divergence from Independence
- **IB**: Information-Based models
- **LM Dirichlet**: Language Model com suavização Dirichlet
- **LM Jelinek Mercer**: Language Model Jelinek-Mercer

**Nota**: `classic` (TF-IDF tradicional) foi removido no ES 8.0.

## 🎓 Exercícios Sugeridos

### Nível Básico
1. Execute `indexa.py` e `buscaVSM.py`
2. Compare scores com `../BM25/busca.py`
3. Observe quais documentos aparecem em posições diferentes

### Nível Intermediário
4. Modifique uma consulta para repetir termos
5. Compare impacto em TF-IDF vs BM25
6. Teste com documentos longos vs curtos

### Nível Avançado
7. **Experimente variações do script Painless**:
   - TF linear: `double tf = doc.freq;` (em vez de raiz)
   - TF logarítmico: `double tf = Math.log(1 + doc.freq);`
   - Sem normalização: remova `* norm`
   - IDF diferente: `Math.log(field.docCount / term.docFreq)`
8. Implemente métricas de avaliação (MAP, NDCG)
9. Compare performance com dataset maior

### 🔬 Experimentos com Scripted Similarity

Modifique o script em `indexa.py` para testar variações:

#### Variação 1: TF Linear (sem raiz)
```painless
double tf = doc.freq;  // Crescimento linear
double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0;
double norm = 1.0 / Math.sqrt(doc.length);
return query.boost * tf * idf * norm;
```

#### Variação 2: TF Logarítmico
```painless
double tf = Math.log(1 + doc.freq);  // Crescimento logarítmico
double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0;
double norm = 1.0 / Math.sqrt(doc.length);
return query.boost * tf * idf * norm;
```

#### Variação 3: Sem Normalização
```painless
double tf = Math.sqrt(doc.freq);
double idf = Math.log((field.docCount + 1.0) / (term.docFreq + 1.0)) + 1.0;
return query.boost * tf * idf;  // Sem norm - favorece docs longos
```

#### Variação 4: IDF Simples
```plainless
double tf = Math.sqrt(doc.freq);
double idf = Math.log(field.docCount / Math.max(1, term.docFreq));  // IDF mais simples
double norm = 1.0 / Math.sqrt(doc.length);
return query.boost * tf * idf * norm;
```

**Exercício**: Implemente cada variação, reindexe, e compare os resultados!

## 📖 Referências

### Papers Clássicos
- Salton, G. (1971). "The SMART Retrieval System"
- Salton & Buckley (1988). "Term Weighting Approaches in Automatic Text Retrieval"

### Documentação
- [Lucene TFIDFSimilarity](https://lucene.apache.org/core/8_0_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html)
- [ElasticSearch Similarity Module](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html)
- [Vector Space Model - Wikipedia](https://en.wikipedia.org/wiki/Vector_space_model)

### Comparações
- [BM25 vs TF-IDF](https://kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm-25/)
- [Information Retrieval Book - Manning et al.](https://nlp.stanford.edu/IR-book/)

## 🔧 Troubleshooting

### Índice não encontrado
```
❌ Índice 'ementas_tfidf' não encontrado!
```
**Solução**: Execute `python indexa.py` primeiro.

### ElasticSearch não está rodando
```
❌ ElasticSearch não está rodando!
```
**Solução**: Execute `../BM25/initElastic.sh`

### Comparação com BM25 falha
```
⚠ Índice BM25 não encontrado
```
**Solução**: Execute `cd ../BM25 && python indexa.py`

## 💡 Quando Usar Cada Algoritmo

### Use TF-IDF quando:
- ✅ Fins didáticos e educacionais
- ✅ Simplicidade é prioridade
- ✅ Trabalha com corpus pequeno
- ✅ Implementação própria de IR

### Use BM25 quando:
- ✅ Produção e aplicações reais
- ✅ Performance é importante
- ✅ Documentos de tamanhos variados
- ✅ Usando ElasticSearch (já é padrão)

## 🎯 Objetivos de Aprendizado

Após usar estes scripts, você deve ser capaz de:

1. ✅ Explicar componentes do TF-IDF (TF, IDF, normalização)
2. ✅ Entender diferenças entre TF-IDF e BM25
3. ✅ Configurar similarity customizada no ElasticSearch
4. ✅ Comparar resultados de diferentes algoritmos de ranking
5. ✅ Escolher algoritmo apropriado para seu caso de uso
6. ✅ Interpretar scores e avaliar relevância

---

**Nota**: Este material foi criado para fins educacionais. Para aplicações em produção, considere usar BM25 (padrão do ElasticSearch) que geralmente oferece melhor performance.
