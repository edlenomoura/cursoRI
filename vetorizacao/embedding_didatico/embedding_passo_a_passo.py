"""
==============================================================================
 EMBEDDING DE PALAVRAS - EXEMPLO DIDÁTICO PASSO A PASSO
==============================================================================

Este programa ensina como criar embeddings (representações vetoriais densas)
de palavras usando uma rede neural simples do tipo autoencoder.

O processo tem 3 etapas:
  1) Construir o vocabulário e atribuir IDs às palavras
  2) Criar vetores de contexto para cada palavra (quantas vezes uma palavra
     aparece ANTES de cada outra palavra no texto)
  3) Treinar uma rede neural autoencoder que comprime esses vetores em
     vetores menores (os embeddings)

Textos de entrada:
  - "manaus capital do amazonas"
  - "belém capital do para"
  - "curitiba capital do parana"
==============================================================================
"""

import numpy as np

np.random.seed(42)  # Para resultados reproduzíveis

# ==============================================================================
# PASSO 1: CONSTRUIR O VOCABULÁRIO
# ==============================================================================
# Primeiro, juntamos todas as sentenças e identificamos as palavras distintas.
# Cada palavra recebe um ID numérico sequencial.

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

# Tokenização: quebrar cada sentença em palavras
todas_palavras = []
for sentenca in sentencas:
    palavras = sentenca.lower().split()
    todas_palavras.extend(palavras)

print(f"\nTodas as palavras (com repetições): {todas_palavras}")
print(f"Total de palavras no texto: {len(todas_palavras)}")

# Vocabulário: apenas as palavras DISTINTAS, na ordem em que aparecem
vocabulario = []
for palavra in todas_palavras:
    if palavra not in vocabulario:
        vocabulario.append(palavra)

# Mapear cada palavra para um ID numérico
palavra_para_id = {palavra: idx for idx, palavra in enumerate(vocabulario)}
id_para_palavra = {idx: palavra for palavra, idx in palavra_para_id.items()}

tamanho_vocab = len(vocabulario)

print(f"\nVocabulário ({tamanho_vocab} palavras distintas):")
for palavra, idx in palavra_para_id.items():
    print(f"  ID {idx}: \"{palavra}\"")


# ==============================================================================
# PASSO 2: CRIAR VETORES DE CONTEXTO
# ==============================================================================
# Para cada palavra do vocabulário, criamos um vetor com 'tamanho_vocab' dimensões.
# Cada dimensão 'j' do vetor da palavra 'i' contém o número de vezes que a
# palavra 'i' aparece IMEDIATAMENTE ANTES da palavra 'j' no texto.
#
# Exemplo com "a casa a a casa":
#   Vocabulário: a(0), casa(1)
#   Vetor de "a":   (1, 2) → "a" aparece antes de "a" 1 vez, antes de "casa" 2 vezes
#   Vetor de "casa": (1, 0) → "casa" aparece antes de "a" 1 vez, antes de "casa" 0 vezes

print("\n" + "=" * 70)
print("PASSO 2: CRIAR VETORES DE CONTEXTO")
print("=" * 70)

# Matriz de contagem: linhas = palavra atual, colunas = próxima palavra
# contagem[i][j] = quantas vezes a palavra i aparece antes da palavra j
contagem = np.zeros((tamanho_vocab, tamanho_vocab), dtype=int)

# Percorrer todas as sentenças e contar os pares consecutivos
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

# Cabeçalho da tabela
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

# Os vetores de contexto são as linhas da matriz
vetores_contexto = contagem.astype(float)

print(f"\nVetores de contexto resultantes:")
for i in range(tamanho_vocab):
    print(f"  \"{id_para_palavra[i]}\" → {vetores_contexto[i].tolist()}")


# ==============================================================================
# PASSO 3: CONSTRUIR E TREINAR A REDE NEURAL (AUTOENCODER)
# ==============================================================================
# A rede neural é um autoencoder: ela recebe o vetor de contexto como entrada
# e tenta reproduzi-lo na saída, passando por uma camada escondida MENOR.
#
# Estrutura da rede:
#   Entrada:  N neurônios (N = tamanho do vocabulário)
#   Escondida: 4 neurônios  ← ESTA É A CAMADA DO EMBEDDING!
#   Saída:    N neurônios
#
# A ideia é que, ao forçar a informação a passar por apenas 4 neurônios,
# a rede aprende uma representação COMPRIMIDA da palavra = o EMBEDDING.
#
#   [entrada N dims] → [W1] → [4 neurônios] → [W2] → [saída N dims]
#                              ↑
#                        EMBEDDING (4 dims)
#
# Cada neurônio da camada escondida está conectado a TODOS os neurônios
# de entrada e de saída (rede fully connected).

print("\n" + "=" * 70)
print("PASSO 3: CONSTRUIR A REDE NEURAL (AUTOENCODER)")
print("=" * 70)

tamanho_embedding = 4  # Número de neurônios na camada escondida

print(f"\nArquitetura da rede:")
print(f"  Camada de entrada:  {tamanho_vocab} neurônios (1 por palavra do vocabulário)")
print(f"  Camada escondida:   {tamanho_embedding} neurônios (será o embedding)")
print(f"  Camada de saída:    {tamanho_vocab} neurônios (reconstrução do vetor)")
print(f"\n  Total de conexões entrada→escondida: {tamanho_vocab} × {tamanho_embedding} = {tamanho_vocab * tamanho_embedding}")
print(f"  Total de conexões escondida→saída:   {tamanho_embedding} × {tamanho_vocab} = {tamanho_embedding * tamanho_vocab}")

# Inicializar pesos aleatoriamente (valores pequenos)
# W1: pesos da camada de entrada para a camada escondida (N x 4)
# b1: bias da camada escondida (4,)
# W2: pesos da camada escondida para a camada de saída (4 x N)
# b2: bias da camada de saída (N,)
W1 = np.random.randn(tamanho_vocab, tamanho_embedding) * 0.1
b1 = np.zeros(tamanho_embedding)
W2 = np.random.randn(tamanho_embedding, tamanho_vocab) * 0.1
b2 = np.zeros(tamanho_vocab)

print(f"\n  Pesos W1 (entrada→escondida): matriz {W1.shape}")
print(f"  Bias b1:  vetor {b1.shape}")
print(f"  Pesos W2 (escondida→saída):  matriz {W2.shape}")
print(f"  Bias b2:  vetor {b2.shape}")


# --- Funções auxiliares da rede ---

def relu(x):
    """Função de ativação ReLU: retorna max(0, x) para cada elemento.
    Usada na camada escondida para introduzir não-linearidade."""
    return np.maximum(0, x)


def relu_derivada(x):
    """Derivada da ReLU: 1 se x > 0, senão 0.
    Necessária para o backpropagation."""
    return (x > 0).astype(float)


# --- Propagação direta (forward pass) ---

def forward(X):
    """
    Calcula a saída da rede para um vetor de entrada X.

    Fluxo:
      1. z1 = X · W1 + b1        (combinação linear na camada escondida)
      2. a1 = ReLU(z1)           (ativação da camada escondida = EMBEDDING)
      3. z2 (s dos slides) = a1 · W2 + b2      (combinação linear na camada de saída)
      4. saida = z2              (saída linear - sem ativação)

    Retorna todas as variáveis intermediárias para uso no backpropagation.
    """
    z1 = X @ W1 + b1       # Pré-ativação da camada escondida
    a1 = relu(z1)           # Ativação da camada escondida (= embedding!)
    z2 = a1 @ W2 + b2      # Pré-ativação da saída
    saida = z2              # Saída (linear)
    return z1, a1, z2, saida


# --- Treinamento ---

print("\n" + "=" * 70)
print("PASSO 4: TREINAR A REDE (BACKPROPAGATION)")
print("=" * 70)

# Dados de treino: cada vetor de contexto é tanto a entrada quanto o alvo
X_treino = vetores_contexto  # (N_palavras x N_vocab)
Y_alvo = vetores_contexto    # queremos que a saída reproduza a entrada

taxa_aprendizado = 0.001
epocas = 5000

print(f"\n  Dados de treino: {X_treino.shape[0]} palavras, cada uma com vetor de {X_treino.shape[1]} dimensões")
print(f"  Taxa de aprendizado: {taxa_aprendizado}")
print(f"  Épocas de treinamento: {epocas}")
print(f"\n  Objetivo: aprender pesos que minimizem o erro entre entrada e saída")
print(f"  A camada escondida de {tamanho_embedding} neurônios COMPRIME a informação")
print(f"  → Os valores dessa camada são os EMBEDDINGS das palavras!\n")

historico_erro = []

for epoca in range(epocas):
    # --- Forward pass ---
    z1, a1, z2, saida = forward(X_treino)

    # --- Calcular o erro (MSE - Mean Squared Error) ---
    erro = Y_alvo - saida
    mse = np.mean(erro ** 2)
    historico_erro.append(mse)

    # --- Backward pass (backpropagation) ---
    # Calcular gradientes de trás para frente.
    # A regra da cadeia (chain rule) do cálculo é usada para propagar o erro.

    n_amostras = X_treino.shape[0]

    # Gradiente da saída (derivada do MSE em relação à saída)
    d_saida = -2 * erro / n_amostras  # (N_palavras x N_vocab)

    # Gradientes da camada de saída
    dW2 = a1.T @ d_saida              # (4 x N_vocab)
    db2 = np.sum(d_saida, axis=0)     # (N_vocab,)

    # Gradiente propagado para a camada escondida
    d_a1 = d_saida @ W2.T             # (N_palavras x 4)
    d_z1 = d_a1 * relu_derivada(z1)   # Aplica derivada da ReLU

    # Gradientes da camada de entrada
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
# Agora que a rede está treinada, passamos cada vetor de contexto pela rede
# e capturamos os valores da CAMADA ESCONDIDA. Esses 4 valores são o embedding!

print("\n" + "=" * 70)
print("PASSO 5: EXTRAIR OS EMBEDDINGS (RESULTADO FINAL)")
print("=" * 70)

print(f"\nPara cada palavra, o embedding é o vetor de {tamanho_embedding} dimensões")
print(f"produzido pela camada escondida da rede neural treinada.\n")

z1_final, embeddings_final, _, saida_final = forward(X_treino)

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
# Comparamos a saída da rede com o vetor original para ver se a rede
# conseguiu aprender a comprimir e reconstruir a informação.

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
# Uma propriedade interessante dos embeddings é que palavras com contextos
# semelhantes terão embeddings próximos. Vamos calcular a similaridade
# entre todos os pares de palavras usando a similaridade do cosseno.

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


# Calcular similaridades para todos os pares
print(f"{'Palavra 1':<12} | {'Palavra 2':<12} | {'Similaridade':>12}")
print("-" * 42)

pares_similares = []
for i in range(tamanho_vocab):
    for j in range(i + 1, tamanho_vocab):
        sim = similaridade_cosseno(embeddings_final[i], embeddings_final[j])
        pares_similares.append((id_para_palavra[i], id_para_palavra[j], sim))

# Ordenar por similaridade (maior primeiro)
pares_similares.sort(key=lambda x: x[2], reverse=True)

for p1, p2, sim in pares_similares:
    print(f"{p1:<12} | {p2:<12} | {sim:>12.4f}")

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"""
O que fizemos:
  1. Criamos um vocabulário de {tamanho_vocab} palavras a partir de 3 sentenças
  2. Para cada palavra, criamos um vetor de {tamanho_vocab} dimensões baseado
     em quantas vezes ela aparece antes de cada outra palavra
  3. Treinamos um autoencoder que comprime esses vetores de {tamanho_vocab} dimensões
  * Basicamente, um Autoencoder é uma rede neural projetada para copiar sua entrada para sua saída, mas com um "truque" no meio do caminho para forçar o aprendizado. Ele tem uma 
  camada escondida com menos neurônios do que a camada de entrada, o que obriga a rede a aprender uma representação comprimida dos dados (encoder) a partir da qual ele deve reconstruir a entrada (decoder).
     em vetores de apenas {tamanho_embedding} dimensões (a camada escondida)
  4. Esses vetores de {tamanho_embedding} dimensões são os EMBEDDINGS das palavras!

Por que isso é útil?
  - Embeddings capturam RELAÇÕES SEMÂNTICAS entre palavras
  - Palavras que aparecem em contextos semelhantes (como nomes de capitais
    ou nomes de estados) tendem a ter embeddings parecidos
  - Em vez de vetores esparsos de {tamanho_vocab} dimensões, temos vetores
    densos de apenas {tamanho_embedding} dimensões — muito mais eficientes!
""")
