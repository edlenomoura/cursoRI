#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
FINE-TUNING DE BI-ENCODER COM BERTIMBAU
================================================================================

Este script demonstra como fazer fine-tuning do BERTimbau no modo BI-ENCODER
para busca semântica no domínio jurídico.

================================================================================
RELEMBRANDO: BI-ENCODER vs CROSS-ENCODER
================================================================================

BI-ENCODER (este script):
   Query ──► [BERT] ──► vetor_q ─┐
                                   ├── cosine(vetor_q, vetor_d) ──► score
   Doc   ──► [BERT] ──► vetor_d ─┘
   
   • Query e documento codificados SEPARADAMENTE
   • Vetores dos documentos podem ser PRÉ-COMPUTADOS → busca rápida
   • Fine-tuning: treina o BERT para produzir vetores bons para cosine

CROSS-ENCODER (finetuneCrossEncoder.py):
   [CLS] Query [SEP] Doc [SEP] ──► [BERT] ──► score
   
   • Mais preciso, mas NÃO permite pré-computar
   • Usado para re-ranking (poucos candidatos)

================================================================================
POR QUE FAZER FINE-TUNING DO BI-ENCODER?
================================================================================

BERT pré-treinado (sem fine-tuning):
- O token [CLS] NÃO foi treinado para similaridade semântica
- Vetores [CLS] de textos semanticamente similares NÃO ficam próximos
- É como pedir para alguém resumir textos sem nunca ter praticado

DEPOIS do fine-tuning:
- O [CLS] de textos similares fica PRÓXIMO no espaço vetorial
- O [CLS] de textos diferentes fica DISTANTE
- Agora o modelo "entende" que sinônimos e paráfrases são similares

   Espaço vetorial ANTES:              Espaço vetorial DEPOIS:
   (vetores aleatórios)                (vetores organizados por semântica)
   
   • dano moral                        • dano moral ─────┐
   • contrato           • alimentos    • danos morais ───┤ cluster
        • prisão                        • ofensa honra ──┘
   • danos morais                       
             • ofensa honra             • contrato ──────┐
                                        • compra venda ──┤ cluster
                                        • aluguel ───────┘

================================================================================
ESTRATÉGIA DE TREINAMENTO: TRIPLET LOSS vs CONTRASTIVE vs MNRL
================================================================================

Existem várias formas de treinar um bi-encoder. Neste script usamos
MULTIPLE NEGATIVES RANKING LOSS (MNRL) — a mais popular e eficiente:

MNRL (Multiple Negatives Ranking Loss):
──────────────────────────────────────────
- Cada exemplo de treino é um par (query, doc_positivo)
- Os doc_positivos de OUTRAS queries no batch servem como NEGATIVOS
- O modelo aprende a maximizar cosine(q, doc+) e minimizar cosine(q, doc-)

Exemplo com batch de 3 pares:
┌────────────────────────────┬─────────────────────────────────────┐
│ Query                      │ Documento Positivo                  │
├────────────────────────────┼─────────────────────────────────────┤
│ q1: "dano moral"           │ d1: "ofensa à honra e dignidade"    │  ← par positivo
│ q2: "acidente trabalho"    │ d2: "lesão durante jornada laboral" │  ← par positivo
│ q3: "pensão alimentícia"   │ d3: "sustento dos filhos menores"   │  ← par positivo
└────────────────────────────┴─────────────────────────────────────┘

Matriz de similaridade (cosine):
              d1      d2      d3
   q1      [ 0.9✓   0.1     0.2  ]   → maximizar diagonal (positivos)
   q2      [ 0.1    0.8✓    0.15 ]   → minimizar fora da diagonal (negativos)
   q3      [ 0.2    0.1     0.85✓]

VANTAGENS DO MNRL:
- NÃO precisa de negativos explícitos (usa o próprio batch!)
- Cada batch de N pares gera N positivos + N×(N-1) negativos
- Muito eficiente em dados

ALTERNATIVAS (não usadas aqui, mas para referência):
- Triplet Loss: (anchor, positive, negative) → requer negativos explícitos
- Contrastive Loss: (par, label) → 1=similar, 0=dissimilar
- InfoNCE: similar ao MNRL, base do SimCLR/CLIP

================================================================================
NESTE SCRIPT — EXEMPLO DIDÁTICO
================================================================================

Usamos pares (query, documento_relevante) do domínio jurídico.
O MNRL usa os docs de outras queries como negativos automaticamente.

Dataset PEQUENO para fins didáticos. Em produção:
- Use centenas de milhares de pares
- Considere hard negatives (negativos difíceis, quasi-relevantes)
- Use datasets como MS MARCO, NQ, ou dados de logs de busca

================================================================================
"""

import time
import copy
import warnings
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, AdamW

warnings.filterwarnings("ignore", message=".*resume_download.*", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*AdamW.*", category=FutureWarning)

BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"


# ============================================================================
# PASSO 1: DADOS DE TREINAMENTO
# ============================================================================
#
# Para MNRL, cada exemplo é um par (query, documento_relevante).
# NÃO precisamos de negativos explícitos — o próprio batch os fornece.
#
# Em produção, esses pares viriam de:
#   - Clicks em resultados de busca (query → doc clicado)
#   - Anotação humana (juízes marcando docs relevantes)
#   - Datasets públicos (MS MARCO, etc.)
#
# ============================================================================

DADOS_TREINAMENTO = [
    # ── Tema: Dano Moral ──
    {"query": "dano moral",
     "doc_positivo": "dano moral por ofensa à honra e dignidade da pessoa"},
    {"query": "indenização por danos morais",
     "doc_positivo": "danos morais por inscrição indevida em cadastro de inadimplentes"},
    {"query": "reparação moral",
     "doc_positivo": "indenização por abalo moral decorrente de falha na prestação de serviço"},
    {"query": "dano extrapatrimonial",
     "doc_positivo": "reparação por dano extrapatrimonial em relação de consumo"},

    # ── Tema: Acidente de Trabalho ──
    {"query": "acidente de trabalho",
     "doc_positivo": "responsabilidade civil do empregador por acidente de trabalho"},
    {"query": "doença ocupacional",
     "doc_positivo": "indenização por doença ocupacional equiparada a acidente laboral"},
    {"query": "acidente no serviço",
     "doc_positivo": "estabilidade provisória do empregado acidentado no serviço"},
    {"query": "lesão no trabalho",
     "doc_positivo": "nexo causal entre atividade laboral e lesão corporal do trabalhador"},

    # ── Tema: Família / Alimentos ──
    {"query": "pensão alimentícia",
     "doc_positivo": "pensão alimentícia para filho menor de idade"},
    {"query": "alimentos para filho",
     "doc_positivo": "revisão de alimentos fixados em sentença judicial"},
    {"query": "guarda dos filhos",
     "doc_positivo": "guarda compartilhada dos filhos após divórcio"},
    {"query": "divórcio e partilha",
     "doc_positivo": "partilha de bens do casal em processo de inventário"},

    # ── Tema: Contratos ──
    {"query": "contrato bancário abusivo",
     "doc_positivo": "revisão de contrato bancário com juros abusivos"},
    {"query": "cláusula abusiva",
     "doc_positivo": "nulidade de cláusulas abusivas em contrato de empréstimo consignado"},
    {"query": "compra e venda de imóvel",
     "doc_positivo": "contrato de compra e venda de imóvel residencial urbano"},
    {"query": "rescisão contratual",
     "doc_positivo": "rescisão indireta do contrato de trabalho por justa causa do empregador"},

    # ── Tema: Penal / Processual ──
    {"query": "prisão ilegal",
     "doc_positivo": "habeas corpus contra prisão preventiva ilegal"},
    {"query": "preso ilegalmente",
     "doc_positivo": "relaxamento de prisão em flagrante por vício formal"},
    {"query": "mandado de segurança",
     "doc_positivo": "mandado de segurança contra ato de autoridade pública"},
    {"query": "recurso contra sentença",
     "doc_positivo": "recurso de apelação contra sentença de primeiro grau"},

    # ── Tema: Execução ──
    {"query": "execução fiscal",
     "doc_positivo": "execução fiscal de dívida tributária municipal"},
    {"query": "penhora de bens",
     "doc_positivo": "penhora de bens do devedor para garantia da execução"},
    {"query": "cumprimento de sentença",
     "doc_positivo": "impugnação ao cumprimento de sentença por excesso de execução"},
    {"query": "embargos à execução",
     "doc_positivo": "embargos de declaração por omissão na sentença"},

    # ── Tema: Previdenciário / Saúde ──
    {"query": "aposentadoria por invalidez",
     "doc_positivo": "aposentadoria por invalidez junto ao INSS"},
    {"query": "tutela de urgência saúde",
     "doc_positivo": "tutela antecipada de urgência em ação de saúde"},
    {"query": "despejo por falta de pagamento",
     "doc_positivo": "ação de despejo por falta de pagamento de aluguel"},
    {"query": "usucapião de imóvel",
     "doc_positivo": "usucapião extraordinária de bem imóvel rural"},
]

# Dados de VALIDAÇÃO — pares novos que o modelo NÃO vê no treino
DADOS_VALIDACAO = [
    {"query": "dano à honra",
     "doc_positivo": "compensação por sofrimento psíquico causado por conduta ilícita"},
    {"query": "acidente laboral",
     "doc_positivo": "empregado sofreu lesão durante jornada de trabalho na empresa"},
    {"query": "alimentos ao filho",
     "doc_positivo": "pai obrigado a pagar pensão mensal para sustento dos filhos"},
    {"query": "juros abusivos",
     "doc_positivo": "revisão judicial de taxa de juros em contrato de financiamento"},
    {"query": "prisão preventiva",
     "doc_positivo": "revogação de prisão preventiva por ausência de fundamentação"},
    {"query": "penhora online",
     "doc_positivo": "bloqueio judicial de conta bancária para satisfação do crédito"},
]


# ============================================================================
# PASSO 2: DATASET PYTORCH
# ============================================================================

class DatasetBiEncoder(Dataset):
    """
    Dataset para fine-tuning do bi-encoder.
    
    Diferença crucial em relação ao cross-encoder:
    
    CROSS-ENCODER:
      - Tokeniza JUNTO: [CLS] query [SEP] documento [SEP]
      - Retorna UM tensor com o par concatenado
    
    BI-ENCODER:
      - Tokeniza SEPARADO: query e documento são tokens INDEPENDENTES
      - Retorna DOIS tensores: um para query, outro para documento
      - Cada um é processado separadamente pelo BERT
    """
    
    def __init__(self, dados, tokenizer, max_length=64):
        """
        Args:
            dados: Lista de dicts com 'query' e 'doc_positivo'
            tokenizer: Tokenizer do BERTimbau
            max_length: Max tokens (64 é suficiente para textos curtos)
        """
        self.dados = dados
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.dados)
    
    def __getitem__(self, idx):
        """
        Retorna query e documento tokenizados SEPARADAMENTE.
        
        Query:     [CLS] tok1 tok2 [SEP] [PAD] [PAD]   ← processada sozinha
        Documento: [CLS] tok3 tok4 tok5 [SEP] [PAD]    ← processado sozinho
        
        Cada um vai gerar seu próprio embedding [CLS] independente.
        """
        exemplo = self.dados[idx]
        
        # Tokeniza QUERY (separadamente)
        query_enc = self.tokenizer(
            exemplo["query"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Tokeniza DOCUMENTO (separadamente)
        doc_enc = self.tokenizer(
            exemplo["doc_positivo"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "query_input_ids": query_enc["input_ids"].squeeze(0),
            "query_attention_mask": query_enc["attention_mask"].squeeze(0),
            "doc_input_ids": doc_enc["input_ids"].squeeze(0),
            "doc_attention_mask": doc_enc["attention_mask"].squeeze(0),
        }


# ============================================================================
# PASSO 3: MODELO BI-ENCODER
# ============================================================================

class BiEncoderModel(nn.Module):
    """
    Modelo Bi-Encoder para busca semântica.
    
    ARQUITETURA:
    ┌──────────────────────────────────────────────────────────┐
    │  Q: [CLS] query [SEP]  ──► BERT ──► [CLS] ──► vetor_q  │
    │                                                          │
    │  D: [CLS] doc [SEP]    ──► BERT ──► [CLS] ──► vetor_d  │
    │                                MESMO BERT                │
    │                           (pesos compartilhados!)        │
    └──────────────────────────────────────────────────────────┘
    
    PESOS COMPARTILHADOS:
    Usamos o MESMO BERT para query e documento.
    Isso é chamado de "tied weights" ou "siamese network".
    
    Vantagens:
    - Metade dos parâmetros (1 BERT, não 2)
    - Query e documento vivem no MESMO espaço vetorial
    - Cosine similarity é válido entre quaisquer textos
    
    POOLING:
    O BERT retorna um vetor para CADA token. Precisamos de UM vetor
    por texto. Estratégias:
    - [CLS] token: usa o primeiro token como representação
    - Mean pooling: média de todos os tokens (geralmente melhor!)
    - Max pooling: máximo por dimensão
    
    Usamos MEAN POOLING neste exemplo (melhor para sentence embeddings).
    """
    
    def __init__(self, model_name):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
    
    def mean_pooling(self, model_output, attention_mask):
        """
        Mean Pooling: média ponderada dos hidden states.
        
        Por que NÃO usar simplesmente a média de todos os tokens?
        Porque tokens de PADDING devem ser IGNORADOS!
        
        Processo:
        1. Pega hidden states de todos os tokens
        2. Multiplica pela attention_mask (0 para PAD, 1 para real)
        3. Soma e divide pelo número de tokens reais
        
        Exemplo:
        hidden_states: [[0.1, 0.2], [0.3, 0.4], [0.0, 0.0]]  (último é PAD)
        attention_mask: [1, 1, 0]
        
        soma = [0.1+0.3, 0.2+0.4] = [0.4, 0.6]
        contagem = 2
        média = [0.2, 0.3] ← ignora o PAD!
        """
        token_embeddings = model_output.last_hidden_state  # [batch, seq_len, 768]
        mask_expanded = attention_mask.unsqueeze(-1).float()  # [batch, seq_len, 1]
        
        # Soma ponderada: só tokens reais (não-PAD)
        sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
        # Contagem de tokens reais por exemplo
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        
        # Média
        return sum_embeddings / sum_mask  # [batch, 768]
    
    def encode(self, input_ids, attention_mask):
        """
        Codifica um lote de textos em vetores.
        
        Usado tanto para queries quanto para documentos
        (mesmo BERT, mesma função).
        """
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        embeddings = self.mean_pooling(outputs, attention_mask)
        
        # Normaliza para norma unitária → cosine vira dot product
        # ||v|| = 1 → cos(a,b) = a·b / (||a|| × ||b||) = a·b
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings  # [batch, 768], cada vetor com norma = 1
    
    def forward(self, query_input_ids, query_attention_mask,
                doc_input_ids, doc_attention_mask):
        """
        Forward pass: codifica queries e documentos separadamente.
        
        Returns:
            query_embeddings: [batch, 768]
            doc_embeddings: [batch, 768]
        """
        query_embeddings = self.encode(query_input_ids, query_attention_mask)
        doc_embeddings = self.encode(doc_input_ids, doc_attention_mask)
        
        return query_embeddings, doc_embeddings


# ============================================================================
# PASSO 4: MULTIPLE NEGATIVES RANKING LOSS (MNRL)
# ============================================================================

class MultipleNegativesRankingLoss(nn.Module):
    """
    MNRL: A loss mais popular para treinar bi-encoders.
    
    IDEIA CENTRAL:
    Dado um batch de N pares (query_i, doc_positivo_i):
    - query_i deve ser SIMILAR ao doc_positivo_i (diagonal da matriz)
    - query_i deve ser DISSIMILAR a doc_positivo_j para j≠i (fora da diagonal)
    
    FUNCIONAMENTO:
    
    1. Calcula matriz de similaridade NxN:
    
       similarity[i][j] = cosine(query_i, doc_j)
    
                  doc_1   doc_2   doc_3   doc_4
       query_1  [ 0.9✓    0.1     0.2     0.05 ]
       query_2  [ 0.15    0.85✓   0.1     0.2  ]
       query_3  [ 0.1     0.2     0.88✓   0.15 ]
       query_4  [ 0.05    0.1     0.15    0.9✓ ]
    
    2. Aplica Cross-Entropy Loss:
       - Labels = [0, 1, 2, 3] (diagonal = classe correta)
       - A diagonal deve ter os maiores valores
       - Loss = CrossEntropyLoss(similarity_matrix, labels)
    
    3. O modelo aprende a:
       - MAXIMIZAR diagonal (pares positivos)
       - MINIMIZAR fora da diagonal (pares negativos)
    
    ESCALA (temperature):
    - Multiplica similaridades por 1/temperature antes do softmax
    - Temperature baixa (ex: 0.05) → distribuição mais "afiada"
    - Temperature alta (ex: 1.0) → distribuição mais "suave"
    - Padrão: 0.05 (funciona bem na prática)
    
    POR QUE FUNCIONA TÃO BEM?
    - Com batch de N=32: cada query ganha 31 negativos "de graça"
    - Não precisa coletar negativos explícitos
    - Negativos são documentos de OUTRAS queries (naturalmente diferentes)
    """
    
    def __init__(self, temperature=0.05):
        super().__init__()
        self.temperature = temperature
        self.cross_entropy = nn.CrossEntropyLoss()
    
    def forward(self, query_embeddings, doc_embeddings):
        """
        Calcula MNRL.
        
        Args:
            query_embeddings: [batch, 768] — vetores das queries
            doc_embeddings: [batch, 768] — vetores dos docs positivos
            
        Returns:
            loss: escalar — valor da loss
        """
        # Matriz de similaridade: [batch, batch]
        # Como os vetores são normalizados, dot product = cosine similarity
        similarity_matrix = torch.matmul(
            query_embeddings, doc_embeddings.T
        ) / self.temperature
        
        # Labels: diagonal = classe correta
        # query_0 → doc_0 (label=0), query_1 → doc_1 (label=1), ...
        batch_size = query_embeddings.size(0)
        labels = torch.arange(batch_size, device=query_embeddings.device)
        
        # Cross-Entropy: maximiza diagonal, minimiza fora
        loss = self.cross_entropy(similarity_matrix, labels)
        
        return loss


# ============================================================================
# PASSO 5: FUNÇÕES DE TREINAMENTO
# ============================================================================

def treinar_uma_epoca(model, dataloader, optimizer, loss_fn, device, epoca_num):
    """
    Treina o bi-encoder por uma época.
    
    DIFERENÇA DO CROSS-ENCODER:
    
    Cross-encoder: [CLS] query [SEP] doc [SEP] → BERT → score único
    Bi-encoder:    query → BERT → vetor_q
                   doc   → BERT → vetor_d      → MNRL(vetor_q, vetor_d)
    
    O BERT é chamado DUAS vezes por exemplo (query + doc),
    mas os vetores de docs podem ser pré-computados em produção.
    """
    model.train()
    loss_total = 0.0
    n_batches = 0
    
    for batch in dataloader:
        # Move para device
        q_ids = batch["query_input_ids"].to(device)
        q_mask = batch["query_attention_mask"].to(device)
        d_ids = batch["doc_input_ids"].to(device)
        d_mask = batch["doc_attention_mask"].to(device)
        
        # Forward: codifica queries e docs SEPARADAMENTE
        query_embs, doc_embs = model(q_ids, q_mask, d_ids, d_mask)
        
        # MNRL: usa o batch inteiro para gerar positivos e negativos
        loss = loss_fn(query_embs, doc_embs)
        
        # Backward + update
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        loss_total += loss.item()
        n_batches += 1
    
    return loss_total / n_batches


def avaliar_recall(model, tokenizer, device, dados_val, todos_docs, top_k=5):
    """
    Avalia o bi-encoder com Recall@K nos dados de validação.
    
    RECALL@K:
    - Para cada query de validação, rankeia TODOS os documentos
    - Verifica se o documento correto está no Top-K
    - Recall@K = (queries com doc correto no top-K) / (total de queries)
    
    Exemplo:
    - Query: "dano à honra"
    - Doc correto: "compensação por sofrimento psíquico..."
    - Top-5 retornados: [..., "compensação por sofrimento...", ...]
    - Se doc correto está no top-5 → acerto!
    
    Args:
        model: BiEncoderModel
        tokenizer: Tokenizer
        device: 'cuda' ou 'cpu'
        dados_val: Dados de validação
        todos_docs: Lista de TODOS os documentos para ranquear
        top_k: K para Recall@K
        
    Returns:
        float: Recall@K (0.0 a 1.0)
    """
    model.eval()
    
    with torch.no_grad():
        # Codifica todos os documentos candidatos
        doc_embeddings = []
        for doc in todos_docs:
            enc = tokenizer(doc, return_tensors="pt", truncation=True,
                          max_length=64, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model.bert(**enc)
            # Mean pooling
            mask = enc["attention_mask"].unsqueeze(-1).float()
            emb = (out.last_hidden_state * mask).sum(1) / mask.sum(1)
            emb = F.normalize(emb, p=2, dim=1)
            doc_embeddings.append(emb[0])
        
        doc_matrix = torch.stack(doc_embeddings)  # [n_docs, 768]
        
        acertos = 0
        for exemplo in dados_val:
            # Codifica query
            enc = tokenizer(exemplo["query"], return_tensors="pt",
                          truncation=True, max_length=64, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model.bert(**enc)
            mask = enc["attention_mask"].unsqueeze(-1).float()
            q_emb = (out.last_hidden_state * mask).sum(1) / mask.sum(1)
            q_emb = F.normalize(q_emb, p=2, dim=1)
            
            # Calcula similaridade com todos os docs
            sims = torch.matmul(q_emb, doc_matrix.T)[0]
            top_indices = sims.argsort(descending=True)[:top_k].tolist()
            
            # Verifica se o doc positivo está no top-K
            doc_correto = exemplo["doc_positivo"]
            top_docs = [todos_docs[i] for i in top_indices]
            if doc_correto in top_docs:
                acertos += 1
        
        recall = acertos / len(dados_val)
    
    return recall


def computar_similaridades(model, tokenizer, device, query, documentos):
    """
    Computa similaridade cosseno entre uma query e uma lista de documentos.
    Usado para visualização antes/depois do fine-tuning.
    """
    model.eval()
    resultados = []
    
    with torch.no_grad():
        # Codifica query
        q_enc = tokenizer(query, return_tensors="pt", truncation=True,
                         max_length=64, padding=True)
        q_enc = {k: v.to(device) for k, v in q_enc.items()}
        q_out = model.bert(**q_enc)
        q_mask = q_enc["attention_mask"].unsqueeze(-1).float()
        q_emb = (q_out.last_hidden_state * q_mask).sum(1) / q_mask.sum(1)
        q_emb = F.normalize(q_emb, p=2, dim=1)[0]
        
        for doc in documentos:
            d_enc = tokenizer(doc, return_tensors="pt", truncation=True,
                            max_length=64, padding=True)
            d_enc = {k: v.to(device) for k, v in d_enc.items()}
            d_out = model.bert(**d_enc)
            d_mask = d_enc["attention_mask"].unsqueeze(-1).float()
            d_emb = (d_out.last_hidden_state * d_mask).sum(1) / d_mask.sum(1)
            d_emb = F.normalize(d_emb, p=2, dim=1)[0]
            
            sim = torch.dot(q_emb, d_emb).item()
            resultados.append({"doc": doc, "score": sim})
    
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados


# ============================================================================
# PASSO 6: FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def mostrar_matriz_similaridade(model, tokenizer, device, queries, docs, titulo):
    """
    Mostra a matriz de similaridade entre queries e documentos.
    A diagonal deve ter os maiores valores (pares corretos).
    """
    model.eval()
    n = min(len(queries), len(docs), 6)  # Limita para caber na tela
    
    print(f"\n   {titulo}")
    print(f"   {'─'*60}")
    
    with torch.no_grad():
        # Codifica queries
        q_embs = []
        for q in queries[:n]:
            enc = tokenizer(q, return_tensors="pt", truncation=True,
                          max_length=64, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model.bert(**enc)
            mask = enc["attention_mask"].unsqueeze(-1).float()
            emb = (out.last_hidden_state * mask).sum(1) / mask.sum(1)
            emb = F.normalize(emb, p=2, dim=1)
            q_embs.append(emb[0])
        
        # Codifica docs
        d_embs = []
        for d in docs[:n]:
            enc = tokenizer(d, return_tensors="pt", truncation=True,
                          max_length=64, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model.bert(**enc)
            mask = enc["attention_mask"].unsqueeze(-1).float()
            emb = (out.last_hidden_state * mask).sum(1) / mask.sum(1)
            emb = F.normalize(emb, p=2, dim=1)
            d_embs.append(emb[0])
        
        q_matrix = torch.stack(q_embs)
        d_matrix = torch.stack(d_embs)
        sim_matrix = torch.matmul(q_matrix, d_matrix.T).cpu().numpy()
    
    # Header
    print(f"   {'':>25}", end="")
    for j in range(n):
        print(f"  d{j+1:d}   ", end="")
    print()
    
    for i in range(n):
        q_label = queries[i][:22].ljust(25)
        print(f"   {q_label}", end="")
        for j in range(n):
            val = sim_matrix[i][j]
            marker = " ✓" if i == j else "  "
            print(f" {val:.3f}{marker}", end="")
        print()
    
    # Estatística da diagonal
    diag = [sim_matrix[i][i] for i in range(n)]
    off_diag = [sim_matrix[i][j] for i in range(n) for j in range(n) if i != j]
    print(f"\n   Diagonal (positivos) média:  {np.mean(diag):.4f}")
    print(f"   Fora diagonal (neg.) média:  {np.mean(off_diag):.4f}")
    print(f"   Diferença (quanto maior, melhor): {np.mean(diag) - np.mean(off_diag):.4f}")


def mostrar_evolucao(historico):
    """Gráfico ASCII da evolução da loss."""
    print(f"\n   📉 EVOLUÇÃO DA LOSS:")
    print(f"   {'─'*55}")
    
    max_loss = max(h["loss"] for h in historico)
    largura = 40
    
    for h in historico:
        tam = int((h["loss"] / max_loss) * largura)
        barra = "█" * tam + "░" * (largura - tam)
        recall_str = f"R@5:{h['recall']:.0%}" if h['recall'] is not None else "     "
        print(f"   Época {h['epoca']:2d} │{barra}│ "
              f"Loss:{h['loss']:.4f} {recall_str}")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("  FINE-TUNING DE BI-ENCODER COM BERTIMBAU")
    print("=" * 70)
    print()
    print("Este script demonstra como treinar o BERTimbau no modo bi-encoder")
    print("para busca semântica, usando Multiple Negatives Ranking Loss (MNRL).")
    print()
    print("Pipeline:")
    print("  1. Preparar pares (query, documento_relevante)")
    print("  2. Carregar BERTimbau base (sem camada de classificação)")
    print("  3. Avaliar ANTES do fine-tuning (baseline)")
    print("  4. Treinar com MNRL por algumas épocas")
    print("  5. Avaliar DEPOIS e comparar rankings")
    print()
    
    # ------------------------------------------------------------------
    # PASSO 1: DADOS
    # ------------------------------------------------------------------
    print("─" * 70)
    print("PASSO 1: DADOS DE TREINAMENTO")
    print("─" * 70)
    
    print(f"\n   Pares de treinamento:  {len(DADOS_TREINAMENTO)}")
    print(f"   Pares de validação:    {len(DADOS_VALIDACAO)}")
    
    print(f"\n   Cada exemplo é um par (query, doc_positivo).")
    print(f"   Negativos são gerados AUTOMATICAMENTE pelo MNRL dentro do batch.")
    print(f"\n   Exemplos:")
    print(f"   {'─'*60}")
    for d in DADOS_TREINAMENTO[:4]:
        print(f"   Q: \"{d['query'][:30]}\"  →  D: \"{d['doc_positivo'][:45]}\"")
    print(f"   ... ({len(DADOS_TREINAMENTO) - 4} mais)")
    
    # Coletamos todos os docs para avaliação (retrieval sobre todos)
    todos_docs = list(set(
        [d["doc_positivo"] for d in DADOS_TREINAMENTO] +
        [d["doc_positivo"] for d in DADOS_VALIDACAO]
    ))
    print(f"\n   Total de documentos únicos (para retrieval): {len(todos_docs)}")
    
    # ------------------------------------------------------------------
    # PASSO 2: MODELO
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 2: CARREGANDO BERTIMBAU (BI-ENCODER)")
    print("─" * 70)
    
    print("\n📥 Carregando tokenizer e modelo...")
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    model = BiEncoderModel(BERTIMBAU_MODEL)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   ✓ Modelo: {BERTIMBAU_MODEL}")
    print(f"   ✓ Device: {device}")
    print(f"   ✓ Arquitetura: BERT base (768 dims) + Mean Pooling + L2 Norm")
    print(f"   ✓ Parâmetros: {total_params:,}")
    print(f"\n   NOTA: Diferente do cross-encoder, aqui NÃO adicionamos")
    print(f"         camada linear. O fine-tuning ajusta o BERT para")
    print(f"         produzir embeddings melhores para cosine similarity.")
    
    # Cópia antes do fine-tuning
    model_antes = copy.deepcopy(model)
    model_antes.eval()
    
    # ------------------------------------------------------------------
    # PASSO 3: AVALIAÇÃO ANTES DO FINE-TUNING
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 3: AVALIAÇÃO ANTES DO FINE-TUNING (Baseline)")
    print("─" * 70)
    print()
    print("   O BERT pré-treinado NÃO foi otimizado para similaridade.")
    print("   Os embeddings [CLS] / mean-pooled NÃO organizam bem")
    print("   documentos por relevância semântica (ainda).")
    
    # Matriz de similaridade
    queries_viz = [d["query"] for d in DADOS_TREINAMENTO[:6]]
    docs_viz = [d["doc_positivo"] for d in DADOS_TREINAMENTO[:6]]
    
    mostrar_matriz_similaridade(
        model, tokenizer, device, queries_viz, docs_viz,
        "Matriz de similaridade ANTES do fine-tuning:"
    )
    
    # Recall@5 antes
    recall_antes = avaliar_recall(model, tokenizer, device, DADOS_VALIDACAO,
                                  todos_docs, top_k=5)
    print(f"\n   📊 Recall@5 ANTES: {recall_antes:.0%}"
          f" ({int(recall_antes * len(DADOS_VALIDACAO))}/{len(DADOS_VALIDACAO)} queries)")
    
    # Ranking de exemplo antes
    query_demo = "reparação por dano moral"
    docs_demo = [
        "dano moral por ofensa à honra e dignidade da pessoa",
        "compensação por sofrimento psíquico causado por conduta ilícita",
        "responsabilidade civil do empregador por acidente de trabalho",
        "contrato de compra e venda de imóvel residencial urbano",
        "guarda compartilhada dos filhos após divórcio",
        "habeas corpus contra prisão preventiva ilegal",
    ]
    
    print(f"\n   Ranking para: \"{query_demo}\"")
    ranking_antes = computar_similaridades(model, tokenizer, device, query_demo, docs_demo)
    for i, r in enumerate(ranking_antes, 1):
        print(f"   {i}. [{r['score']:.4f}] {r['doc'][:55]}")
    
    # ------------------------------------------------------------------
    # PASSO 4: CONFIGURAÇÃO DO TREINAMENTO
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 4: CONFIGURAÇÃO DO TREINAMENTO")
    print("─" * 70)
    
    BATCH_SIZE = 8
    LEARNING_RATE = 2e-5
    NUM_EPOCAS = 15
    TEMPERATURE = 0.05
    
    dataset_treino = DatasetBiEncoder(DADOS_TREINAMENTO, tokenizer, max_length=64)
    loader_treino = DataLoader(dataset_treino, batch_size=BATCH_SIZE, shuffle=True)
    
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    loss_fn = MultipleNegativesRankingLoss(temperature=TEMPERATURE)
    
    print(f"""
   ✓ Batch size:    {BATCH_SIZE}
   ✓ Learning rate: {LEARNING_RATE}
   ✓ Épocas:        {NUM_EPOCAS}
   ✓ Temperature:   {TEMPERATURE}
   ✓ Loss:          Multiple Negatives Ranking Loss (MNRL)
   ✓ Pooling:       Mean Pooling + L2 Normalize
   
   COM BATCH_SIZE = {BATCH_SIZE}:
   Cada batch gera:
   - {BATCH_SIZE} pares POSITIVOS (query_i, doc_i) — da diagonal
   - {BATCH_SIZE} × {BATCH_SIZE - 1} = {BATCH_SIZE * (BATCH_SIZE - 1)} pares NEGATIVOS (query_i, doc_j) — fora da diagonal
   Total de sinais de treino por batch: {BATCH_SIZE * BATCH_SIZE}
""")
    
    # ------------------------------------------------------------------
    # PASSO 5: TREINAMENTO
    # ------------------------------------------------------------------
    print("─" * 70)
    print("PASSO 5: TREINAMENTO (Fine-Tuning com MNRL)")
    print("─" * 70)
    print()
    print("   Início do treinamento...")
    print(f"   {'─'*55}")
    
    historico = []
    
    for epoca in range(1, NUM_EPOCAS + 1):
        t0 = time.time()
        
        loss = treinar_uma_epoca(model, loader_treino, optimizer, loss_fn, device, epoca)
        
        # Avalia Recall@5 a cada 3 épocas (para não demorar muito)
        recall = None
        if epoca % 3 == 0 or epoca == NUM_EPOCAS:
            recall = avaliar_recall(model, tokenizer, device, DADOS_VALIDACAO,
                                    todos_docs, top_k=5)
        
        tempo = time.time() - t0
        
        historico.append({
            "epoca": epoca,
            "loss": loss,
            "recall": recall,
            "tempo": tempo
        })
        
        recall_str = f"Recall@5: {recall:.0%}" if recall is not None else ""
        print(f"   Época {epoca:2d}/{NUM_EPOCAS} │ "
              f"Loss: {loss:.4f} │ "
              f"{recall_str:>15} │ "
              f"{tempo:.1f}s")
    
    mostrar_evolucao(historico)
    
    # ------------------------------------------------------------------
    # PASSO 6: AVALIAÇÃO DEPOIS DO FINE-TUNING
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 6: AVALIAÇÃO DEPOIS DO FINE-TUNING")
    print("─" * 70)
    
    # Matriz de similaridade DEPOIS
    mostrar_matriz_similaridade(
        model, tokenizer, device, queries_viz, docs_viz,
        "Matriz de similaridade DEPOIS do fine-tuning:"
    )
    
    # Recall@5 depois
    recall_depois = avaliar_recall(model, tokenizer, device, DADOS_VALIDACAO,
                                   todos_docs, top_k=5)
    
    print(f"\n   📊 COMPARAÇÃO DE RECALL@5:")
    print(f"   ├─ ANTES:  {recall_antes:.0%}"
          f" ({int(recall_antes * len(DADOS_VALIDACAO))}/{len(DADOS_VALIDACAO)})")
    print(f"   └─ DEPOIS: {recall_depois:.0%}"
          f" ({int(recall_depois * len(DADOS_VALIDACAO))}/{len(DADOS_VALIDACAO)})")
    
    # ------------------------------------------------------------------
    # PASSO 7: COMPARAÇÃO DE RANKINGS
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 7: COMPARAÇÃO DE RANKINGS (Antes vs Depois)")
    print("─" * 70)
    
    print(f"\n   Query: \"{query_demo}\"")
    
    print(f"\n   🔴 ANTES do fine-tuning:")
    print(f"   {'─'*60}")
    ranking_antes = computar_similaridades(model_antes, tokenizer, device, query_demo, docs_demo)
    for i, r in enumerate(ranking_antes, 1):
        print(f"   {i}. [{r['score']:.4f}] {r['doc'][:55]}")
    
    print(f"\n   🟢 DEPOIS do fine-tuning:")
    print(f"   {'─'*60}")
    ranking_depois = computar_similaridades(model, tokenizer, device, query_demo, docs_demo)
    for i, r in enumerate(ranking_depois, 1):
        print(f"   {i}. [{r['score']:.4f}] {r['doc'][:55]}")
    
    # Mais uma query para ver generalização
    query_demo2 = "trabalhador acidentado na empresa"
    print(f"\n   Query (generalização): \"{query_demo2}\"")
    
    print(f"\n   🔴 ANTES:")
    print(f"   {'─'*60}")
    for i, r in enumerate(computar_similaridades(
            model_antes, tokenizer, device, query_demo2, docs_demo), 1):
        print(f"   {i}. [{r['score']:.4f}] {r['doc'][:55]}")
    
    print(f"\n   🟢 DEPOIS:")
    print(f"   {'─'*60}")
    for i, r in enumerate(computar_similaridades(
            model, tokenizer, device, query_demo2, docs_demo), 1):
        print(f"   {i}. [{r['score']:.4f}] {r['doc'][:55]}")
    
    # ------------------------------------------------------------------
    # RESUMO FINAL
    # ------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("RESUMO: FINE-TUNING DE BI-ENCODER vs CROSS-ENCODER")
    print("=" * 70)
    print("""
   BI-ENCODER (este script):
   ┌──────────────────────────────────────────────────────────────┐
   │ Dados:     Pares (query, doc_positivo)                      │
   │ Loss:      MNRL (Multiple Negatives Ranking Loss)           │
   │ Arquit.:   BERT → mean pooling → L2 norm → cosine          │
   │ Treino:    Maximiza cosine(q, d+), minimiza cosine(q, d-)   │
   │ Saída:     Vetores de 768 dims (pré-computáveis!)           │
   │ Uso:       Retrieval em grandes coleções (milhões docs)     │
   └──────────────────────────────────────────────────────────────┘

   CROSS-ENCODER (finetuneCrossEncoder.py):
   ┌──────────────────────────────────────────────────────────────┐
   │ Dados:     Pares (query, doc) com label 0/1                 │
   │ Loss:      BCEWithLogitsLoss                                │
   │ Arquit.:   BERT + Linear(768→1) → score único               │
   │ Treino:    Minimiza erro entre score e label                │
   │ Saída:     Score escalar (NÃO pré-computável)               │
   │ Uso:       Re-ranking de poucos candidatos (~100)           │
   └──────────────────────────────────────────────────────────────┘

   PIPELINE COMPLETO EM PRODUÇÃO:
   ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
   │  Bi-Encoder  │────►│ Top-100 docs │────►│  Cross-Encoder   │──► Top-10
   │  (fine-tuned)│     │  candidatos  │     │  (fine-tuned)    │   finais
   │  Retrieval   │     │              │     │  Re-ranking      │
   └──────────────┘     └──────────────┘     └──────────────────┘
""")
    
    print("🎓 EXERCÍCIOS SUGERIDOS:")
    print("  1. Aumente o batch_size e observe o efeito nos negativos do MNRL")
    print("  2. Adicione hard negatives (docs quasi-relevantes como negativos)")
    print("  3. Experimente [CLS] pooling ao invés de mean pooling")
    print("  4. Compare com o cross-encoder (finetuneCrossEncoder.py)")
    print("  5. Salve o modelo: model.bert.save_pretrained('meu_biencoder/')")
    print("  6. Indexe os embeddings no ElasticSearch (indexaBertimbauElastic.py)")
    print("  7. Implemente o pipeline completo: bi-encoder → cross-encoder")
    print()
    print("📚 REFERÊNCIAS:")
    print("  - Sentence-BERT (bi-encoder): https://arxiv.org/abs/1908.10084")
    print("  - MNRL / InfoNCE: https://arxiv.org/abs/2004.04906")
    print("  - Dense Passage Retrieval: https://arxiv.org/abs/2004.04906")
    print("  - BERTimbau: https://github.com/neuralmind-ai/portuguese-bert")
    print("  - Sentence-Transformers: https://www.sbert.net/")


if __name__ == "__main__":
    main()
