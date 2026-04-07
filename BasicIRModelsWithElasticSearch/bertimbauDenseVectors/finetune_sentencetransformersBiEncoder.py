from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 1. Carrega o BERTimbau base
model = SentenceTransformer('neuralmind/bert-base-portuguese-cased')

# 2. Formato de Treino (Anchor, Positive, Negative)
train_examples = [
    InputExample(texts=['O que é citar?', 'Citação é o ato pelo qual...', 'A maçã é uma fruta...']),
    # Adicione milhares aqui...
]