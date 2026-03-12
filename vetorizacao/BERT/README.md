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
