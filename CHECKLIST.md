# ✅ Checklist para Publicação do Repositório

Use este checklist para verificar se tudo está pronto antes de tornar o repositório público.

## 📋 Antes de Publicar

### Arquivos Essenciais
- [x] `README.md` - README principal atualizado e completo
- [x] `LICENSE` - ⚠️ **EDITE e adicione seu nome no lugar de [Seu Nome]**
- [x] `.gitignore` - Configurado para ignorar arquivos desnecessários
- [x] `CONTRIBUTING.md` - Guia de contribuição
- [x] `requirements.txt` - Dependências do projeto

### Documentação
- [x] Cada subdiretório tem seu próprio README
- [x] Exemplos de código estão comentados
- [x] Instruções de instalação estão claras
- [ ] Links no README principal funcionam corretamente

### Conteúdo Sensível ⚠️
- [x] Nenhuma credencial ou senha
- [x] Nenhuma informação pessoal sensível
- [x] Nenhum token ou API key
- [x] Nenhuma referência a sistemas internos

### Código
- [ ] Todos os programas executam sem erro
- [ ] Dependências estão documentadas
- [ ] Exemplos foram testados
- [ ] Comentários estão em português

## 🚀 Passos para Publicar

### 1. Atualizar Informações Pessoais

**IMPORTANTE:** Edite o arquivo `LICENSE`:
```bash
# Substitua [Seu Nome] pelo seu nome real
nano LICENSE
# ou use seu editor preferido
```

### 2. Inicializar Git (Método Fácil)

Execute o script automatizado:
```bash
./init_repo.sh
```

**OU** faça manualmente (veja `SETUP_GIT.md` para instruções detalhadas):
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
```

### 3. Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - Nome: `cursoRI` (ou outro de sua escolha)
   - Descrição: "Exemplos didáticos para ensino de Recuperação de Informação"
   - Visibilidade: **Public** ✅
   - **NÃO** inicialize com README
3. Clique em "Create repository"

### 4. Conectar e Enviar

```bash
# Substitua SEU-USUARIO pelo seu username do GitHub
git remote add origin https://github.com/SEU-USUARIO/cursoRI.git
git push -u origin main
```

### 5. Configurar Repositório no GitHub

No GitHub, acesse Settings e configure:

**About (canto superior direito):**
- ✅ Adicione descrição
- ✅ Adicione website (se tiver)
- ✅ Adicione topics: `information-retrieval`, `machine-learning`, `nlp`, `educational`, `python`, `portuguese`

**Opções:**
- ✅ Issues habilitadas
- ✅ Wiki desabilitada (opcional)
- ✅ Discussions (opcional, mas recomendado para projeto educacional)

## 📊 Após a Publicação

### Verificação Final
- [ ] README é exibido corretamente na página principal
- [ ] Badges estão funcionando
- [ ] Links estão funcionando
- [ ] Estrutura de pastas está correta

### Divulgação (Opcional)
- [ ] Compartilhe com seus alunos
- [ ] Adicione link no material da disciplina
- [ ] Poste em redes acadêmicas (ResearchGate, Academia.edu)
- [ ] Considere postar no Reddit r/MachineLearning ou r/learnmachinelearning

### Manutenção
- [ ] Configure notificações de issues
- [ ] Responda issues e pull requests
- [ ] Mantenha documentação atualizada
- [ ] Adicione exemplos conforme surgem dúvidas dos alunos

## 🔄 Atualizações Futuras

Para adicionar novos conteúdos:

```bash
# Criar branch para nova funcionalidade
git checkout -b feature/nova-metrica

# Fazer modificações...

# Commit
git add .
git commit -m "Adiciona métrica MRR"

# Push
git push -u origin feature/nova-metrica

# No GitHub, crie um Pull Request
```

## 📚 Recursos Úteis

- [Guia Git](SETUP_GIT.md) - Instruções detalhadas de Git
- [Guia de Contribuição](CONTRIBUTING.md) - Como outros podem contribuir
- [GitHub Guides](https://guides.github.com) - Tutoriais oficiais
- [Markdown Guide](https://www.markdownguide.org) - Sintaxe Markdown

## ❓ Dúvidas Comuns

**P: O que fazer se esquecer de editar o LICENSE antes do primeiro commit?**
R: Não tem problema! Edite o arquivo, faça um novo commit e push:
```bash
nano LICENSE
git add LICENSE
git commit -m "Atualiza informações de licença"
git push
```

**P: Posso mudar o nome do repositório depois?**
R: Sim! No GitHub: Settings → Repository name → Rename

**P: E se eu quiser tornar privado mais tarde?**
R: Settings → Danger Zone → Change visibility → Make private

---

**Pronto para publicar?** Execute `./init_repo.sh` e siga as instruções! 🚀
