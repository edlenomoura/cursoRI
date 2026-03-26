"""
==============================================================================
 EMBEDDING DE PALAVRAS - VERSÃO LINEAR (SEM ReLU)
==============================================================================

DIFERENÇA em relação à versão com ReLU:
  - A camada escondida NÃO usa função de ativação (é linear)
  - O embedding é z1 = X·W1 + b1 diretamente, sem aplicar ReLU
  - Isso preserva valores negativos no embedding (representação mais rica)
  - Mais parecido com o que Word2Vec faz na prática

Vantagem: o embedding pode ter valores negativos, o que dá mais
expressividade à representação. Com ReLU, valores negativos viram 0,
perdendo informação.

Textos de entrada:
  - "manaus capital do amazonas"
  - "belém capital do para"
  - "curitiba capital do parana"
==============================================================================
"""

import numpy as np

np.random.seed(42)  # Mesma seed para comparação justa com a versão ReLU

# ==============================================================================
# PASSO 1: CONSTRUIR O VOCABULÁRIO
# ==============================================================================

print("=" * 70)
print("PASSO 1: CONSTRUIR O VOCABULÁRIO")
print("=" * 70)

sentencas = [
    "manaus capital do amazonas",
    "belém capital do para",
    "curitiba capital do parana"
]

print(f"\nSentenças de entrada:")
for i, s in enumerate(sentencas):
    print(f"  {i + 1}. \"{s}\"")

todas_palavras = []
for sentenca in sentencas:
    palavras = sentenca.lower().split()
    todas_palavras.extend(palavras)

print(f"\nTodas as palavras (com repetições): {todas_palavras}")
print(f"Total de palavras no texto: {len(todas_palavras)}")

vocabulario = []
for palavra in todas_palavras:
    if palavra not in vocabulario:
        vocabulario.append(palavra)

palavra_para_id = {palavra: idx for idx, palavra in enumerate(vocabulario)}
id_para_palavra = {idx: palavra for palavra, idx in palavra_para_id.items()}

tamanho_vocab = len(vocabulario)

print(f"\nVocabulário ({tamanho_vocab} palavras distintas):")
for palavra, idx in palavra_para_id.items():
    print(f"  ID {idx}: \"{palavra}\"")


# ==============================================================================
# PASSO 2: CRIAR VETORES DE CONTEXTO
# ==============================================================================

print("\n" + "=" * 70)
print("PASSO 2: CRIAR VETORES DE CONTEXTO")
print("=" * 70)

contagem = np.zeros((tamanho_vocab, tamanho_vocab), dtype=int)

print("\nAnalisando pares de palavras consecutivas:")
for sentenca in sentencas:
    palavras = sentenca.lower().split()
    for k in range(len(palavras) - 1):
        palavra_atual = palavras[k]
        proxima_palavra = palavras[k + 1]
        id_atual = palavra_para_id[palavra_atual]
        id_proxima = palavra_para_id[proxima_palavra]
        contagem[id_atual][id_proxima] += 1
        print(f"  \"{palavra_atual}\" (ID {id_atual}) aparece antes de "
              f"\"{proxima_palavra}\" (ID {id_proxima})")

print(f"\nMatriz de contagem ({tamanho_vocab} x {tamanho_vocab}):")
print(f"  Linhas = palavra vetorizada | Colunas = palavra seguinte")

header = "          "
for j in range(tamanho_vocab):
    header += f"{id_para_palavra[j]:>10}"
print(f"\n{header}")
print("  " + "-" * (10 + tamanho_vocab * 10))

for i in range(tamanho_vocab):
    linha = f"  {id_para_palavra[i]:>8}|"
    for j in range(tamanho_vocab):
        linha += f"{contagem[i][j]:>10}"
    print(linha)

vetores_contexto = contagem.astype(float)

print(f"\nVetores de contexto resultantes:")
for i in range(tamanho_vocab):
    print(f"  \"{id_para_palavra[i]}\" → {vetores_contexto[i].tolist()}")


# ==============================================================================
# PASSO 3: CONSTRUIR A REDE NEURAL (AUTOENCODER LINEAR)
# ==============================================================================
# DIFERENÇA PRINCIPAL: Nesta versão, a camada escondida é LINEAR.
# Não há função de ativação (ReLU) entre a entrada e a camada escondida.
#
#   [entrada N dims] → [W1] → [4 neurônios LINEARES] → [W2] → [saída N dims]
#                               ↑
#                         EMBEDDING (4 dims)
#                    (pode ter valores negativos!)
#
# Na versão com ReLU:  embedding = max(0, X·W1 + b1)  ← valores negativos viram 0
# Nesta versão:        embedding = X·W1 + b1           ← valores negativos preservados

print("\n" + "=" * 70)
print("PASSO 3: CONSTRUIR A REDE NEURAL (AUTOENCODER LINEAR)")
print("=" * 70)

tamanho_embedding = 4

print(f"\nArquitetura da rede:")
print(f"  Camada de entrada:  {tamanho_vocab} neurônios (1 por palavra do vocabulário)")
print(f"  Camada escondida:   {tamanho_embedding} neurônios LINEAR (será o embedding)")
print(f"  Camada de saída:    {tamanho_vocab} neurônios (reconstrução do vetor)")
print(f"\n  ⚠️  SEM função de ativação ReLU na camada escondida!")
print(f"  O embedding é z1 = X·W1 + b1 diretamente.")
print(f"  Valores negativos são PRESERVADOS no embedding.")
print(f"\n  Total de conexões entrada→escondida: {tamanho_vocab} × {tamanho_embedding} = {tamanho_vocab * tamanho_embedding}")
print(f"  Total de conexões escondida→saída:   {tamanho_embedding} × {tamanho_vocab} = {tamanho_embedding * tamanho_vocab}")

W1 = np.random.randn(tamanho_vocab, tamanho_embedding) * 0.1
b1 = np.zeros(tamanho_embedding)
W2 = np.random.randn(tamanho_embedding, tamanho_vocab) * 0.1
b2 = np.zeros(tamanho_vocab)

print(f"\n  Pesos W1 (entrada→escondida): matriz {W1.shape}")
print(f"  Bias b1:  vetor {b1.shape}")
print(f"  Pesos W2 (escondida→saída):  matriz {W2.shape}")
print(f"  Bias b2:  vetor {b2.shape}")


# --- Propagação direta (forward pass) ---

def forward(X):
    """
    Calcula a saída da rede para um vetor de entrada X.

    VERSÃO LINEAR - Fluxo:
      1. z1 = X · W1 + b1        (combinação linear = EMBEDDING direto!)
      2. z2 = z1 · W2 + b2       (combinação linear na camada de saída)
      3. saida = z2               (saída linear)

    Diferença da versão ReLU: NÃO aplica ReLU em z1.
    O embedding é z1 diretamente, podendo ter valores negativos.
    """
    z1 = X @ W1 + b1       # Camada escondida LINEAR (= embedding!)
    # SEM ReLU aqui! Na versão anterior: a1 = relu(z1)
    z2 = z1 @ W2 + b2      # Camada de saída
    saida = z2
    return z1, z2, saida


# --- Treinamento ---

print("\n" + "=" * 70)
print("PASSO 4: TREINAR A REDE (BACKPROPAGATION)")
print("=" * 70)

X_treino = vetores_contexto
Y_alvo = vetores_contexto

taxa_aprendizado = 0.001
epocas = 5000

print(f"\n  Dados de treino: {X_treino.shape[0]} palavras, cada uma com vetor de {X_treino.shape[1]} dimensões")
print(f"  Taxa de aprendizado: {taxa_aprendizado}")
print(f"  Épocas de treinamento: {epocas}")
print(f"\n  Objetivo: aprender pesos que minimizem o erro entre entrada e saída")
print(f"  A camada escondida de {tamanho_embedding} neurônios COMPRIME a informação")
print(f"  → Os valores dessa camada (SEM ReLU) são os EMBEDDINGS das palavras!\n")

historico_erro = []

for epoca in range(epocas):
    # --- Forward pass ---
    z1, z2, saida = forward(X_treino)

    # --- Calcular o erro (MSE) ---
    erro = Y_alvo - saida
    mse = np.mean(erro ** 2)
    historico_erro.append(mse)

    # --- Backward pass (backpropagation) ---
    # DIFERENÇA: sem ReLU, o gradiente passa direto pela camada escondida.
    # Não precisamos multiplicar pela derivada da ReLU.

    n_amostras = X_treino.shape[0]

    # Gradiente da saída
    d_saida = -2 * erro / n_amostras  # (N_palavras x N_vocab)

    # Gradientes da camada de saída (escondida → saída)
    dW2 = z1.T @ d_saida              # (4 x N_vocab)  ← usa z1 em vez de a1
    db2 = np.sum(d_saida, axis=0)     # (N_vocab,)

    # Gradiente propagado para a camada escondida
    # SEM multiplicar por relu_derivada! O gradiente flui livremente.
    d_z1 = d_saida @ W2.T             # (N_palavras x 4)

    # Gradientes da camada de entrada (entrada → escondida)
    dW1 = X_treino.T @ d_z1           # (N_vocab x 4)
    db1 = np.sum(d_z1, axis=0)        # (4,)

    # --- Atualizar pesos (gradient descent) ---
    W1 -= taxa_aprendizado * dW1
    b1 -= taxa_aprendizado * db1
    W2 -= taxa_aprendizado * dW2
    b2 -= taxa_aprendizado * db2

    # Mostrar progresso a cada 500 épocas
    if epoca % 500 == 0 or epoca == epocas - 1:
        print(f"  Época {epoca:>5}/{epocas} | Erro (MSE): {mse:.6f}")


# ==============================================================================
# PASSO 5: EXTRAIR OS EMBEDDINGS
# ==============================================================================
# O embedding agora é z1 (pré-ativação), que PRESERVA valores negativos.

print("\n" + "=" * 70)
print("PASSO 5: EXTRAIR OS EMBEDDINGS (RESULTADO FINAL)")
print("=" * 70)

print(f"\nPara cada palavra, o embedding é o vetor de {tamanho_embedding} dimensões")
print(f"produzido pela camada escondida LINEAR (z1 = X·W1 + b1).")
print(f"Valores negativos são preservados (diferente da versão com ReLU).\n")

embeddings_final, _, saida_final = forward(X_treino)

print(f"{'Palavra':<12} | {'Vetor Original':<45} | {'Embedding ({0} dims)'.format(tamanho_embedding)}")
print("-" * 85)

for i in range(tamanho_vocab):
    palavra = id_para_palavra[i]
    vetor_original = vetores_contexto[i].tolist()
    embedding = embeddings_final[i]
    embedding_str = "[" + ", ".join(f"{v:.4f}" for v in embedding) + "]"
    print(f"{palavra:<12} | {str(vetor_original):<45} | {embedding_str}")


# ==============================================================================
# PASSO 6: VERIFICAR A QUALIDADE (RECONSTRUÇÃO)
# ==============================================================================

print("\n" + "=" * 70)
print("PASSO 6: VERIFICAR A RECONSTRUÇÃO")
print("=" * 70)
print("\nComparação entre o vetor original e o reconstruído pela rede:\n")

for i in range(tamanho_vocab):
    palavra = id_para_palavra[i]
    original = vetores_contexto[i]
    reconstruido = saida_final[i]
    erro_palavra = np.mean((original - reconstruido) ** 2)
    print(f"  \"{palavra}\":")
    print(f"    Original:     {original.tolist()}")
    print(f"    Reconstruído: [{', '.join(f'{v:.2f}' for v in reconstruido)}]")
    print(f"    Erro (MSE):   {erro_palavra:.6f}\n")


# ==============================================================================
# PASSO 7: SIMILARIDADE ENTRE PALAVRAS
# ==============================================================================

print("=" * 70)
print("PASSO 7: SIMILARIDADE ENTRE PALAVRAS (COSSENO)")
print("=" * 70)
print("\nPalavras com contextos semelhantes terão embeddings próximos.")
print("Similaridade = 1 (muito semelhantes) até -1 (opostas)\n")


def similaridade_cosseno(a, b):
    """Calcula a similaridade do cosseno entre dois vetores."""
    norma_a = np.linalg.norm(a)
    norma_b = np.linalg.norm(b)
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return np.dot(a, b) / (norma_a * norma_b)


print(f"{'Palavra 1':<12} | {'Palavra 2':<12} | {'Similaridade':>12}")
print("-" * 42)

pares_similares = []
for i in range(tamanho_vocab):
    for j in range(i + 1, tamanho_vocab):
        sim = similaridade_cosseno(embeddings_final[i], embeddings_final[j])
        pares_similares.append((id_para_palavra[i], id_para_palavra[j], sim))

pares_similares.sort(key=lambda x: x[2], reverse=True)

for p1, p2, sim in pares_similares:
    print(f"{p1:<12} | {p2:<12} | {sim:>12.4f}")

print("\n" + "=" * 70)
print("RESUMO — COMPARAÇÃO COM A VERSÃO ReLU")
print("=" * 70)
print(f"""
VERSÃO LINEAR (este programa):
  - Camada escondida SEM ativação: embedding = X·W1 + b1
  - Valores negativos nos embeddings são PRESERVADOS
  - O gradiente flui livremente (sem "cortar" em zero)
  - Mais parecido com Word2Vec

VERSÃO COM ReLU (embedding_passo_a_passo.py):
  - Camada escondida COM ReLU: embedding = max(0, X·W1 + b1)
  - Valores negativos viram ZERO (representação esparsa)
  - Neurônios podem "morrer" (ficar permanentemente em 0)

Compare os embeddings e as similaridades entre as duas versões!
""")
