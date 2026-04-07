from sentence_transformers import CrossEncoder, InputExample
from torch.utils.data import DataLoader

# 1. Carrega o BERTimbau como Cross-Encoder
model = CrossEncoder('neuralmind/bert-base-portuguese-cased', num_labels=1)

# 2. Define os dados (Query, Documento, Score)
train_examples = [
    InputExample(texts=['O que é citar?', 'Citação é o ato pelo qual...'], label=1.0),
    InputExample(texts=['O que é citar?', 'A maçã é uma fruta...'], label=0.0) # Negativo
]

# 3. DataLoader otimizado para sua GPU
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)

# 4. Treino (Fit)
model.fit(train_dataloader=train_dataloader, epochs=1, evaluation_steps=100)