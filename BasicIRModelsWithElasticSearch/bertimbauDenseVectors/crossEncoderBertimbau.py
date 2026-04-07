#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CROSS-ENCODER COM BERTIMBAU PARA RE-RANKING DE BUSCA
================================================================================

Este script demonstra o uso do BERTimbau no modo CROSS-ENCODER para busca,
comparando com o modo BI-ENCODER já visto nos outros scripts do curso.

================================================================================
BI-ENCODER vs CROSS-ENCODER — A DIFERENÇA FUNDAMENTAL
================================================================================

BI-ENCODER (modo usado em indexaBertimbauElastic.py e buscaBertimbauElastic.py):
──────────────────────────────────────────────────────────────────────────────────

  Consulta ──► [BERT] ──► vetor_q ─┐
                                     ├──► cosine(vetor_q, vetor_d) ──► score
  Documento ──► [BERT] ──► vetor_d ─┘

  • Consulta e documento são codificados SEPARADAMENTE
  • Cada texto vira um vetor independente de 768 dimensões
  • Comparação feita por similaridade cosseno entre vetores
  • Vantagem: vetores dos documentos podem ser pré-computados (RÁPIDO!)
  • Desvantagem: não há interação entre query e documento durante a codificação

CROSS-ENCODER (modo demonstrado neste script):
──────────────────────────────────────────────────────────────────────────────────

  [CLS] Consulta [SEP] Documento [SEP] ──► [BERT] ──► score de relevância
          ↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕↕
          Cross-Attention COMPLETA
          entre todos os tokens de
          query e documento juntos!

  • Consulta e documento são alimentados JUNTOS ao BERT
  • BERT faz cross-attention entre TODOS os tokens de ambos os textos
  • Produz um score ÚNICO de relevância para o par (query, documento)
  • Vantagem: MUITO mais preciso (BERT "vê" query + doc ao mesmo tempo)
  • Desvantagem: NÃO pode pré-computar (precisa rodar BERT para cada par)

================================================================================
POR QUE O CROSS-ENCODER É MAIS PRECISO?
================================================================================

Imagine a consulta: "dano moral por atraso de voo"

BI-ENCODER:
- Codifica "dano moral por atraso de voo" → vetor_q (768 dims)
- Codifica "indenização por cancelamento de passagem aérea" → vetor_d (768 dims)
- Calcula cosine(vetor_q, vetor_d)
- O modelo NUNCA viu os dois textos juntos!

CROSS-ENCODER:
- Alimenta: [CLS] dano moral por atraso de voo [SEP] indenização por
  cancelamento de passagem aérea [SEP]
- BERT faz self-attention entre TODOS os tokens dos DOIS textos
- "dano moral" interage com "indenização" (sinônimos contextuais)
- "atraso de voo" interage com "cancelamento de passagem aérea" (mesmo domínio)
- O modelo pode capturar relações CRUZADAS entre os textos!

================================================================================
PIPELINE TÍPICO: RETRIEVE & RE-RANK (duas etapas)
================================================================================

  Coleção de     Etapa 1: Retrieval        Etapa 2: Re-Ranking
  Documentos     (rápido, aproximado)       (lento, preciso)
  ┌──────────┐   ┌──────────────────┐       ┌──────────────────┐
  │ 1.000.000│──►│ BM25 ou kNN      │──►    │ Cross-Encoder    │──► Top 10
  │ documentos│   │ Retorna Top 100  │ 100   │ Re-ordena Top 100│    finais
  └──────────┘   │ candidatos       │ docs  │ com score preciso│
                 └──────────────────┘       └──────────────────┘

  • Etapa 1: Filtra candidatos (BM25 léxico ou bi-encoder semântico)
    → Rápido, processa milhões de documentos em milissegundos
  • Etapa 2: Re-rankeia candidatos com cross-encoder
    → Lento (~100 pares), mas MUITO mais preciso

================================================================================
NESTE SCRIPT
================================================================================

Usamos BERTimbau (neuralmind/bert-base-portuguese-cased) de duas formas:

1. Como Bi-Encoder: codifica query e docs separadamente (baseline)
2. Como Cross-Encoder: codifica pares (query, doc) juntos (re-ranking)

Para o cross-encoder, usamos BertForSequenceClassification que adiciona
uma camada linear sobre o token [CLS] para produzir um score de relevância.

NOTA IMPORTANTE:
O modelo NÃO foi fine-tunado para re-ranking. Em produção, seria necessário
fine-tunar com dados de relevância (ex: pares query-doc com labels).
Para fins DIDÁTICOS, demonstramos:
  - A arquitetura e o pipeline completo
  - Como a cross-attention captura interações entre query e doc
  - A diferença estrutural entre bi-encoder e cross-encoder
  - O trade-off velocidade vs. precisão

================================================================================
"""

import time
import warnings
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, BertForSequenceClassification
from typing import List, Tuple

# Suprimir warnings
warnings.filterwarnings("ignore", message=".*resume_download.*", category=FutureWarning)

# Mesmo modelo BERTimbau dos outros scripts
BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"

# Documentos de exemplo — conceitos jurídicos curtos
# (Usando uma amostra pequena para o exemplo rodar rápido e ser didático)
DOCUMENTOS = [
    {"id": 1,  "texto": "dano moral por ofensa à honra e dignidade da pessoa"},
    {"id": 2,  "texto": "indenização por acidente de trânsito com vítima fatal"},
    {"id": 3,  "texto": "contrato de compra e venda de imóvel residencial urbano"},
    {"id": 4,  "texto": "pensão alimentícia para filho menor de idade"},
    {"id": 5,  "texto": "execução fiscal de dívida tributária municipal"},
    {"id": 6,  "texto": "habeas corpus contra prisão preventiva ilegal"},
    {"id": 7,  "texto": "recurso de apelação contra sentença de primeiro grau"},
    {"id": 8,  "texto": "responsabilidade civil do empregador por acidente de trabalho"},
    {"id": 9,  "texto": "usucapião extraordinária de bem imóvel rural"},
    {"id": 10, "texto": "guarda compartilhada dos filhos após divórcio"},
    {"id": 11, "texto": "rescisão indireta do contrato de trabalho por justa causa do empregador"},
    {"id": 12, "texto": "mandado de segurança contra ato de autoridade pública"},
    {"id": 13, "texto": "penhora de bens do devedor para garantia da execução"},
    {"id": 14, "texto": "embargos de declaração por omissão na sentença"},
    {"id": 15, "texto": "danos morais por inscrição indevida em cadastro de inadimplentes"},
    {"id": 16, "texto": "revisão de contrato bancário com juros abusivos"},
    {"id": 17, "texto": "aposentadoria por invalidez junto ao INSS"},
    {"id": 18, "texto": "ação de despejo por falta de pagamento de aluguel"},
    {"id": 19, "texto": "tutela antecipada de urgência em ação de saúde"},
    {"id": 20, "texto": "impugnação ao cumprimento de sentença por excesso de execução"},
]


# ============================================================================
# CARREGAMENTO DOS MODELOS
# ============================================================================

def carregar_bertimbau_biencoder():
    """
    Carrega BERTimbau no modo BI-ENCODER.
    
    Usa AutoModel: retorna hidden states (vetores) para cada token.
    O token [CLS] é usado como embedding da sentença.
    
    Este é o MESMO modo usado em indexaBertimbauElastic.py
    """
    print("📥 Carregando BERTimbau (BI-ENCODER)...")
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    model = AutoModel.from_pretrained(BERTIMBAU_MODEL)
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"   ✓ Modelo carregado no modo bi-encoder ({device})\n")
    
    return tokenizer, model, device


def carregar_bertimbau_crossencoder():
    """
    Carrega BERTimbau no modo CROSS-ENCODER.
    
    Usa BertForSequenceClassification:
    - Mesma arquitetura BERT (12 camadas de transformer)
    - MAIS uma camada linear no topo: [CLS] (768 dims) → score (1 dim)
    
    Estrutura:
    ┌─────────────────────────────────────┐
    │  Camada de Classificação (Linear)   │  ← Nova! Projeta [CLS] → score
    │  768 → 1                            │
    ├─────────────────────────────────────┤
    │  BERT (12 camadas Transformer)      │  ← Mesmas camadas do bi-encoder
    │  Token [CLS] = representação global │
    ├─────────────────────────────────────┤
    │  Token Embeddings + Position Emb.   │
    │  [CLS] query [SEP] documento [SEP]  │  ← Entrada: PAR de textos!
    └─────────────────────────────────────┘
    
    NOTA: A camada linear é inicializada com pesos aleatórios.
    Em produção, faríamos fine-tuning com dados de relevância.
    """
    print("📥 Carregando BERTimbau (CROSS-ENCODER)...")
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    
    # num_labels=1: regressão (1 score de relevância por par)
    model = BertForSequenceClassification.from_pretrained(
        BERTIMBAU_MODEL,
        num_labels=1  # Score único de relevância
    )
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"   ✓ Modelo carregado no modo cross-encoder ({device})")
    print(f"   Arquitetura: BERT base (768) + Linear(768→1)\n")
    
    return tokenizer, model, device


# ============================================================================
# BI-ENCODER: CODIFICAÇÃO SEPARADA
# ============================================================================

def biencoder_gerar_embedding(texto, tokenizer, model, device):
    """
    [BI-ENCODER] Gera embedding de um texto individual.
    
    Processo:
    1. Tokeniza o texto
    2. Passa pelo BERT
    3. Extrai hidden state do token [CLS]
    4. Retorna vetor de 768 dimensões
    
    NOTA: Query e documento são processados SEPARADAMENTE.
    Não há interação entre eles nesta etapa.
    """
    inputs = tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Token [CLS] → embedding da sentença
    cls_embedding = outputs.last_hidden_state[0][0].cpu().numpy()
    return cls_embedding


def biencoder_rankear(query, documentos, tokenizer, model, device):
    """
    [BI-ENCODER] Rankeia documentos por similaridade com a query.
    
    Pipeline:
    1. Gera embedding da query (separadamente)
    2. Gera embedding de cada documento (separadamente)
    3. Calcula cosine similarity entre query e cada documento
    4. Ordena por score decrescente
    
    Complexidade: O(N) chamadas ao BERT, onde N = número de documentos
    MAS: embeddings dos documentos podem ser PRÉ-COMPUTADOS!
    Em produção, só precisa computar o embedding da query.
    """
    # Embedding da query
    emb_query = biencoder_gerar_embedding(query, tokenizer, model, device)
    
    resultados = []
    for doc in documentos:
        # Embedding do documento (em produção, seria pré-computado)
        emb_doc = biencoder_gerar_embedding(doc["texto"], tokenizer, model, device)
        
        # Similaridade cosseno
        cos_sim = np.dot(emb_query, emb_doc) / (
            np.linalg.norm(emb_query) * np.linalg.norm(emb_doc)
        )
        
        resultados.append({
            "id": doc["id"],
            "texto": doc["texto"],
            "score": float(cos_sim)
        })
    
    # Ordena por score decrescente
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados


# ============================================================================
# CROSS-ENCODER: CODIFICAÇÃO CONJUNTA
# ============================================================================

def crossencoder_score_par(query, documento, tokenizer, model, device):
    """
    [CROSS-ENCODER] Calcula score de relevância para um par (query, documento).
    
    Processo:
    1. Tokeniza JUNTOS: [CLS] query [SEP] documento [SEP]
    2. BERT processa com cross-attention COMPLETA entre tokens
    3. Camada linear projeta [CLS] → score escalar
    
    A MÁGICA DO CROSS-ENCODER:
    
    Na self-attention do BERT, CADA token da query pode "olhar" para
    CADA token do documento (e vice-versa):
    
    Tokens de entrada:
    [CLS] dano moral [SEP] indenização por ofensa à honra [SEP]
      ↕     ↕    ↕           ↕         ↕    ↕      ↕   ↕
    Attention entre TODOS eles! "dano" ← attend → "ofensa"
                                "moral" ← attend → "honra"
    
    Isso permite capturar relações semânticas CRUZADAS que o
    bi-encoder não consegue (pois codifica cada texto isoladamente).
    
    Args:
        query: Texto da consulta
        documento: Texto do documento
        tokenizer: Tokenizer do BERT
        model: BertForSequenceClassification
        device: 'cuda' ou 'cpu'
        
    Returns:
        float: Score de relevância (quanto maior, mais relevante)
    """
    # Tokenização como PAR de sentenças:
    # O tokenizer automaticamente gera: [CLS] text_a [SEP] text_b [SEP]
    # e seta token_type_ids: 0 0 0 0 0 0 1 1 1 1 1 1
    #                        \___ query ___/ \__ doc __/
    inputs = tokenizer(
        query,            # Primeira sentença (query)
        documento,        # Segunda sentença (documento)
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # outputs.logits: tensor de shape [1, 1] (batch=1, num_labels=1)
    # É o score de relevância do par (query, documento)
    score = outputs.logits[0][0].cpu().item()
    
    return score


def crossencoder_rankear(query, documentos, tokenizer, model, device):
    """
    [CROSS-ENCODER] Rankeia documentos por relevância com a query.
    
    Pipeline:
    1. Para CADA documento, alimenta o par (query, documento) ao BERT
    2. BERT computa cross-attention entre query e documento
    3. Score de relevância para cada par
    4. Ordena por score decrescente
    
    CUSTO: O(N) chamadas ao BERT (mesmo que bi-encoder)
    MAS: NÃO pode pré-computar! Precisa rodar BERT para cada par.
    Por isso, cross-encoder é usado para RE-RANKING (poucos candidatos).
    """
    resultados = []
    
    for doc in documentos:
        score = crossencoder_score_par(query, doc["texto"], tokenizer, model, device)
        resultados.append({
            "id": doc["id"],
            "texto": doc["texto"],
            "score": score
        })
    
    # Ordena por score decrescente
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados


# ============================================================================
# CROSS-ENCODER MANUAL (sem camada de classificação)
# ============================================================================

def crossencoder_manual_score(query, documento, tokenizer, model_base, device):
    """
    [CROSS-ENCODER MANUAL] Score usando modelo base (AutoModel) + cosine.
    
    ALTERNATIVA ao BertForSequenceClassification que NÃO requer
    camada de classificação (e portanto não depende de fine-tuning).
    
    Ideia:
    1. Codifica (query, documento) como par → extrai [CLS]
    2. Codifica "texto relevante" como âncora → extrai [CLS]
    3. Calcula cosine([CLS] do par, [CLS] da âncora relevante)
    
    Na prática: usamos a NORMA do vetor [CLS] do par como heurística.
    Pares mais "coerentes" tendem a ter [CLS] com maior ativação.
    
    NOTA: Esta é uma heurística simplificada para ilustração.
    Em produção, use um modelo fine-tunado.
    """
    # Tokeniza como PAR de sentenças
    inputs = tokenizer(
        query,
        documento,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model_base(**inputs)
    
    # [CLS] token do par (query, doc) processado junto
    cls_par = outputs.last_hidden_state[0][0]
    
    # Mean pooling de todos os tokens (alternativa ao [CLS])
    # Captura a representação "média" da interação query-documento
    attention_mask = inputs['attention_mask'][0]
    token_embeddings = outputs.last_hidden_state[0]
    mask_expanded = attention_mask.unsqueeze(-1).float()
    mean_pooled = (token_embeddings * mask_expanded).sum(0) / mask_expanded.sum(0)
    
    # Score: norma L2 do vetor mean-pooled
    # Pares semanticamente coerentes tendem a ativar mais neurônios
    score = mean_pooled.norm().cpu().item()
    
    return score


# ============================================================================
# PIPELINE RETRIEVE & RE-RANK
# ============================================================================

def retrieve_and_rerank(query, documentos, tokenizer_bi, model_bi, device_bi,
                        tokenizer_cross, model_cross, device_cross,
                        top_k_retrieval=10, top_k_final=5):
    """
    PIPELINE COMPLETO: Retrieve & Re-Rank (duas etapas).
    
    Este é o padrão usado em sistemas modernos de busca (Google, Bing, etc.)
    
    ┌─────────────────────────────────────────────────────────────────┐
    │ ETAPA 1: RETRIEVAL (Bi-Encoder)                                │
    │                                                                 │
    │   Query ──► [BERT] ──► vetor_q                                 │
    │                          │ cosine similarity                    │
    │   Docs  ──► [BERT] ──► vetores_d (pré-computados)             │
    │                          │                                      │
    │   Resultado: Top-K candidatos (rápido, ~ms)                    │
    └─────────────────────────┬───────────────────────────────────────┘
                              │ Top-K candidatos
                              ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ ETAPA 2: RE-RANKING (Cross-Encoder)                            │
    │                                                                 │
    │   Para cada candidato:                                          │
    │   [CLS] query [SEP] candidato [SEP] ──► [BERT] ──► score      │
    │                                                                 │
    │   Resultado: Top-N finais reordenados (preciso, ~100ms/par)    │
    └─────────────────────────────────────────────────────────────────┘
    
    Args:
        query: Texto da consulta
        documentos: Coleção completa de documentos
        top_k_retrieval: Quantos candidatos recuperar na Etapa 1
        top_k_final: Quantos resultados finais retornar
        
    Returns:
        tuple: (resultados_retrieval, resultados_rerank)
    """
    print(f"\n   📋 Etapa 1: Retrieval (Bi-Encoder) — buscando Top-{top_k_retrieval}...")
    t0 = time.time()
    
    # Etapa 1: Retrieval rápido com bi-encoder
    resultados_retrieval = biencoder_rankear(query, documentos, tokenizer_bi, model_bi, device_bi)
    candidatos = resultados_retrieval[:top_k_retrieval]
    
    t1 = time.time()
    print(f"      ✓ {len(candidatos)} candidatos recuperados ({t1-t0:.2f}s)")
    
    # Etapa 2: Re-ranking preciso com cross-encoder
    print(f"   🔬 Etapa 2: Re-Ranking (Cross-Encoder) — re-ordenando {len(candidatos)} candidatos...")
    
    docs_candidatos = [{"id": c["id"], "texto": c["texto"]} for c in candidatos]
    resultados_rerank = crossencoder_rankear(query, docs_candidatos, tokenizer_cross, model_cross, device_cross)
    
    t2 = time.time()
    print(f"      ✓ Re-ranking concluído ({t2-t1:.2f}s)")
    
    return resultados_retrieval[:top_k_final], resultados_rerank[:top_k_final]


# ============================================================================
# DEMONSTRAÇÃO: VISUALIZANDO A CROSS-ATTENTION
# ============================================================================

def demonstrar_tokens_par(query, documento, tokenizer):
    """
    Mostra como o tokenizer prepara a entrada do cross-encoder.
    
    Visualiza a diferença entre:
    - Bi-encoder: tokeniza query e doc SEPARADAMENTE
    - Cross-encoder: tokeniza como PAR (query, doc) JUNTOS
    """
    print(f"\n{'─'*70}")
    print("VISUALIZAÇÃO DA TOKENIZAÇÃO")
    print(f"{'─'*70}")
    
    # BI-ENCODER: codificação separada
    tokens_query = tokenizer.tokenize(query)
    tokens_doc = tokenizer.tokenize(documento)
    
    print(f"\n🔵 BI-ENCODER (separado):")
    print(f"   Query:     [CLS] {' '.join(tokens_query)} [SEP]")
    print(f"   Documento: [CLS] {' '.join(tokens_doc)} [SEP]")
    print(f"   → BERT processa CADA UM separadamente")
    print(f"   → Não há interação entre tokens de query e documento")
    
    # CROSS-ENCODER: codificação conjunta
    encoded = tokenizer(query, documento, return_tensors="pt")
    tokens_par = tokenizer.convert_ids_to_tokens(encoded['input_ids'][0])
    types = encoded['token_type_ids'][0].tolist()
    
    print(f"\n🟢 CROSS-ENCODER (junto):")
    print(f"   Tokens:     {' '.join(tokens_par)}")
    print(f"   Type IDs:   {' '.join(str(t) for t in types)}")
    print(f"               {'─'*40}")
    print(f"               0 = tokens da query")
    print(f"               1 = tokens do documento")
    print(f"   → BERT processa TUDO JUNTO com cross-attention!")
    print(f"   → Cada token pode 'olhar' para todos os outros tokens")
    
    # Conta de tokens
    n_query = sum(1 for t in types if t == 0) - 2  # -2 para [CLS] e [SEP]
    n_doc = sum(1 for t in types if t == 1) - 1    # -1 para [SEP] final
    n_total = len(tokens_par)
    
    print(f"\n   Estatísticas:")
    print(f"   Tokens da query:     {n_query}")
    print(f"   Tokens do documento: {n_doc}")
    print(f"   Total (com especiais): {n_total}")
    print(f"   Interações de attention: {n_total}² = {n_total**2} pares")


# ============================================================================
# EXIBIÇÃO DE RESULTADOS
# ============================================================================

def exibir_ranking(resultados, titulo, max_resultados=5):
    """Exibe ranking formatado"""
    print(f"\n   {titulo}")
    print(f"   {'─'*60}")
    for i, r in enumerate(resultados[:max_resultados], 1):
        print(f"   {i}. [Score: {r['score']:+.4f}] (doc {r['id']:2d}) {r['texto'][:55]}")


def exibir_comparacao(query, resultados_bi, resultados_cross, top_n=5):
    """Exibe comparação lado a lado entre bi-encoder e cross-encoder"""
    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO: BI-ENCODER vs CROSS-ENCODER")
    print(f"Consulta: \"{query}\"")
    print(f"{'='*70}")
    
    exibir_ranking(resultados_bi, "🔵 BI-ENCODER (separado → cosine)", top_n)
    exibir_ranking(resultados_cross, "🟢 CROSS-ENCODER (junto → score direto)", top_n)
    
    # Mostra mudanças de posição
    print(f"\n   📊 MUDANÇAS DE POSIÇÃO (Cross vs Bi):")
    print(f"   {'─'*60}")
    
    # Mapa de posição no bi-encoder
    pos_bi = {r["id"]: i+1 for i, r in enumerate(resultados_bi[:top_n])}
    
    for i, r in enumerate(resultados_cross[:top_n], 1):
        doc_id = r["id"]
        pos_anterior = pos_bi.get(doc_id, "—")
        if pos_anterior != "—":
            delta = pos_anterior - i
            if delta > 0:
                seta = f"↑ subiu {delta}"
            elif delta < 0:
                seta = f"↓ desceu {abs(delta)}"
            else:
                seta = "= manteve"
        else:
            seta = "★ novo no top-5"
        
        print(f"   doc {doc_id:2d}: Bi=#{pos_anterior} → Cross=#{i}  ({seta})")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("  CROSS-ENCODER COM BERTIMBAU PARA RE-RANKING DE BUSCA")
    print("=" * 70)
    print()
    print("Este script demonstra o modo CROSS-ENCODER do BERTimbau,")
    print("comparando com o modo BI-ENCODER para tarefas de busca.")
    print()
    print("Conceitos demonstrados:")
    print("  1. Diferença entre bi-encoder e cross-encoder")
    print("  2. Como a tokenização funciona para pares de sentenças")
    print("  3. Scoring de relevância com cross-encoder")
    print("  4. Pipeline Retrieve & Re-Rank (duas etapas)")
    print("  5. Comparação de rankings entre as duas abordagens")
    print()
    
    # ------------------------------------------------------------------
    # CARREGAMENTO DOS MODELOS
    # ------------------------------------------------------------------
    print("─" * 70)
    print("PASSO 1: CARREGANDO MODELOS")
    print("─" * 70)
    
    tokenizer_bi, model_bi, device_bi = carregar_bertimbau_biencoder()
    tokenizer_cross, model_cross, device_cross = carregar_bertimbau_crossencoder()
    
    # ------------------------------------------------------------------
    # DEMONSTRAÇÃO 1: TOKENIZAÇÃO DO PAR
    # ------------------------------------------------------------------
    print("\n" + "─" * 70)
    print("PASSO 2: COMO O CROSS-ENCODER TOKENIZA PARES")
    print("─" * 70)
    
    demonstrar_tokens_par(
        query="dano moral por atraso de voo",
        documento="indenização por cancelamento de passagem aérea",
        tokenizer=tokenizer_cross
    )
    
    # ------------------------------------------------------------------
    # DEMONSTRAÇÃO 2: SCORING DE PARES INDIVIDUAIS
    # ------------------------------------------------------------------
    print("\n" + "─" * 70)
    print("PASSO 3: SCORING DE PARES COM CROSS-ENCODER")
    print("─" * 70)
    print()
    print("Vamos ver como o cross-encoder pontua diferentes pares (query, doc).")
    print("Pares mais relevantes devem receber scores mais altos.")
    print()
    
    query_demo = "indenização por dano moral"
    pares_demo = [
        ("dano moral por ofensa à honra e dignidade da pessoa",              "Muito relevante"),
        ("danos morais por inscrição indevida em cadastro de inadimplentes", "Relevante"),
        ("responsabilidade civil do empregador por acidente de trabalho",    "Parcialmente relevante"),
        ("contrato de compra e venda de imóvel residencial urbano",          "Pouco relevante"),
        ("guarda compartilhada dos filhos após divórcio",                    "Irrelevante"),
    ]
    
    print(f"   Query: \"{query_demo}\"")
    print(f"   {'─'*60}")
    
    scores_demo = []
    for doc_texto, relevancia in pares_demo:
        score = crossencoder_score_par(
            query_demo, doc_texto,
            tokenizer_cross, model_cross, device_cross
        )
        scores_demo.append((doc_texto, relevancia, score))
    
    # Ordena por score
    scores_demo.sort(key=lambda x: x[2], reverse=True)
    
    for i, (doc_texto, relevancia, score) in enumerate(scores_demo, 1):
        print(f"   {i}. [Score: {score:+.4f}] ({relevancia})")
        print(f"      \"{doc_texto[:60]}\"")
    
    print()
    print("   💡 OBSERVAÇÃO:")
    print("   O modelo NÃO foi fine-tunado, então os scores absolutos")
    print("   não representam probabilidade de relevância. Em produção,")
    print("   faríamos fine-tuning com dados rotulados (ex: MS MARCO).")
    print("   O importante aqui é entender a ARQUITETURA e o PIPELINE.")
    
    # ------------------------------------------------------------------
    # DEMONSTRAÇÃO 3: RANKINGS COMPLETOS
    # ------------------------------------------------------------------
    print("\n" + "─" * 70)
    print("PASSO 4: RANKINGS COMPLETOS — BI-ENCODER vs CROSS-ENCODER")
    print("─" * 70)
    
    consultas = [
        "indenização por dano moral",
        "guarda dos filhos no divórcio",
        "dívida tributária e penhora de bens",
    ]
    
    for query in consultas:
        print(f"\n⏳ Processando: \"{query}\"...")
        
        resultados_bi = biencoder_rankear(
            query, DOCUMENTOS, tokenizer_bi, model_bi, device_bi
        )
        resultados_cross = crossencoder_rankear(
            query, DOCUMENTOS, tokenizer_cross, model_cross, device_cross
        )
        
        exibir_comparacao(query, resultados_bi, resultados_cross, top_n=5)
    
    # ------------------------------------------------------------------
    # DEMONSTRAÇÃO 4: PIPELINE RETRIEVE & RE-RANK
    # ------------------------------------------------------------------
    print("\n" + "─" * 70)
    print("PASSO 5: PIPELINE RETRIEVE & RE-RANK (duas etapas)")
    print("─" * 70)
    print()
    print("Em produção, o cross-encoder é usado como RE-RANKER:")
    print("  Etapa 1 (rápida): Bi-encoder ou BM25 recupera candidatos")
    print("  Etapa 2 (precisa): Cross-encoder re-ordena os candidatos")
    
    query_pipeline = "acidente de trabalho e responsabilidade"
    print(f"\n   Query: \"{query_pipeline}\"")
    
    resultados_ret, resultados_rer = retrieve_and_rerank(
        query_pipeline, DOCUMENTOS,
        tokenizer_bi, model_bi, device_bi,
        tokenizer_cross, model_cross, device_cross,
        top_k_retrieval=10,
        top_k_final=5
    )
    
    exibir_ranking(resultados_ret, "📋 Após Etapa 1 (Bi-Encoder Retrieval)")
    exibir_ranking(resultados_rer, "🔬 Após Etapa 2 (Cross-Encoder Re-Rank)")
    
    # ------------------------------------------------------------------
    # DEMONSTRAÇÃO 5: TRADE-OFF VELOCIDADE vs PRECISÃO
    # ------------------------------------------------------------------
    print("\n" + "─" * 70)
    print("PASSO 6: TRADE-OFF VELOCIDADE vs PRECISÃO")
    print("─" * 70)
    
    query_speed = "pensão alimentícia"
    n_docs = len(DOCUMENTOS)
    
    # Mede tempo do bi-encoder
    t0 = time.time()
    biencoder_rankear(query_speed, DOCUMENTOS, tokenizer_bi, model_bi, device_bi)
    tempo_bi = time.time() - t0
    
    # Mede tempo do cross-encoder
    t0 = time.time()
    crossencoder_rankear(query_speed, DOCUMENTOS, tokenizer_cross, model_cross, device_cross)
    tempo_cross = time.time() - t0
    
    print(f"""
   Query: "{query_speed}"
   Documentos: {n_docs}

   ┌────────────────────┬──────────────┬──────────────────────────┐
   │ Método             │ Tempo        │ Chamadas ao BERT         │
   ├────────────────────┼──────────────┼──────────────────────────┤
   │ Bi-Encoder         │ {tempo_bi:8.3f}s    │ 1 (query) + {n_docs} (docs)*    │
   │ Cross-Encoder      │ {tempo_cross:8.3f}s    │ {n_docs} (pares query+doc)     │
   └────────────────────┴──────────────┴──────────────────────────┘
   * Em produção, embeddings dos docs são pré-computados!
     Então o bi-encoder faz APENAS 1 chamada ao BERT (da query).
   
   ESCALABILIDADE:
   ┌──────────────────┬─────────────────┬─────────────────────────┐
   │ Cenário          │ Bi-Encoder      │ Cross-Encoder           │
   ├──────────────────┼─────────────────┼─────────────────────────┤
   │ 20 documentos    │ ~1 chamada BERT │ ~20 chamadas BERT       │
   │ 1.000 documentos │ ~1 chamada BERT │ ~1.000 chamadas BERT    │
   │ 1.000.000 docs   │ ~1 chamada BERT │ ~1.000.000 chamadas ⚠️  │
   └──────────────────┴─────────────────┴─────────────────────────┘
   
   → Por isso o cross-encoder é usado para RE-RANKING, não retrieval!
   → Pipeline ideal: Bi-Encoder (Top-100) → Cross-Encoder (Re-Rank 100)
""")
    
    # ------------------------------------------------------------------
    # RESUMO FINAL
    # ------------------------------------------------------------------
    print("=" * 70)
    print("RESUMO: QUANDO USAR CADA ABORDAGEM")
    print("=" * 70)
    print("""
   BI-ENCODER:
   ✓ Retrieval em grandes coleções (milhões de documentos)
   ✓ Quando precisa de resposta rápida (< 100ms)
   ✓ Embeddings podem ser pré-computados e indexados (ex: ElasticSearch)
   ✗ Menos preciso (não captura interações query-documento)

   CROSS-ENCODER:
   ✓ Re-ranking de candidatos pré-selecionados (dezenas/centenas)
   ✓ Quando precisão é mais importante que velocidade
   ✓ Captura interações semânticas cruzadas entre query e documento
   ✗ Lento para grandes coleções (O(N) chamadas ao BERT por query)

   PIPELINE IDEAL (Retrieve & Re-Rank):
   ✓ Combina o melhor dos dois mundos
   ✓ Bi-Encoder ou BM25 para retrieval rápido (Etapa 1)
   ✓ Cross-Encoder para re-ranking preciso (Etapa 2)
   ✓ Usado por Google, Bing, e sistemas modernos de busca
""")
    
    print("🎓 EXERCÍCIOS SUGERIDOS:")
    print("  1. Adicione mais documentos e observe o impacto no tempo")
    print("  2. Varie as consultas e compare os rankings")
    print("  3. Teste com consultas ambíguas (ex: 'banco' → financeiro ou assento?)")
    print("  4. Implemente fine-tuning do cross-encoder com dados rotulados")
    print("  5. Integre com ElasticSearch: BM25 (Etapa 1) + Cross-Encoder (Etapa 2)")
    print()
    print("📚 REFERÊNCIAS:")
    print("  - BERTimbau: https://github.com/neuralmind-ai/portuguese-bert")
    print("  - Cross-Encoders: https://www.sbert.net/examples/applications/cross-encoder/README.html")
    print("  - Retrieve & Re-Rank: https://arxiv.org/abs/2010.11934")
    print("  - MS MARCO (dataset): https://microsoft.github.io/msmarco/")


if __name__ == "__main__":
    main()
