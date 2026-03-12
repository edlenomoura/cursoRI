# Word2Vec - Vetorização com CBOW e Skip-gram

Demonstração de vetorização de texto usando Word2Vec com comparação entre os algoritmos CBOW e Skip-gram.

## O que é Word2Vec?

Word2Vec é um algoritmo de aprendizado de máquina que transforma palavras em vetores numéricos (embeddings). Palavras com significados similares ficam próximas no espaço vetorial.

## Características

- **Vetores estáticos** - Mesma palavra sempre tem o mesmo vetor
- **Treinamento rápido** - Treina do zero com seu corpus
- **Leve** - ~MB de recursos
- **Dimensões configuráveis** - Exemplo usa 10 dimensões

## Instalação

Este projeto possui seu próprio ambiente virtual Python (venv) para garantir isolamento de dependências.

### Ativando o ambiente virtual

```bash
# No diretório word2vec
source venv/bin/activate
```

### Instalando dependências (caso necessário)

```bash
pip install -r requirements.txt
```

## Como executar

```bash
# Com o ambiente virtual ativado
python word2vec_demo.py
```

## Desativando o ambiente virtual

```bash
deactivate
```

## O que o programa faz

1. **Pré-processa texto** - Remove pontuação e tokeniza 5 sentenças
2. **Treina dois modelos** - CBOW (sg=0) e Skip-gram (sg=1)
3. **Mostra vetores** - Compara vetores de ambos algoritmos para cada palavra
4. **Calcula similaridades** - Encontra palavras semanticamente similares
5. **Salva modelos** - Gera `word2vec_cbow.bin` e `word2vec_skipgram.bin`

## Parâmetros principais

- **vector_size=10**: Dimensão dos vetores (configurável)
- **window=3**: Janela de contexto (3 palavras antes e depois)
- **min_count=1**: Mantém todas as palavras (bom para corpus pequeno)
- **sg=0/1**: Algoritmo CBOW (0) ou Skip-gram (1)
- **epochs=100**: Número de iterações de treinamento

## Diferenças CBOW vs Skip-gram

### CBOW (Continuous Bag of Words)
- Prevê palavra alvo a partir do contexto
- Mais rápido
- Melhor para palavras frequentes

### Skip-gram
- Prevê contexto a partir da palavra alvo
- Melhor para palavras raras
- Captura relações semânticas mais sutis
- Recomendado para corpus pequenos

## Arquivos gerados

- `word2vec_cbow.bin` - Modelo CBOW treinado
- `word2vec_skipgram.bin` - Modelo Skip-gram treinado

## Melhor para

- Busca de documentos similares
- Clustering de palavras
- Recomendação baseada em conteúdo
- Análise de similaridade semântica
