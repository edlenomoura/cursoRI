# 🎓 Curso de Recuperação de Informação - Exemplos Didáticos

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Repositório com exemplos práticos e didáticos para auxiliar no ensino de **Recuperação de Informação** (Information Retrieval). Contém implementações comentadas de métricas de avaliação e técnicas de vetorização de texto.

## 📚 Conteúdo

Este repositório está organizado em duas áreas principais:

### 1️⃣ Métricas de Avaliação ([`metricas/`](metricas/))

Implementações detalhadas das principais métricas para avaliar sistemas de recuperação de informação:

- **[NDCG](metricas/ndcg/)** (Normalized Discounted Cumulative Gain)
  - Relevância graduada (0, 1, 2, ...)
  - Duas implementações: padrão e linear
  - Exemplos de cálculo manual e automático
  
- **[MAP](metricas/map/)** (Mean Average Precision)
  - Relevância binária (0 ou 1)
  - Cálculo de precisão média
  - Exemplos práticos com múltiplas consultas

📖 **[Leia mais sobre métricas →](metricas/README.md)**

### 2️⃣ Vetorização de Texto ([`vetorizacao/`](vetorizacao/))

Demonstrações práticas de técnicas de vetorização para processamento de texto em português:

- **[Word2Vec](vetorizacao/word2vec/)** - Vetores estáticos
  - Comparação entre CBOW e Skip-gram
  - Treinamento do zero
  - Leve e rápido
  
- **[BERTimbau](vetorizacao/BERT/)** - Vetores contextualizados
  - BERT pré-treinado em português brasileiro
  - Embeddings contextualizados
  - Estado da arte em NLP

📖 **[Leia mais sobre vetorização →](vetorizacao/README.md)**

## 📂 Estrutura do Projeto

```
cursoRI/
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências globais
│
├── metricas/                    # Métricas de avaliação
│   ├── README.md
│   ├── INICIO_RAPIDO.md
│   ├── ndcg/                    # NDCG
│   │   ├── calcula_ndcg.py
│   │   ├── exemplo_calculo_manual.py
│   │   ├── README.md
│   │   ├── RESUMO.md
│   │   └── sampleFiles/
│   └── map/                     # MAP
│       ├── calcula_map.py
│       ├── exemplo_calculo_manual.py
│       ├── README.md
│       └── RESUMO.md
│
└── vetorizacao/                 # Vetorização de texto
    ├── README.md
    ├── word2vec/                # Word2Vec
    │   ├── word2vec_demo.py
    │   ├── requirements.txt
    │   └── README.md
    └── BERT/                    # BERTimbau
        ├── bertimbau_demo.py
        ├── requirements.txt
        └── README.md
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/cursoRI.git
   cd cursoRI
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

### Exemplos de Uso

#### Calculando NDCG:
```bash
cd metricas/ndcg
python calcula_ndcg.py
```

#### Calculando MAP:
```bash
cd metricas/map
python calcula_map.py
```

#### Testando Word2Vec:
```bash
cd vetorizacao/word2vec
pip install -r requirements.txt
python word2vec_demo.py
```

#### Testando BERTimbau:
```bash
cd vetorizacao/BERT
pip install -r requirements.txt
python bertimbau_demo.py
```

## 🎯 Objetivos Pedagógicos

Este material foi desenvolvido para:

- ✅ Demonstrar conceitos teóricos com exemplos práticos
- ✅ Fornecer código comentado e de fácil compreensão
- ✅ Permitir experimentação e modificação pelos alunos
- ✅ Servir como referência para implementações futuras

## 📖 Documentação

Cada diretório contém sua própria documentação detalhada:

- [Métricas - Guia Completo](metricas/README.md)
- [Métricas - Início Rápido](metricas/INICIO_RAPIDO.md)
- [NDCG - Documentação](metricas/ndcg/README.md)
- [MAP - Documentação](metricas/map/README.md)
- [Vetorização - Guia](vetorizacao/README.md)
- [Word2Vec - Documentação](vetorizacao/word2vec/README.md)
- [BERTimbau - Documentação](vetorizacao/BERT/README.md)

## 💡 Para Professores

Este material pode ser usado para:

- Demonstrações em sala de aula
- Exercícios práticos de laboratório
- Base para trabalhos e projetos
- Referência para provas e avaliações

Sinta-se livre para adaptar e modificar conforme necessário!

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você encontrou um erro, tem uma sugestão de melhoria ou quer adicionar novos exemplos:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaMetrica`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova métrica X'`)
4. Push para a branch (`git push origin feature/NovaMetrica`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📧 Contato

Para dúvidas, sugestões ou discussões sobre o material didático, abra uma [issue](../../issues) no GitHub.

---

**Nota:** Este é um projeto educacional. Os exemplos são simplificados para fins didáticos e podem não refletir as melhores práticas para sistemas de produção.

## O que cada programa faz

### word2vec_demo.py

1. **Lê um texto de exemplo** - Pequeno corpus sobre direito e justiça
2. **Pré-processa o texto** - Remove pontuação e tokeniza
3. **Treina dois modelos** - CBOW e Skip-gram
4. **Mostra os vetores** - Compara vetores de ambos os algoritmos
5. **Analisa similaridades** - Encontra palavras semanticamente similares
6. **Salva os modelos** - Persiste ambos os modelos treinados

### bertimbau_demo.py

1. **Carrega o BERTimbau** - Modelo pré-treinado em português
2. **Processa sentenças** - Tokeniza usando WordPiece
3. **Gera vetores contextualizados** - 768 dimensões por sentença
4. **Calcula similaridades** - Compara sentenças semanticamente
5. **Compara abordagens** - Explica diferenças entre Word2Vec e BERT

## Principais diferenças

| Característica | Word2Vec | BERTimbau |
|----------------|----------|-----------|
| Tipo de vetor | Estático | Contextualizado |
| Dimensões | 10-300 (configurável) | 768 (fixo) |
| Treinamento | Do zero | Pré-treinado |
| Tamanho | ~MB | ~400MB |
| Velocidade | Muito rápido | Mais lento |
| Melhor para | Similaridade simples | Tarefas complexas de NLP |

## Arquivos gerados

### Por word2vec_demo.py:
- `vetorizacao/word2vec/word2vec_cbow.bin`: Modelo CBOW treinado
- `vetorizacao/word2vec/word2vec_skipgram.bin`: Modelo Skip-gram treinado

### Por bertimbau_demo.py:
- Nenhum (usa modelo pré-treinado do Hugging Face)

## Otimização para GPU (opcional)

Se você tiver uma GPU NVIDIA, pode acelerar o BERTimbau:

```bash
# Desinstala torch CPU
pip uninstall torch

# Instala torch com CUDA (verifique sua versão do CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Exemplos de uso em produção

### Word2Vec:
- Busca de documentos similares
- Clustering de palavras
- Recomendação baseada em conteúdo

### BERTimbau:
- Classificação de textos jurídicos
- Análise de sentimento
- Perguntas e respostas
- Named Entity Recognition (NER)
