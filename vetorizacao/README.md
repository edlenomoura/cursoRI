# Vetorização de Texto - Exemplos Práticos

Este diretório contém programas demonstrativos de diferentes técnicas de vetorização de texto em português.

## 📁 Estrutura

```
vetorizacao/
├── venv_word2vec/         # Ambiente virtual com todas as dependências
├── word2vec/              # Programa Word2Vec (CBOW vs Skip-gram)
└── BERT/                  # Programa BERTimbau
```

## 🚀 Instalação (uma vez)

```bash
# Criar e ativar o ambiente virtual
python -m venv venv_word2vec
source venv_word2vec/bin/activate  # No Windows: venv_word2vec\Scripts\activate

# Instalar todas as dependências
pip install gensim transformers torch "numpy<2"
```

### [word2vec/](word2vec/) - Vetores Estáticos
Demonstração de Word2Vec com comparação entre CBOW e Skip-gram.

**Quick start:**
```bash
source venv_word2vec/bin/activate
cd word2vec
python word2vec_demo.py
```

**Ideal para:**
- Similaridade de palavras
- Clustering
- Análise rápida

---

### [BERT/](BERT/) - Vetores Contextualizados
Demonstração de BERTimbau (BERT em português brasileiro).

**Quick start:**
```bash
source venv_word2vec/bin/activate
cd BERT
python bertimbau_demo.py
```

**Ideal para:**
- Classificação de textos
- Análise de sentimento
- Busca semântica
- NER, Q&A

---

## 🔄 Comparação Rápida

| Característica | Word2Vec | BERTimbau |
|----------------|----------|-----------|
| Tipo | Estático | Contextualizado |
| Dimensões | 10-300 | 768 |
| Tamanho | ~MB | ~400MB |
| Velocidade | Muito rápido | Mais lento |
| Contexto | Não | Sim |
| Treinamento | Necessário | Pré-treinado |

## 📖 Documentação

Cada subdiretório contém seu próprio README com documentação detalhada:
- [word2vec/README.md](word2vec/README.md)
- [BERT/README.md](BERT/README.md)
