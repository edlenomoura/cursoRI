"""
Programa de demonstração de BERTimbau para vetorização de texto
BERTimbau é um modelo BERT pré-treinado especificamente para português brasileiro
Diferente do Word2Vec, BERT gera vetores contextualizados (depende do contexto da sentença)
"""

# Importa a biblioteca transformers do Hugging Face
# Esta biblioteca fornece acesso a modelos pré-treinados como BERT
# Lembre-se que o BERT é um transformer, veja os slides sobre BERT 
# para lembar porque ele é chamado de transformer
from transformers import AutoTokenizer, AutoModel

# Importa torch (PyTorch) para manipular tensores e fazer inferência
import torch

# Importa numpy para manipulação de arrays numéricos
import numpy as np

print("=" * 70)
print("DEMONSTRAÇÃO DE BERTIMBAU - VETORIZAÇÃO CONTEXTUALIZADA")
print("=" * 70)
print("\nBERTimbau é um modelo BERT treinado em português brasileiro")
print("Características:")
print("  • Vetores contextualizados (mesma palavra = diferentes vetores)")
print("  • ~110 milhões de parâmetros")
print("  • Vetores de 768 dimensões")
print("=" * 70)

# Texto de exemplo - mesmo corpus usado no Word2Vec para comparação
texto_exemplo = """
O direito é a garantia da justiça social.
A justiça deve ser acessível a todos os cidadãos.
O tribunal analisa cada caso com atenção.
A lei protege os direitos fundamentais.
Os advogados defendem a justiça e os direitos.
"""

print(f"\nTexto original:\n{texto_exemplo}")

# PASSO 1: Preparando as sentenças
print(f"\n{'=' * 70}")
print("PASSO 1: PREPARAÇÃO DAS SENTENÇAS")
print(f"{'=' * 70}")

# Divide o texto em sentenças (uma por linha)
sentencas = [linha.strip() for linha in texto_exemplo.split('\n') if linha.strip()]

print(f"Total de sentenças: {len(sentencas)}")
for i, sentenca in enumerate(sentencas, 1):
    print(f"  {i}. {sentenca}")

# PASSO 2: Carregando o modelo BERTimbau
print(f"\n{'=' * 70}")
print("PASSO 2: CARREGANDO O MODELO BERTIMBAU")
print(f"{'=' * 70}")
print("Aguarde... Este passo pode demorar na primeira execução.")
print("(O modelo será baixado automaticamente - ~400MB)\n")

# Nome do modelo no Hugging Face Hub
# neuralmind/bert-base-portuguese-cased é o BERTimbau base
modelo_nome = "neuralmind/bert-base-portuguese-cased"

# Carrega o tokenizador - responsável por converter texto em tokens numéricos
# O tokenizador divide o texto em subpalavras (subword tokens) usando WordPiece
tokenizer = AutoTokenizer.from_pretrained(modelo_nome)
print(f"✓ Tokenizador carregado: {modelo_nome}")

# Carrega o modelo BERT pré-treinado
# AutoModel carrega automaticamente a arquitetura correta baseada no nome
modelo = AutoModel.from_pretrained(modelo_nome)
print(f"✓ Modelo carregado: {modelo_nome}")
print(f"  - Parâmetros: ~110 milhões")
print(f"  - Dimensão dos vetores: 768")

# Coloca o modelo em modo de avaliação (inference mode)
# MODOS DO MODELO:
#
# 1. MODO DE TREINAMENTO (Training Mode) - modelo.train()
#    - Dropout ativo: desliga aleatoriamente neurônios para evitar overfitting
#    - Batch Normalization: usa estatísticas do batch atual
#    - Usado quando: estamos ajustando os pesos do modelo (fine-tuning)
#    - Cálculo de gradientes: ativo (para backpropagation)
#      IDEAL TER UMA GPU BOA SE TENTAR FAZER FINE TUNING DO MODELO, POIS É MUITO PESADO
#
# 2. MODO DE AVALIAÇÃO (Evaluation/Inference Mode) - modelo.eval()
#    - Dropout desativado: todos os neurônios ativos (comportamento determinístico)
#    - Batch Normalization: usa estatísticas globais calculadas no treinamento
#    - Usado quando: fazemos previsões/inferência (não estamos treinando)
#    - Cálculo de gradientes: geralmente desativado (usa torch.no_grad())
#    - Resultado: mais rápido e com menos uso de memória
#
# Aqui usamos eval() porque estamos apenas fazendo inferência (vetorização),
# não estamos treinando ou ajustando o modelo.
modelo.eval()

# PASSO 3: Tokenização das sentenças
print(f"\n{'=' * 70}")
print("PASSO 3: TOKENIZAÇÃO COM BERTIMBAU")
print(f"{'=' * 70}")
print("BERT usa tokenização em subpalavras (WordPiece):")
print("Palavras podem ser divididas em pedaços menores\n")

# Demonstra a tokenização da primeira sentença
sentenca_exemplo = sentencas[0]
tokens = tokenizer.tokenize(sentenca_exemplo)
print(f"Sentença: '{sentenca_exemplo}'")
print(f"Tokens: {tokens}")
print(f"Total de tokens: {len(tokens)}")
print("\nTokens especiais:")
print("  [CLS] - Token especial no início (representa a sentença toda)")
print("  [SEP] - Token especial no fim (separador)")

# PASSO 4: Gerando vetores para cada sentença
print(f"\n{'=' * 70}")
print("PASSO 4: GERANDO VETORES CONTEXTUALIZADOS")
print(f"{'=' * 70}")
print("Processando cada sentença e extraindo seus vetores...\n")

# Lista para armazenar os vetores de cada sentença
vetores_sentencas = []

# Desabilita o cálculo de gradientes (não estamos treinando, apenas inferindo)
# Isso economiza memória e torna o processamento mais rápido
# se fosse fine-tunning, ai teríamos que calcular os gradientes, mas como só queremos os vetores, não precisamos disso
# se fosse calcular os gradientes, teríamos que usar o modelo em modo de treinamento (modelo.train()) e não desabilitar os gradientes
with torch.no_grad():
    for i, sentenca in enumerate(sentencas, 1):
        print(f"[{i}/{len(sentencas)}] Processando: '{sentenca}'")
        
        # Tokeniza a sentença e converte para formato aceito pelo modelo
        # return_tensors='pt' retorna tensores do PyTorch
        # outras alternativas para return_tensors poderiam 
        # ser 'tf' para TensorFlow ou 'np' para NumPy, mas 
        # aqui usamos PyTorch
        # (*Tensores são objetos matemáticos que generalizam conceitos 
        # de escalares, vetores e matrizes para dimensões superiores (arranjos multidimensionais de números). 
        # . Pense neles como matrizes e vetores aqui)
        # padding=True e truncation=True garantem que o input tenha tamanho adequado
        inputs = tokenizer(
            sentenca,
            return_tensors='pt',     # Retorna tensores PyTorch
            padding=True,            # Adiciona padding se necessário
            truncation=True,         # Trunca se passar do tamanho máximo (512 tokens)
            max_length=512           # Tamanho máximo de entrada do BERT, esse valor é em número de tokens 
                                     # da sentença, não é o número de palavras, porque o BERT pode dividir 
                                    # palavras em subpalavras (tokens) 
        )
        
        # Passa os inputs pelo modelo BERT
        # outputs contém os embeddings de cada token para a sentença
        # lembre que BERT gera um vetor para cada token, não apenas um vetor para a sentença inteira
        # e os vetores de cada token mudam em função da sentença

        outputs = modelo(**inputs)
        
        # last_hidden_state contém os vetores de cada token [batch_size, seq_length, hidden_size]
        # hidden_size = 768 para o BERT base
        hidden_states = outputs.last_hidden_state
        
        # ESTRATÉGIA 1: Usa o vetor [CLS] como representação da sentença
        # O token [CLS] (primeiro token) é treinado para representar a sentença toda
        vetor_cls = hidden_states[0, 0, :].numpy()  # Pega o primeiro token da primeira sentença
        
        # ESTRATÉGIA 2: Calcula a média de todos os tokens (pooling)
        # Esta é outra forma comum de obter um vetor para a sentença
        vetor_mean = hidden_states[0].mean(dim=0).numpy()  # Média de todos os tokens
        
        # Vamos usar o vetor [CLS] como representação principal
        vetores_sentencas.append(vetor_cls)
        
        print(f"    Tokens de entrada: {inputs['input_ids'].shape[1]}")
        print(f"    Vetor [CLS] (primeiras 10 dims): {vetor_cls[:10]}")
        print(f"    Forma do vetor completo: {vetor_cls.shape}")
        print()

# PASSO 5: Análise dos vetores gerados
print(f"{'=' * 70}")
print("PASSO 5: ANÁLISE DOS VETORES GERADOS")
print(f"{'=' * 70}")

print(f"\nResumo da vetorização:")
print(f"  - Total de sentenças vetorizadas: {len(vetores_sentencas)}")
print(f"  - Dimensão de cada vetor: {vetores_sentencas[0].shape[0]}")
print(f"  - Tamanho total em memória: ~{len(vetores_sentencas) * 768 * 4 / 1024:.2f} KB")

# Demonstra os tokens e vetores individuais de cada sentença
print(f"\nDETALHES: Tokens e seus vetores (primeiras 5 dimensões)")
print(f"Lembre-se: BERT gera um vetor para CADA token da sentença!\n")

# Processa novamente as sentenças para mostrar detalhes dos tokens
with torch.no_grad():
    for i, sentenca in enumerate(sentencas[:2], 1):  # Mostra apenas 2 primeiras sentenças para não poluir
        print(f"─" * 70)
        print(f"Sentença {i}: '{sentenca}'")
        print(f"─" * 70)
        
        # Tokeniza a sentença
        inputs = tokenizer(sentenca, return_tensors='pt', padding=True, truncation=True, max_length=512)
        
        # Obtém os tokens como strings
        tokens_ids = inputs['input_ids'][0].tolist()
        tokens_strings = tokenizer.convert_ids_to_tokens(tokens_ids)
        
        # Passa pelo modelo para obter vetores
        outputs = modelo(**inputs)
        hidden_states = outputs.last_hidden_state
        
        # Mostra cada token e seu vetor
        print(f"\nTotal de tokens (incluindo [CLS] e [SEP]): {len(tokens_strings)}\n")
        for idx, token in enumerate(tokens_strings):
            vetor_token = hidden_states[0, idx, :].numpy()
            print(f"  Token {idx:2d}: '{token:15s}' → Vetor (5 primeiras dims): {vetor_token[:5]}")
        
        print(f"\n  💡 Cada um desses {len(tokens_strings)} tokens tem 768 dimensões!")
        print(f"  💡 Os vetores dependem do CONTEXTO da sentença")
        print()

print(f"{'─' * 70}\n")

# PASSO 6: Calculando similaridade entre sentenças
print(f"\n{'=' * 70}")
print("PASSO 6: SIMILARIDADE ENTRE SENTENÇAS")
print(f"{'=' * 70}")
print("Calculando similaridade de cosseno entre pares de sentenças:\n")

def cosine_similarity(v1, v2):
    """
    Calcula a similaridade de cosseno entre dois vetores
    Retorna um valor entre -1 e 1, onde 1 = vetores idênticos
    """
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Compara cada par de sentenças
for i in range(len(sentencas)):
    for j in range(i + 1, len(sentencas)):
        similaridade = cosine_similarity(vetores_sentencas[i], vetores_sentencas[j])
        print(f"Sentença {i+1} vs Sentença {j+1}: {similaridade:.4f}")
        print(f"  [{i+1}] {sentencas[i][:50]}...")
        print(f"  [{j+1}] {sentencas[j][:50]}...")
        print()

# PASSO 7: Comparação Word2Vec vs BERTimbau
print(f"{'=' * 70}")
print("PASSO 7: WORD2VEC vs BERTIMBAU - PRINCIPAIS DIFERENÇAS")
print(f"{'=' * 70}")

print("""
┌─────────────────┬──────────────────────┬──────────────────────────┐
│ Característica  │ Word2Vec             │ BERTimbau                │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Tipo de vetor   │ Estático             │ Contextualizado          │
│                 │ (mesma palavra =     │ (mesma palavra pode ter  │
│                 │  mesmo vetor)        │  vetores diferentes)     │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Dimensões       │ 50-300 (configurável)│ 768 (BERT base)          │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Treinamento     │ Rápido, corpus       │ Pré-treinado em grande   │
│                 │ específico           │ corpus, pronto para uso  │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Corpus mínimo   │ Milhares de sentenças│ Não precisa (já treinado)│
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Uso de recursos │ Leve (~MB)           │ Pesado (~400MB + RAM)    │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Velocidade      │ Muito rápido         │ Mais lento (milhares de  │
│                 │                      │ operações por sentença)  │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ Melhor para     │ - Tarefas simples    │ - Tarefas complexas      │
│                 │ - Similaridade       │ - Classificação          │
│                 │ - Clustering         │ - Q&A, NER, etc.         │
└─────────────────┴──────────────────────┴──────────────────────────┘
""")

print("\nEXEMPLO DE CONTEXTUALIZAÇÃO:")
print("Palavra 'banco' no Word2Vec: sempre o mesmo vetor")
print("Palavra 'banco' no BERT:")
print("  'Sentei no banco da praça' → vetor A (mobiliário)")
print("  'Fui ao banco sacar dinheiro' → vetor B (instituição)")
print("  A ≠ B (vetores diferentes baseados no contexto!)")

print(f"\n{'=' * 70}")
print("DEMONSTRAÇÃO CONCLUÍDA!")
print(f"{'=' * 70}")
print("\nNOTAS IMPORTANTES:")
print("- BERTimbau captura nuances contextuais que Word2Vec não consegue")
print("- Requer mais recursos computacionais (CPU/GPU, RAM)")
print("- Ideal para tarefas de NLP complexas em português brasileiro")
print("- Não requer treinamento adicional (já vem pré-treinado)")
