#!/bin/bash

# Script para inicializar o repositório Git do projeto cursoRI
# Autor: Gerado automaticamente
# Uso: ./init_repo.sh

set -e  # Sair se houver erro

echo "🚀 Inicializando repositório Git para cursoRI..."
echo ""

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado. Por favor, instale o Git primeiro:"
    echo "   macOS: brew install git"
    echo "   Ubuntu/Debian: sudo apt-get install git"
    exit 1
fi

# Verificar se já existe um repositório Git
if [ -d ".git" ]; then
    echo "⚠️  Repositório Git já existe neste diretório."
    read -p "Deseja continuar mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
else
    # Inicializar o repositório
    echo "📁 Inicializando repositório Git..."
    git init
    echo "✅ Repositório inicializado"
fi

# Adicionar todos os arquivos
echo ""
echo "📝 Adicionando arquivos ao repositório..."
git add .

# Criar o primeiro commit
echo ""
echo "💾 Criando commit inicial..."
git commit -m "Initial commit: Projeto de exemplos didáticos de Recuperação de Informação

- Métricas: NDCG e MAP
- Vetorização: Word2Vec e BERTimbau
- Documentação completa
- Exemplos comentados"

echo "✅ Commit criado"

# Renomear para main
echo ""
echo "🔄 Renomeando branch para 'main'..."
git branch -M main
echo "✅ Branch renomeada"

echo ""
echo "✨ Repositório local configurado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Crie um repositório público no GitHub:"
echo "      https://github.com/new"
echo ""
echo "   2. Configure o remote (substitua SEU-USUARIO):"
echo "      git remote add origin https://github.com/SEU-USUARIO/cursoRI.git"
echo ""
echo "   3. Faça o push inicial:"
echo "      git push -u origin main"
echo ""
echo "   4. IMPORTANTE: Edite o arquivo LICENSE e substitua '[Seu Nome]' pelo seu nome real"
echo ""
echo "📖 Veja SETUP_GIT.md para mais detalhes"
echo ""
