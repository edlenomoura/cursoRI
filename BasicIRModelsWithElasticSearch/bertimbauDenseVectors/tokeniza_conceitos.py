#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TOKENIZAÇÃO DE CONCEITOS COM BERTIMBAU
================================================================================

Este script:
1. Lê um arquivo txt com campos separados por '|'
2. Isola o segundo campo (conceitos)
3. Tokeniza cada conceito usando o BERTimbau
4. Gera um arquivo JSON com o texto original e os tokens

================================================================================
"""

import json
import warnings
from transformers import AutoTokenizer

# Suprimir warnings
warnings.filterwarnings("ignore", message=".*resume_download.*", category=FutureWarning)

# Configuração
BERTIMBAU_MODEL = "neuralmind/bert-base-portuguese-cased"
ARQUIVO_ENTRADA = "conceitos.txt"
ARQUIVO_SAIDA = "conceitos_tokenizados.json"


def carregar_tokenizer():
    """Carrega o tokenizer do BERTimbau"""
    print(f"\n📥 Carregando tokenizer do BERTimbau...")
    print(f"   Modelo: {BERTIMBAU_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BERTIMBAU_MODEL)
    print(f"   ✓ Tokenizer carregado")
    return tokenizer


def ler_conceitos(caminho_arquivo):
    """
    Lê o arquivo txt e extrai o segundo campo (após o separador '|').
    
    Args:
        caminho_arquivo: Caminho do arquivo de entrada
        
    Returns:
        list: Lista de strings com os conceitos (segundo campo)
    """
    conceitos = []
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        for num_linha, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha:
                continue  # Pula linhas vazias
            
            campos = linha.split('|')
            
            if len(campos) >= 2:
                conceito = campos[1].strip()
                if conceito:
                    conceitos.append(conceito)
            else:
                print(f"   ⚠ Linha {num_linha} sem separador '|': {linha[:50]}...")
    
    print(f"\n✓ Arquivo lido: {len(conceitos)} conceitos extraídos")
    return conceitos


def tokenizar_conceitos(conceitos, tokenizer):
    """
    Tokeniza cada conceito usando o BERTimbau.
    
    Args:
        conceitos: Lista de strings com os conceitos
        tokenizer: Tokenizer do BERTimbau
        
    Returns:
        list: Lista de dicts com 'original' e 'tokenizado'
    """
    resultados = []
    
    for conceito in conceitos:
        # tokenize() retorna a lista de tokens (subwords)
        tokens = tokenizer.tokenize(conceito)
        
        resultados.append({
            "original": conceito,
            "tokenizado": tokens
        })
    
    return resultados


def salvar_json(resultados, caminho_saida):
    """Salva os resultados em um arquivo JSON"""
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Arquivo salvo: {caminho_saida}")
    print(f"  Total de conceitos: {len(resultados)}")


def main():
    print("=" * 70)
    print("TOKENIZAÇÃO DE CONCEITOS COM BERTIMBAU")
    print("=" * 70)
    
    try:
        # 1. Carregar tokenizer
        tokenizer = carregar_tokenizer()
        
        # 2. Ler conceitos do arquivo
        conceitos = ler_conceitos(ARQUIVO_ENTRADA)
        
        if not conceitos:
            print("\n❌ Nenhum conceito encontrado no arquivo.")
            return
        
        # 3. Tokenizar
        print(f"\n🔤 Tokenizando conceitos...")
        resultados = tokenizar_conceitos(conceitos, tokenizer)
        
        # 4. Salvar JSON
        salvar_json(resultados, ARQUIVO_SAIDA)
        
        # 5. Mostrar alguns exemplos
        print(f"\n📋 Exemplos (primeiros 5):")
        print("-" * 50)
        for item in resultados[:5]:
            print(f"  Original:   \"{item['original']}\"")
            print(f"  Tokenizado: {item['tokenizado']}")
            print()
        
        print("=" * 70)
        print("✓ PROCESSO CONCLUÍDO!")
        print("=" * 70)
        
    except FileNotFoundError:
        print(f"\n❌ Arquivo '{ARQUIVO_ENTRADA}' não encontrado!")
        print(f"   Certifique-se de que o arquivo está no diretório atual.")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()