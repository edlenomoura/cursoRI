"""
Programa de demonstração de Word2Vec
Este programa mostra como transformar texto em vetores usando Word2Vec
Compara os algoritmos CBOW (Continuous Bag of Words) e Skip-gram
"""

# Importa a biblioteca gensim, que fornece a implementação do Word2Vec
# Word2Vec é um algoritmo que aprende representações vetoriais de palavras
from gensim.models import Word2Vec

# Importa biblioteca para processamento de texto em português
import re

# Texto de exemplo - pequeno corpus para demonstração
# Em aplicações reais, você precisaria de muito mais texto para treinar um bom modelo
texto_exemplo = """
O direito é a garantia da justiça social.
A justiça deve ser acessível a todos os cidadãos.
O tribunal analisa cada caso com atenção.
A lei protege os direitos fundamentais.
Os advogados defendem a justiça e os direitos.
"""

print("=" * 60)
print("DEMONSTRAÇÃO DE WORD2VEC - CBOW vs SKIP-GRAM")
print("=" * 60)
print("Este programa compara dois algoritmos de vetorização:")
print("  • CBOW (Continuous Bag of Words)")
print("  • Skip-gram")
print(f"\nTexto original:\n{texto_exemplo}")

# PASSO 1: Pré-processamento do texto
# Remove pontuação e converte para minúsculas para normalização
texto_limpo = re.sub(r'[^\w\s]', '', texto_exemplo.lower())

# Divide o texto em sentenças (cada linha é uma sentença)
# Word2Vec trabalha com listas de sentenças, onde cada sentença é uma lista de palavras
sentencas = [linha.split() for linha in texto_limpo.split('\n') if linha.strip()]

print(f"\n{'=' * 60}")
print("PASSO 1: PRÉ-PROCESSAMENTO")
print(f"{'=' * 60}")
print(f"Sentenças tokenizadas:")
for i, sentenca in enumerate(sentencas, 1):
    print(f"  {i}. {sentenca}")

# PASSO 2: Treinamento dos modelos Word2Vec (CBOW e Skip-gram)
print(f"\n{'=' * 60}")
print("PASSO 2: TREINAMENTO DOS MODELOS WORD2VEC")
print(f"{'=' * 60}")

# Parâmetros comuns para ambos os modelos
parametros_comuns = {
    'sentences': sentencas,      # Lista de sentenças (cada sentença é uma lista de tokens)
    'vector_size': 10,           # Dimensão dos vetores (10 dimensões para cada palavra)
                                 # Valores típicos: 100-300 para corpus grandes
    'window': 3,                 # Janela de contexto: quantas palavras antes e depois considerar
                                 # window=3 significa que considera 3 palavras à esquerda e 3 à direita
    'min_count': 1,              # Frequência mínima: palavras que aparecem menos que isso são ignoradas
                                 # min_count=1 mantém todas as palavras (bom para corpus pequeno)
    'workers': 4,                # Número de threads para treinamento paralelo
    'epochs': 100                # Número de iterações sobre o corpus durante o treinamento
                                 # Mais epochs = mais aprendizado (mas pode causar overfitting)
}

print("\n>>> Treinando modelo com CBOW (Continuous Bag of Words)...")
# CBOW: Prevê a palavra alvo a partir do contexto (palavras ao redor)
# Mais rápido e funciona melhor para palavras frequentes
modelo_cbow = Word2Vec(
    **parametros_comuns,
    sg=0                         # sg=0 usa o algoritmo CBOW
)
print(f"✓ Modelo CBOW treinado!")
print(f"  - Vocabulário: {len(modelo_cbow.wv)} palavras únicas")
print(f"  - Dimensão dos vetores: {modelo_cbow.wv.vector_size}")

print("\n>>> Treinando modelo com Skip-gram...")
# Skip-gram: Prevê as palavras do contexto a partir da palavra alvo
# Funciona melhor para palavras raras e corpus pequenos
# Captura melhor relações semânticas sutis
modelo_skipgram = Word2Vec(
    **parametros_comuns,
    sg=1                         # sg=1 usa o algoritmo Skip-gram
)
print(f"✓ Modelo Skip-gram treinado!")
print(f"  - Vocabulário: {len(modelo_skipgram.wv)} palavras únicas")
print(f"  - Dimensão dos vetores: {modelo_skipgram.wv.vector_size}")

# PASSO 3: Explorando os vetores gerados (comparação CBOW vs Skip-gram)
print(f"\n{'=' * 60}")
print("PASSO 3: VETORES GERADOS PARA CADA TOKEN")
print(f"{'=' * 60}")
print("Comparando vetores gerados pelos dois algoritmos:\n")

# Itera sobre cada palavra no vocabulário e mostra vetores de ambos os modelos
for palavra in modelo_cbow.wv.index_to_key:  # index_to_key contém todas as palavras do vocabulário
    vetor_cbow = modelo_cbow.wv[palavra]      # Obtém o vetor da palavra no modelo CBOW
    vetor_skipgram = modelo_skipgram.wv[palavra]  # Obtém o vetor da palavra no modelo Skip-gram
    
    print(f"Palavra: '{palavra}'")
    print(f"  CBOW:      {vetor_cbow}")
    print(f"  Skip-gram: {vetor_skipgram}")
    print(f"  Forma: {vetor_cbow.shape}")
    print()

# PASSO 4: Demonstração de similaridade semântica (comparação CBOW vs Skip-gram)
print(f"\n{'=' * 60}")
print("PASSO 4: ANÁLISE DE SIMILARIDADE SEMÂNTICA")
print(f"{'=' * 60}")
print("Comparando as palavras mais similares encontradas por cada algoritmo:\n")

# Word2Vec aprende que palavras usadas em contextos similares têm vetores próximos
# Podemos calcular a similaridade entre palavras usando cosseno da distância vetorial

# Escolhe algumas palavras do vocabulário para análise
palavras_teste = ['justiça', 'direitos', 'lei']

for palavra in palavras_teste:
    if palavra in modelo_cbow.wv:
        print(f"═══ Palavra: '{palavra}' ═══")
        
        # Tenta calcular similaridades com CBOW
        print(f"\n  [CBOW] Palavras mais similares:")
        try:
            # most_similar retorna as palavras com vetores mais próximos (maior similaridade de cosseno)
            similares_cbow = modelo_cbow.wv.most_similar(palavra, topn=3)  # topn=3 retorna as 3 mais similares
            for palavra_similar, similaridade in similares_cbow:
                print(f"    - {palavra_similar}: {similaridade:.4f}")  # similaridade varia de 0 a 1
        except:
            print(f"    (Corpus muito pequeno para calcular similaridades confiáveis)")
        
        # Tenta calcular similaridades com Skip-gram
        print(f"\n  [Skip-gram] Palavras mais similares:")
        try:
            similares_skipgram = modelo_skipgram.wv.most_similar(palavra, topn=3)
            for palavra_similar, similaridade in similares_skipgram:
                print(f"    - {palavra_similar}: {similaridade:.4f}")
        except:
            print(f"    (Corpus muito pequeno para calcular similaridades confiáveis)")
        
        print()  # Linha em branco para separação

# PASSO 5: Salvando os modelos treinados
print(f"\n{'=' * 60}")
print("PASSO 5: PERSISTÊNCIA DOS MODELOS")
print(f"{'=' * 60}")

# Salva ambos os modelos treinados para uso futuro
modelo_cbow.save("word2vec_cbow.bin")
print("✓ Modelo CBOW salvo em: word2vec_cbow.bin")

modelo_skipgram.save("word2vec_skipgram.bin")
print("✓ Modelo Skip-gram salvo em: word2vec_skipgram.bin")

# Para carregar os modelos posteriormente, use:
# modelo_cbow_carregado = Word2Vec.load("word2vec_cbow.bin")
# modelo_skipgram_carregado = Word2Vec.load("word2vec_skipgram.bin")

print(f"\n{'=' * 60}")
print("DEMONSTRAÇÃO CONCLUÍDA!")
print(f"{'=' * 60}")
print("\nNOTAS IMPORTANTES:")
print("- Este é um exemplo didático com corpus muito pequeno")
print("- Para resultados melhores, use milhares de sentenças")
print("- Word2Vec aprende relações semânticas entre palavras")
print("- Palavras com contextos similares terão vetores próximos")
print("\nDIFERENÇAS ENTRE CBOW E SKIP-GRAM:")
print("- CBOW: Prevê palavra a partir do contexto (mais rápido)")
print("- Skip-gram: Prevê contexto a partir da palavra (melhor para palavras raras)")
print("- Skip-gram geralmente funciona melhor com corpus pequenos")
print("- CBOW é mais eficiente computacionalmente para corpus grandes")
