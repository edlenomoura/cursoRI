# 🚀 Guia de Setup do Repositório Git

Este guia mostra como transformar este projeto local em um repositório Git público no GitHub.

## Pré-requisitos

- Git instalado ([Download](https://git-scm.com/downloads))
- Conta no GitHub ([Criar conta](https://github.com/join))

## Passo a Passo

### 1. Inicializar o Repositório Local

No diretório do projeto (`cursoRI/`), execute:

```bash
# Inicializar o repositório Git
git init

# Adicionar todos os arquivos
git add .

# Criar o primeiro commit
git commit -m "Initial commit: Projeto de exemplos didáticos de Recuperação de Informação"
```

### 2. Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name:** `cursoRI` (ou outro nome de sua preferência)
   - **Description:** "Exemplos didáticos para ensino de Recuperação de Informação"
   - **Visibility:** Selecione **Public**
   - ⚠️ **NÃO** marque "Initialize this repository with a README"
5. Clique em **"Create repository"**

### 3. Conectar o Repositório Local ao GitHub

Após criar o repositório, o GitHub mostrará instruções. Use:

```bash
# Adicionar o remote (substitua SEU-USUARIO pelo seu nome de usuário do GitHub)
git remote add origin https://github.com/SEU-USUARIO/cursoRI.git

# Renomear a branch principal para 'main' (padrão do GitHub)
git branch -M main

# Fazer o primeiro push
git push -u origin main
```

### 4. Verificar

Acesse `https://github.com/SEU-USUARIO/cursoRI` e verifique se todos os arquivos foram enviados corretamente.

## Comandos Git Úteis para o Futuro

### Fazer alterações

```bash
# Ver arquivos modificados
git status

# Adicionar arquivos específicos
git add arquivo1.py arquivo2.py

# Ou adicionar todos os arquivos modificados
git add .

# Criar commit com mensagem descritiva
git commit -m "Adiciona nova métrica MRR"

# Enviar para o GitHub
git push
```

### Criar nova funcionalidade

```bash
# Criar e mudar para nova branch
git checkout -b feature/nova-metrica

# ... fazer modificações ...

# Commit das mudanças
git add .
git commit -m "Implementa métrica MRR"

# Enviar branch para GitHub
git push -u origin feature/nova-metrica

# No GitHub, abra um Pull Request
```

### Atualizar do GitHub

```bash
# Baixar mudanças do GitHub
git pull
```

## Estrutura do .gitignore

O arquivo `.gitignore` já está configurado para ignorar:
- ✅ Ambientes virtuais (`venv/`, `venv_word2vec/`)
- ✅ Arquivos Python compilados (`__pycache__/`, `*.pyc`)
- ✅ Modelos treinados grandes (`*.bin`, `*.model`)
- ✅ Arquivos de IDEs (`.vscode/`, `.idea/`)
- ✅ Arquivos do sistema (`.DS_Store`)

## Configurações Recomendadas

### Configurar nome e email (primeira vez)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"
```

### Adicionar descrição do repositório

No GitHub, edite a descrição e adicione topics relevantes:
- `information-retrieval`
- `machine-learning`
- `nlp`
- `educational`
- `python`
- `portuguese`

### Adicionar badges ao README

As badges já estão incluídas no README.md:
- Badge Python 3.8+
- Badge de Licença MIT

## Próximos Passos

Após o repositório estar público:

1. ✅ Configure o GitHub Pages (se quiser site estático)
2. ✅ Adicione colaboradores (Settings → Collaborators)
3. ✅ Configure GitHub Actions para CI/CD (opcional)
4. ✅ Adicione issues ou projetos para rastrear melhorias

## Atualizar a Licença

**IMPORTANTE:** Edite o arquivo `LICENSE` e substitua `[Seu Nome]` pelo seu nome real:

```bash
# Edite manualmente ou use:
sed -i '' 's/\[Seu Nome\]/Seu Nome Real/g' LICENSE
git add LICENSE
git commit -m "Atualiza informações de licença"
git push
```

## Dúvidas?

- Documentação oficial do Git: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com
- GitHub Help: https://help.github.com

---

**Dica:** Faça commits pequenos e frequentes com mensagens descritivas. Isso facilita o rastreamento de mudanças e colaboração!
