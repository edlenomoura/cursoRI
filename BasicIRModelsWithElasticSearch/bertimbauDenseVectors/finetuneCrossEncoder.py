#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
FINE-TUNING DE CROSS-ENCODER COM BERTIMBAU
================================================================================

Este script demonstra como fazer fine-tuning do BERTimbau no modo cross-encoder
para a tarefa de re-ranking de busca jurídica.

================================================================================
O QUE É FINE-TUNING?
================================================================================

BERT pré-treinado:
- Aprendeu a "entender" português a partir de bilhões de palavras
- Sabe representar textos, mas NÃO sabe julgar relevância de busca
- É como um estudante que leu muitos livros, mas nunca fez uma prova

Fine-tuning:
- Adapta o modelo pré-treinado para uma TAREFA ESPECÍFICA
- Usamos exemplos rotulados: pares (query, documento) com labels de relevância
- É como treinar o estudante com exercícios específicos de uma matéria

ANTES do fine-tuning:
   [CLS] consulta [SEP] documento [SEP] ──► BERT ──► score ALEATÓRIO
                                                       (camada linear não treinada)

DEPOIS do fine-tuning:
   [CLS] consulta [SEP] documento [SEP] ──► BERT ──► score CALIBRADO
                                                       (modelo aprendeu o que é relevante)

================================================================================
ETAPAS DO FINE-TUNING
================================================================================

1. DADOS DE TREINAMENTO:
   - Pares (query, documento) com label de relevância
   - Label = 1.0 → documento relevante para a query
   - Label = 0.0 → documento NÃO relevante para a query
   - (Também pode ser gradual: 0.0, 0.5, 1.0)

2. ARQUITETURA:
   ┌─────────────────────────────────────┐
   │  Camada Linear (768 → 1)           │  ← Treinável (inicializada aleatória)
   ├─────────────────────────────────────┤
   │  BERT (12 camadas Transformer)      │  ← Treinável (pesos pré-treinados)
   ├─────────────────────────────────────┤
   │  [CLS] query [SEP] documento [SEP]  │  ← Entrada
   └─────────────────────────────────────┘

3. LOSS FUNCTION:
   - BCEWithLogitsLoss (Binary Cross-Entropy com logits)
   - Compara o score predito com o label real
   - Ajusta pesos para minimizar o erro

4. OTIMIZADOR:
   - AdamW com learning rate BAIXO (2e-5)
   - LR baixo porque NÃO queremos destruir o conhecimento pré-treinado
   - Apenas ajustar levemente os pesos para a nova tarefa

================================================================================
NESTE SCRIPT — EXEMPLO DIDÁTICO
================================================================================

Usamos um dataset PEQUENO e sintético de exemplos jurídicos para:
- Demonstrar todo o pipeline de fine-tuning
- Mostrar como os scores mudam antes/depois do treinamento
- Ilustrar overfitting (com poucos dados, o modelo decora)

Em produção, usaríamos:
- Milhares/milhões de pares rotulados
- Datasets como MS MARCO, TREC, ou dados próprios
- Validação cruzada, early stopping, etc.

================================================================================
"""

import time
import warnings
import copy
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, BertForSequenceClassification, AdamW
from typing import List, Tuple, Dict

warnings.filterwarnings("ignore", message=".*resume_download.*", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*AdamW.*", category=FutureWarning)

BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"


# ============================================================================
# PASSO 1: DADOS DE TREINAMENTO
# ============================================================================
#
# Em um cenário real, teríamos milhares de exemplos vindos de:
#   - Anotadores humanos (juízes, advogados)
#   - Logs de cliques de busca (query → doc clicado = relevante)
#   - Datasets públicos (MS MARCO, etc.)
#
# Para fins DIDÁTICOS, criamos um dataset pequeno e controlado.
# Cada exemplo tem:
#   - query: consulta do usuário
#   - documento: texto do documento candidato
#   - label: 1.0 (relevante) ou 0.0 (não relevante)
#
# ============================================================================

DADOS_TREINAMENTO = [
    # ── QUERY 1: "dano moral" ──
    # Positivos (relevantes)
    {"query": "dano moral",
     "documento": "dano moral por ofensa à honra e dignidade da pessoa",
     "label": 1.0},
    {"query": "dano moral",
     "documento": "danos morais por inscrição indevida em cadastro de inadimplentes",
     "label": 1.0},
    {"query": "dano moral",
     "documento": "indenização por abalo moral decorrente de falha na prestação de serviço",
     "label": 1.0},
    # Negativos (não relevantes)
    {"query": "dano moral",
     "documento": "contrato de compra e venda de imóvel residencial urbano",
     "label": 0.0},
    {"query": "dano moral",
     "documento": "execução fiscal de dívida tributária municipal",
     "label": 0.0},
    {"query": "dano moral",
     "documento": "habeas corpus contra prisão preventiva ilegal",
     "label": 0.0},

    # ── QUERY 2: "acidente de trabalho" ──
    # Positivos
    {"query": "acidente de trabalho",
     "documento": "responsabilidade civil do empregador por acidente de trabalho",
     "label": 1.0},
    {"query": "acidente de trabalho",
     "documento": "indenização por doença ocupacional equiparada a acidente laboral",
     "label": 1.0},
    {"query": "acidente de trabalho",
     "documento": "estabilidade provisória do empregado acidentado no serviço",
     "label": 1.0},
    # Negativos
    {"query": "acidente de trabalho",
     "documento": "guarda compartilhada dos filhos após divórcio",
     "label": 0.0},
    {"query": "acidente de trabalho",
     "documento": "pensão alimentícia para filho menor de idade",
     "label": 0.0},
    {"query": "acidente de trabalho",
     "documento": "usucapião extraordinária de bem imóvel rural",
     "label": 0.0},

    # ── QUERY 3: "pensão alimentícia" ──
    # Positivos
    {"query": "pensão alimentícia",
     "documento": "pensão alimentícia para filho menor de idade",
     "label": 1.0},
    {"query": "pensão alimentícia",
     "documento": "revisão de alimentos fixados em sentença judicial",
     "label": 1.0},
    {"query": "pensão alimentícia",
     "documento": "execução de prestação alimentar por inadimplemento do devedor",
     "label": 1.0},
    # Negativos
    {"query": "pensão alimentícia",
     "documento": "mandado de segurança contra ato de autoridade pública",
     "label": 0.0},
    {"query": "pensão alimentícia",
     "documento": "penhora de bens do devedor para garantia da execução",
     "label": 0.0},
    {"query": "pensão alimentícia",
     "documento": "embargos de declaração por omissão na sentença",
     "label": 0.0},

    # ── QUERY 4: "contrato bancário" ──
    # Positivos
    {"query": "contrato bancário",
     "documento": "revisão de contrato bancário com juros abusivos",
     "label": 1.0},
    {"query": "contrato bancário",
     "documento": "nulidade de cláusulas abusivas em contrato de empréstimo consignado",
     "label": 1.0},
    # Negativos
    {"query": "contrato bancário",
     "documento": "aposentadoria por invalidez junto ao INSS",
     "label": 0.0},
    {"query": "contrato bancário",
     "documento": "ação de despejo por falta de pagamento de aluguel",
     "label": 0.0},

    # ── QUERY 5: "prisão ilegal" ──
    # Positivos
    {"query": "prisão ilegal",
     "documento": "habeas corpus contra prisão preventiva ilegal",
     "label": 1.0},
    {"query": "prisão ilegal",
     "documento": "relaxamento de prisão em flagrante por vício formal",
     "label": 1.0},
    # Negativos
    {"query": "prisão ilegal",
     "documento": "rescisão indireta do contrato de trabalho por justa causa do empregador",
     "label": 0.0},
    {"query": "prisão ilegal",
     "documento": "tutela antecipada de urgência em ação de saúde",
     "label": 0.0},
]

# Dados de VALIDAÇÃO (separados — o modelo NUNCA vê durante o treino)
DADOS_VALIDACAO = [
    {"query": "dano moral",
     "documento": "reparação por dano extrapatrimonial em relação de consumo",
     "label": 1.0},
    {"query": "dano moral",
     "documento": "recurso de apelação contra sentença de primeiro grau",
     "label": 0.0},
    {"query": "acidente de trabalho",
     "documento": "nexo causal entre atividade laboral e lesão corporal do trabalhador",
     "label": 1.0},
    {"query": "acidente de trabalho",
     "documento": "contrato de compra e venda de imóvel residencial urbano",
     "label": 0.0},
    {"query": "pensão alimentícia",
     "documento": "obrigação de prestar alimentos ao filho até a maioridade civil",
     "label": 1.0},
    {"query": "pensão alimentícia",
     "documento": "impugnação ao cumprimento de sentença por excesso de execução",
     "label": 0.0},
]

# Dados de TESTE (para avaliar antes e depois do fine-tuning)
# Pares com relevância variada — usamos para ver se o modelo aprendeu
DADOS_TESTE = [
    # Deve ser relevante
    {"query": "dano moral",
     "documento": "compensação por sofrimento psíquico causado por conduta ilícita",
     "label": 1.0},
    {"query": "acidente de trabalho",
     "documento": "empregado sofreu lesão durante jornada de trabalho na empresa",
     "label": 1.0},
    {"query": "pensão alimentícia",
     "documento": "pai obrigado a pagar pensão mensal para sustento dos filhos",
     "label": 1.0},
    # Não deve ser relevante
    {"query": "dano moral",
     "documento": "partilha de bens do casal em processo de inventário",
     "label": 0.0},
    {"query": "acidente de trabalho",
     "documento": "ação de cobrança de honorários advocatícios extrajudiciais",
     "label": 0.0},
    {"query": "pensão alimentícia",
     "documento": "busca e apreensão de veículo alienado fiduciariamente",
     "label": 0.0},
]


# ============================================================================
# PASSO 2: DATASET E DATALOADER (PyTorch)
# ============================================================================

class DatasetCrossEncoder(Dataset):
    """
    Dataset PyTorch para fine-tuning do cross-encoder.
    
    PAPEL DO DATASET:
    - Armazena os pares (query, documento, label)
    - Tokeniza cada par usando o formato de entrada do BERT:
      [CLS] query [SEP] documento [SEP]
    - Retorna tensores prontos para o modelo
    
    PAPEL DO DATALOADER (usado depois):
    - Agrupa exemplos em BATCHES (lotes)
    - Embaralha os dados a cada época
    - Permite processamento em paralelo
    """
    
    def __init__(self, dados: List[Dict], tokenizer, max_length=128):
        """
        Args:
            dados: Lista de dicts com 'query', 'documento', 'label'
            tokenizer: Tokenizer do BERTimbau
            max_length: Tamanho máximo da sequência tokenizada
                        (128 é suficiente para textos curtos como os nossos)
        """
        self.dados = dados
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.dados)
    
    def __getitem__(self, idx):
        """
        Retorna um exemplo tokenizado.
        
        O tokenizer recebe (query, documento) como par de sentenças e gera:
        
        input_ids:      [CLS] tok1 tok2 [SEP] tok3 tok4 tok5 [SEP] [PAD] [PAD]
        attention_mask:    1    1    1     1     1    1    1     1     0     0
        token_type_ids:    0    0    0     0     1    1    1     1     0     0
                          |__ query __|         |___ documento ___|
        
        - input_ids: IDs dos tokens no vocabulário do BERT
        - attention_mask: 1 = token real, 0 = padding (ignorar)
        - token_type_ids: 0 = tokens da query, 1 = tokens do documento
        """
        exemplo = self.dados[idx]
        
        # Tokeniza como PAR de sentenças
        encoded = self.tokenizer(
            exemplo["query"],           # Sentença A (query)
            exemplo["documento"],       # Sentença B (documento)
            truncation=True,
            max_length=self.max_length,
            padding="max_length",       # Pad até max_length
            return_tensors="pt"
        )
        
        # Remove dimensão de batch (tokenizer retorna [1, seq_len])
        item = {k: v.squeeze(0) for k, v in encoded.items()}
        
        # Label de relevância
        item["labels"] = torch.tensor(exemplo["label"], dtype=torch.float)
        
        return item


# ============================================================================
# PASSO 3: FUNÇÕES DE TREINAMENTO
# ============================================================================

def treinar_uma_epoca(model, dataloader, optimizer, loss_fn, device, epoca_num):
    """
    Treina o modelo por UMA ÉPOCA (uma passada completa pelos dados).
    
    UMA ÉPOCA DE TREINAMENTO:
    
    Para cada batch de exemplos:
    ┌──────────────────────────────────────────────────────────────────┐
    │ 1. FORWARD PASS                                                  │
    │    Entrada → BERT → score_predito                                │
    │                                                                  │
    │ 2. CÁLCULO DA LOSS                                               │
    │    loss = BCEWithLogitsLoss(score_predito, label_real)           │
    │    "Quão errado o modelo está?"                                  │
    │                                                                  │
    │ 3. BACKWARD PASS (Backpropagation)                               │
    │    Calcula gradientes: ∂loss/∂peso para CADA peso do modelo     │
    │    "Quanto cada peso contribuiu para o erro?"                    │
    │                                                                  │
    │ 4. ATUALIZAÇÃO DOS PESOS (Optimizer Step)                        │
    │    peso_novo = peso_antigo - lr × gradiente                      │
    │    "Ajusta pesos na direção que reduz o erro"                    │
    └──────────────────────────────────────────────────────────────────┘
    
    Args:
        model: BertForSequenceClassification
        dataloader: DataLoader com os dados de treinamento
        optimizer: AdamW
        loss_fn: BCEWithLogitsLoss
        device: 'cuda' ou 'cpu'
        epoca_num: Número da época (para exibição)
        
    Returns:
        float: Loss média da época
    """
    model.train()  # Modo treino (ativa dropout, batch norm)
    loss_total = 0.0
    n_batches = 0
    
    for batch in dataloader:
        # Move dados para GPU/CPU
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        token_type_ids = batch["token_type_ids"].to(device)
        labels = batch["labels"].to(device)
        
        # ── FORWARD PASS ──
        # O modelo recebe os tokens e produz logits (scores não-normalizados)
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        logits = outputs.logits.squeeze(-1)  # Shape: [batch_size]
        
        # ── CÁLCULO DA LOSS ──
        # BCEWithLogitsLoss = Sigmoid + Binary Cross Entropy
        # Compara score predito com label real (0.0 ou 1.0)
        loss = loss_fn(logits, labels)
        
        # ── BACKWARD PASS ──
        # Calcula gradientes via backpropagation
        optimizer.zero_grad()  # Zera gradientes anteriores
        loss.backward()        # Calcula novos gradientes
        
        # Gradient clipping: evita "explosão de gradientes"
        # (limita magnitude dos gradientes para estabilidade)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        # ── ATUALIZAÇÃO DOS PESOS ──
        optimizer.step()       # Aplica gradientes aos pesos
        
        loss_total += loss.item()
        n_batches += 1
    
    loss_media = loss_total / n_batches
    return loss_media


def avaliar(model, dataloader, loss_fn, device):
    """
    Avalia o modelo nos dados de validação (SEM TREINAR).
    
    Diferenças em relação ao treinamento:
    - model.eval(): desativa dropout e batch norm
    - torch.no_grad(): não calcula gradientes (mais rápido, menos memória)
    - NÃO faz optimizer.step() (não atualiza pesos)
    
    Returns:
        tuple: (loss_média, acurácia, lista_de_predições)
    """
    model.eval()  # Modo avaliação
    loss_total = 0.0
    n_batches = 0
    acertos = 0
    total = 0
    predicoes = []
    
    with torch.no_grad():  # Desativa cálculo de gradientes
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids
            )
            logits = outputs.logits.squeeze(-1)
            
            loss = loss_fn(logits, labels)
            loss_total += loss.item()
            n_batches += 1
            
            # Converte logits → probabilidade com sigmoid
            probs = torch.sigmoid(logits)
            
            # Predição: prob > 0.5 → relevante (1), senão → não relevante (0)
            preds = (probs > 0.5).float()
            acertos += (preds == labels).sum().item()
            total += labels.size(0)
            
            # Salva predições para análise
            for i in range(labels.size(0)):
                predicoes.append({
                    "label_real": labels[i].item(),
                    "score": logits[i].item(),
                    "prob": probs[i].item(),
                    "pred": preds[i].item()
                })
    
    loss_media = loss_total / max(n_batches, 1)
    acuracia = acertos / max(total, 1)
    
    return loss_media, acuracia, predicoes


# ============================================================================
# PASSO 4: FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def mostrar_scores_teste(model, tokenizer, device, dados, titulo):
    """
    Mostra os scores do modelo para os dados de teste.
    Útil para comparar ANTES vs DEPOIS do fine-tuning.
    """
    model.eval()
    print(f"\n   {titulo}")
    print(f"   {'─'*65}")
    
    with torch.no_grad():
        for exemplo in dados:
            encoded = tokenizer(
                exemplo["query"],
                exemplo["documento"],
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            encoded = {k: v.to(device) for k, v in encoded.items()}
            
            logit = model(**encoded).logits[0][0].item()
            prob = torch.sigmoid(torch.tensor(logit)).item()
            
            label = "✓ REL" if exemplo["label"] == 1.0 else "✗ NÃO"
            pred_ok = "✓" if (prob > 0.5) == (exemplo["label"] == 1.0) else "✗"
            
            print(f"   {pred_ok} [{label}] Score:{logit:+7.3f} Prob:{prob:.3f}"
                  f"  Q:\"{exemplo['query'][:20]}\" → D:\"{exemplo['documento'][:45]}\"")


def mostrar_evolucao_treinamento(historico):
    """
    Mostra gráfico ASCII da evolução da loss durante o treinamento.
    
    A loss deve DIMINUIR ao longo das épocas (modelo está aprendendo).
    """
    print(f"\n   📉 EVOLUÇÃO DA LOSS (deve diminuir):")
    print(f"   {'─'*55}")
    
    max_loss = max(h["loss_treino"] for h in historico)
    largura_barra = 40
    
    for h in historico:
        # Barra proporcional à loss
        tamanho = int((h["loss_treino"] / max_loss) * largura_barra)
        barra = "█" * tamanho + "░" * (largura_barra - tamanho)
        
        print(f"   Época {h['epoca']:2d} │{barra}│ "
              f"Loss:{h['loss_treino']:.4f} "
              f"Val:{h['loss_val']:.4f} "
              f"Acc:{h['acc_val']:.0%}")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("  FINE-TUNING DE CROSS-ENCODER COM BERTIMBAU")
    print("=" * 70)
    print()
    print("Este script demonstra como adaptar (fine-tune) o BERTimbau")
    print("para funcionar como cross-encoder de relevância jurídica.")
    print()
    print("Pipeline:")
    print("  1. Preparar dados de treinamento (pares query-doc com labels)")
    print("  2. Carregar BERTimbau + camada de classificação")
    print("  3. Avaliar modelo ANTES do fine-tuning (baseline)")
    print("  4. Treinar por algumas épocas")
    print("  5. Avaliar modelo DEPOIS do fine-tuning")
    print("  6. Comparar scores antes vs depois")
    print()
    
    # ------------------------------------------------------------------
    # PASSO 1: PREPARAÇÃO
    # ------------------------------------------------------------------
    print("─" * 70)
    print("PASSO 1: PREPARAÇÃO DOS DADOS")
    print("─" * 70)
    
    print(f"\n   Dados de treinamento: {len(DADOS_TREINAMENTO)} exemplos")
    print(f"   Dados de validação:   {len(DADOS_VALIDACAO)} exemplos")
    print(f"   Dados de teste:       {len(DADOS_TESTE)} exemplos")
    
    # Contagem de positivos/negativos
    pos_treino = sum(1 for d in DADOS_TREINAMENTO if d["label"] == 1.0)
    neg_treino = sum(1 for d in DADOS_TREINAMENTO if d["label"] == 0.0)
    print(f"\n   Treinamento: {pos_treino} positivos + {neg_treino} negativos")
    
    print(f"\n   Exemplos dos dados:")
    print(f"   {'─'*60}")
    for i, d in enumerate(DADOS_TREINAMENTO[:4]):
        label_str = "RELEVANTE" if d["label"] == 1.0 else "NÃO RELEV"
        print(f"   [{label_str}] Q:\"{d['query']}\" → D:\"{d['documento'][:50]}\"")
    print(f"   ... ({len(DADOS_TREINAMENTO) - 4} mais)")
    
    # ------------------------------------------------------------------
    # PASSO 2: CARREGAR MODELO
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 2: CARREGANDO BERTIMBAU + CAMADA DE CLASSIFICAÇÃO")
    print("─" * 70)
    
    print("\n📥 Carregando tokenizer e modelo...")
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    
    # BertForSequenceClassification = BERT + Linear(768→1)
    model = BertForSequenceClassification.from_pretrained(
        BERTIMBAU_MODEL,
        num_labels=1  # 1 score de relevância (regressão/binário)
    )
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    print(f"   ✓ Modelo: {BERTIMBAU_MODEL}")
    print(f"   ✓ Device: {device}")
    print(f"   ✓ Arquitetura: BERT (768) + Linear(768→1)")
    
    # Conta parâmetros
    total_params = sum(p.numel() for p in model.parameters())
    treinaveis = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   ✓ Parâmetros totais:    {total_params:>12,}")
    print(f"   ✓ Parâmetros treináveis: {treinaveis:>12,}")
    print(f"\n   NOTA: A camada linear (768→1 = 769 parâmetros) é NOVA.")
    print(f"         Os pesos do BERT (109M+) são PRÉ-TREINADOS.")
    print(f"         No fine-tuning, TODOS os pesos são ajustados levemente.")
    
    # ------------------------------------------------------------------
    # PASSO 3: AVALIAR ANTES DO FINE-TUNING
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 3: SCORES ANTES DO FINE-TUNING (Baseline)")
    print("─" * 70)
    print()
    print("   O modelo ainda NÃO foi treinado para relevância.")
    print("   A camada linear tem pesos ALEATÓRIOS.")
    print("   Os scores NÃO devem fazer sentido (é o esperado).")
    
    # Salva cópia do modelo antes do fine-tuning para comparar depois
    model_antes = copy.deepcopy(model)
    model_antes.eval()
    
    mostrar_scores_teste(model, tokenizer, device, DADOS_TESTE,
                         "Scores ANTES do fine-tuning (camada linear aleatória):")
    
    # ------------------------------------------------------------------
    # PASSO 4: CRIAR DATASETS E DATALOADERS
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 4: CRIANDO DATASETS E DATALOADERS")
    print("─" * 70)
    
    # Datasets
    dataset_treino = DatasetCrossEncoder(DADOS_TREINAMENTO, tokenizer, max_length=128)
    dataset_val = DatasetCrossEncoder(DADOS_VALIDACAO, tokenizer, max_length=128)
    dataset_teste = DatasetCrossEncoder(DADOS_TESTE, tokenizer, max_length=128)
    
    # DataLoaders
    # batch_size=8: processa 8 pares de cada vez
    # shuffle=True: embaralha a cada época (evita padrões de ordem)
    BATCH_SIZE = 8
    
    loader_treino = DataLoader(dataset_treino, batch_size=BATCH_SIZE, shuffle=True)
    loader_val = DataLoader(dataset_val, batch_size=BATCH_SIZE, shuffle=False)
    loader_teste = DataLoader(dataset_teste, batch_size=BATCH_SIZE, shuffle=False)
    
    print(f"\n   ✓ Batch size: {BATCH_SIZE}")
    print(f"   ✓ Batches por época (treino): {len(loader_treino)}")
    print(f"   ✓ Max sequence length: 128 tokens")
    
    # Mostra um batch de exemplo
    batch_exemplo = next(iter(loader_treino))
    print(f"\n   Exemplo de um batch:")
    print(f"   ├─ input_ids shape:      {list(batch_exemplo['input_ids'].shape)}")
    print(f"   ├─ attention_mask shape:  {list(batch_exemplo['attention_mask'].shape)}")
    print(f"   ├─ token_type_ids shape:  {list(batch_exemplo['token_type_ids'].shape)}")
    print(f"   └─ labels shape:          {list(batch_exemplo['labels'].shape)}")
    print(f"      labels valores:        {batch_exemplo['labels'].tolist()}")
    
    # ------------------------------------------------------------------
    # PASSO 5: CONFIGURAR OTIMIZADOR E LOSS
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 5: CONFIGURANDO OTIMIZADOR E LOSS")
    print("─" * 70)
    
    # Learning rate BAIXO: não queremos destruir os pesos pré-treinados!
    # Típico para fine-tuning de BERT: 1e-5 a 5e-5
    LEARNING_RATE = 2e-5
    NUM_EPOCAS = 10  # Poucas épocas (dataset pequeno → overfitting rápido)
    
    # AdamW: Adam com Weight Decay (regularização)
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    
    # BCEWithLogitsLoss: ideal para classificação binária
    # Combina Sigmoid + Binary Cross Entropy em uma operação numericamente estável
    #
    # Fórmula: loss = -[y × log(σ(x)) + (1-y) × log(1 - σ(x))]
    # onde: y = label (0 ou 1), x = logit (score do modelo), σ = sigmoid
    loss_fn = nn.BCEWithLogitsLoss()
    
    print(f"\n   ✓ Otimizador:     AdamW")
    print(f"   ✓ Learning rate:  {LEARNING_RATE}")
    print(f"   ✓ Weight decay:   0.01")
    print(f"   ✓ Loss function:  BCEWithLogitsLoss")
    print(f"   ✓ Épocas:         {NUM_EPOCAS}")
    print(f"   ✓ Grad clipping:  max_norm=1.0")
    
    print(f"""
   POR QUE ESSES VALORES?

   Learning rate = 2e-5 (muito baixo!):
   ┌──────────────────────────────────┐
   │ LR muito alto (ex: 0.01):       │ → Destrói pesos pré-treinados
   │ LR muito baixo (ex: 1e-7):      │ → Não aprende nada
   │ LR ideal para BERT (~2e-5):     │ → Ajusta levemente os pesos ✓
   └──────────────────────────────────┘
   
   O BERT já sabe "entender" português. Só precisamos ajustar
   levemente para que ele aprenda a julgar relevância.
""")
    
    # ------------------------------------------------------------------
    # PASSO 6: TREINAMENTO
    # ------------------------------------------------------------------
    print("─" * 70)
    print("PASSO 6: TREINAMENTO (Fine-Tuning)")
    print("─" * 70)
    print()
    print("   Início do treinamento...")
    print(f"   {'─'*55}")
    
    historico = []
    
    for epoca in range(1, NUM_EPOCAS + 1):
        t0 = time.time()
        
        # Treina uma época
        loss_treino = treinar_uma_epoca(
            model, loader_treino, optimizer, loss_fn, device, epoca
        )
        
        # Avalia na validação
        loss_val, acc_val, _ = avaliar(model, loader_val, loss_fn, device)
        
        tempo = time.time() - t0
        
        historico.append({
            "epoca": epoca,
            "loss_treino": loss_treino,
            "loss_val": loss_val,
            "acc_val": acc_val,
            "tempo": tempo
        })
        
        print(f"   Época {epoca:2d}/{NUM_EPOCAS} │ "
              f"Loss treino: {loss_treino:.4f} │ "
              f"Loss val: {loss_val:.4f} │ "
              f"Acc val: {acc_val:.0%} │ "
              f"{tempo:.1f}s")
    
    # Mostra evolução
    mostrar_evolucao_treinamento(historico)
    
    # ------------------------------------------------------------------
    # PASSO 7: AVALIAR DEPOIS DO FINE-TUNING
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 7: SCORES DEPOIS DO FINE-TUNING")
    print("─" * 70)
    print()
    print("   Agora o modelo FOI treinado para julgar relevância.")
    print("   Os scores devem refletir melhor a relevância real.")
    
    mostrar_scores_teste(model_antes, tokenizer, device, DADOS_TESTE,
                         "🔴 ANTES do fine-tuning (baseline):")
    
    mostrar_scores_teste(model, tokenizer, device, DADOS_TESTE,
                         "🟢 DEPOIS do fine-tuning:")
    
    # Avaliação formal no teste
    loss_teste, acc_teste, preds_teste = avaliar(model, loader_teste, loss_fn, device)
    print(f"\n   📊 Métricas no conjunto de TESTE:")
    print(f"   ├─ Loss:      {loss_teste:.4f}")
    print(f"   └─ Acurácia:  {acc_teste:.0%} ({int(acc_teste * len(DADOS_TESTE))}/{len(DADOS_TESTE)} corretos)")
    
    # ------------------------------------------------------------------
    # PASSO 8: DEMONSTRAÇÃO DE USO PARA RE-RANKING
    # ------------------------------------------------------------------
    print(f"\n{'─'*70}")
    print("PASSO 8: USANDO O MODELO TREINADO PARA RE-RANKING")
    print("─" * 70)
    
    query_demo = "indenização por dano moral"
    candidatos = [
        "dano moral por ofensa à honra e dignidade da pessoa",
        "compensação por sofrimento psíquico causado por conduta ilícita",
        "responsabilidade civil do empregador por acidente de trabalho",
        "contrato de compra e venda de imóvel residencial urbano",
        "guarda compartilhada dos filhos após divórcio",
        "habeas corpus contra prisão preventiva ilegal",
    ]
    
    print(f"\n   Query: \"{query_demo}\"")
    print(f"   Candidatos para re-ranking: {len(candidatos)}")
    
    # Score com modelo ANTES
    print(f"\n   🔴 Ranking com modelo SEM fine-tuning:")
    print(f"   {'─'*60}")
    
    scores_antes = []
    model_antes.eval()
    with torch.no_grad():
        for doc in candidatos:
            enc = tokenizer(query_demo, doc, return_tensors="pt",
                          truncation=True, max_length=128, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            logit = model_antes(**enc).logits[0][0].item()
            prob = torch.sigmoid(torch.tensor(logit)).item()
            scores_antes.append({"doc": doc, "score": logit, "prob": prob})
    
    scores_antes.sort(key=lambda x: x["score"], reverse=True)
    for i, s in enumerate(scores_antes, 1):
        print(f"   {i}. [Score:{s['score']:+7.3f} Prob:{s['prob']:.3f}] {s['doc'][:55]}")
    
    # Score com modelo DEPOIS
    print(f"\n   🟢 Ranking com modelo COM fine-tuning:")
    print(f"   {'─'*60}")
    
    scores_depois = []
    model.eval()
    with torch.no_grad():
        for doc in candidatos:
            enc = tokenizer(query_demo, doc, return_tensors="pt",
                          truncation=True, max_length=128, padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            logit = model(**enc).logits[0][0].item()
            prob = torch.sigmoid(torch.tensor(logit)).item()
            scores_depois.append({"doc": doc, "score": logit, "prob": prob})
    
    scores_depois.sort(key=lambda x: x["score"], reverse=True)
    for i, s in enumerate(scores_depois, 1):
        print(f"   {i}. [Score:{s['score']:+7.3f} Prob:{s['prob']:.3f}] {s['doc'][:55]}")
    
    # ------------------------------------------------------------------
    # RESUMO FINAL
    # ------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("RESUMO: O QUE APRENDEMOS SOBRE FINE-TUNING DE CROSS-ENCODER")
    print("=" * 70)
    print("""
   1. DADOS: Precisamos de pares (query, documento) com labels de relevância
      - Mais dados = melhor generalização
      - Dados equilibrados (positivos ≈ negativos)

   2. MODELO: BertForSequenceClassification = BERT + Linear(768→1)
      - BERT: pesos pré-treinados (entende português)
      - Linear: pesos novos (aprende a julgar relevância)

   3. TREINAMENTO:
      - Learning rate BAIXO (2e-5): preserva conhecimento pré-treinado
      - BCEWithLogitsLoss: loss para classificação binária
      - Gradient clipping: estabilidade numérica
      - Poucas épocas: evita overfitting (especialmente com poucos dados)

   4. AVALIAÇÃO:
      - Sempre separar treino / validação / teste
      - Monitorar loss de validação (se subir → overfitting)
      - Acurácia, Precision, Recall, nDCG para ranking

   5. USO EM PRODUÇÃO:
      - Pipeline: BM25/Bi-Encoder (Retrieval) → Cross-Encoder (Re-Rank)
      - Salvar modelo treinado: model.save_pretrained("meu_modelo/")
      - Carregar depois: BertForSequenceClassification.from_pretrained("meu_modelo/")

   ⚠️  LIMITAÇÕES DESTE EXEMPLO:
      - Dataset MUITO pequeno (26 exemplos) → modelo memoriza, não generaliza
      - Em produção, use milhares/milhões de exemplos
      - Considere datasets como MS MARCO, TREC, ou dados do seu domínio
""")
    
    print("🎓 EXERCÍCIOS SUGERIDOS:")
    print("  1. Aumente o dataset e observe a melhora na generalização")
    print("  2. Experimente diferentes learning rates (1e-5, 3e-5, 5e-5)")
    print("  3. Adicione labels graduais (0.0, 0.5, 1.0) ao invés de binário")
    print("  4. Implemente early stopping (parar quando loss_val para de melhorar)")
    print("  5. Salve e recarregue o modelo treinado")
    print("  6. Integre com o crossEncoderBertimbau.py (pipeline completo)")
    print()
    print("📚 REFERÊNCIAS:")
    print("  - Fine-tuning BERT: https://arxiv.org/abs/1810.04805 (seção 4)")
    print("  - Cross-Encoder training: https://www.sbert.net/docs/cross_encoder/training_overview.html")
    print("  - MS MARCO dataset: https://microsoft.github.io/msmarco/")
    print("  - HuggingFace fine-tuning: https://huggingface.co/docs/transformers/training")


if __name__ == "__main__":
    main()
