# 🤝 Guia de Contribuição

Obrigado pelo interesse em contribuir com este projeto educacional! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### 1. Reportar Erros

Se você encontrou um erro:
- **Verifique** se já não existe uma issue aberta sobre o problema
- **Abra uma issue** descrevendo:
  - O que você esperava que acontecesse
  - O que realmente aconteceu
  - Passos para reproduzir o erro
  - Versão do Python e sistema operacional

### 2. Sugerir Melhorias

Para sugestões de novas funcionalidades ou melhorias:
- **Abra uma issue** com a tag `enhancement`
- **Descreva** claramente a melhoria proposta
- **Explique** por que seria útil do ponto de vista didático

### 3. Contribuir com Código

#### Passo a passo:

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/cursoRI.git
   cd cursoRI
   ```

3. **Crie uma branch** para sua contribuição:
   ```bash
   git checkout -b feature/minha-contribuicao
   ```

4. **Faça suas alterações** seguindo as diretrizes abaixo

5. **Teste** suas alterações:
   ```bash
   python seu_arquivo.py
   ```

6. **Commit** suas mudanças:
   ```bash
   git add .
   git commit -m "Descrição clara do que foi feito"
   ```

7. **Push** para seu fork:
   ```bash
   git push origin feature/minha-contribuicao
   ```

8. **Abra um Pull Request** no repositório original

## Diretrizes de Código

### Princípios Gerais

- ✅ **Clareza didática** acima de otimização
- ✅ **Comentários explicativos** em português
- ✅ **Exemplos simples** e fáceis de entender
- ✅ **Código executável** sem dependências complexas

### Estilo de Código Python

```python
# Use nomes descritivos
def calcula_precisao(relevantes_recuperados, total_recuperados):
    """
    Calcula a precisão de um sistema de recuperação.
    
    Args:
        relevantes_recuperados: Número de docs relevantes recuperados
        total_recuperados: Total de documentos recuperados
        
    Returns:
        float: Precisão (entre 0 e 1)
    """
    if total_recuperados == 0:
        return 0.0
    return relevantes_recuperados / total_recuperados
```

### Documentação

- **Docstrings** em todas as funções principais
- **Comentários** explicando a lógica complexa
- **README.md** atualizado quando adicionar novos módulos
- **Exemplos de uso** quando aplicável

### Testes

Para projetos didáticos, testes formais não são obrigatórios, mas:
- ✅ Verifique que o código executa sem erros
- ✅ Teste com diferentes inputs
- ✅ Valide os resultados manualmente

## Tipos de Contribuição Bem-Vindas

### 📊 Novas Métricas

Exemplos: MRR (Mean Reciprocal Rank), Precision@K, Recall@K, F1-Score

**Requisitos:**
- Implementação clara e comentada
- Exemplo de cálculo manual
- Documentação explicando quando usar
- Arquivo de exemplo com dados

### 🔤 Novas Técnicas de Vetorização

Exemplos: TF-IDF, FastText, Sentence-BERT, GPT embeddings

**Requisitos:**
- Código executável independente
- Comparação com técnicas existentes
- Requisitos de sistema documentados
- Tempo de execução estimado

### 📚 Melhorias na Documentação

- Correções de typos
- Exemplos adicionais
- Traduções (se aplicável)
- Diagramas explicativos

### 🐛 Correções de Bugs

Sempre bem-vindas! Inclua:
- Descrição do bug
- O que foi corrigido
- Como testar a correção

## Estrutura para Novos Módulos

Ao adicionar um novo módulo, siga esta estrutura:

```
novo_modulo/
├── README.md              # Documentação completa
├── RESUMO.md              # Resumo de 1 página (opcional)
├── exemplo_calculo_manual.py   # Exemplo passo a passo
├── calcula_[metrica].py   # Implementação principal
└── sampleFiles/           # Arquivos de exemplo (se necessário)
    └── exemplo.json
```

## Código de Conduta

- 🤝 Seja respeitoso e construtivo
- 💡 Foco no aprendizado
- 🌍 Ambiente inclusivo para todos os níveis
- 📖 Educação em primeiro lugar

## Dúvidas?

- Abra uma **issue** com a tag `question`
- Ou entre em contato diretamente

---

**Lembre-se:** Este é um projeto educacional. O objetivo é facilitar o aprendizado, não criar o código mais otimizado possível.

Obrigado por contribuir! 🎓
