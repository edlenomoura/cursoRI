#!/bin/bash
################################################################################
# SCRIPT DE INICIALIZAÇÃO DO DOCKER E ELASTICSEARCH
################################################################################
#
# OBJETIVO:
# Este script automatiza o processo de inicialização do ElasticSearch usando
# Docker. Ele foi criado para fins didáticos e facilita o setup para alunos.
#
# O QUE ESTE SCRIPT FAZ:
# 1. Verifica se o Docker está rodando (inicia se necessário)
# 2. Verifica se container ElasticSearch existe (cria se necessário)
# 3. Aguarda o ElasticSearch ficar pronto para receber requisições
# 4. Exibe informações sobre o cluster
#
# USO:
#   ./initElastic.sh
#
# REQUISITOS:
# - Docker Desktop instalado
# - Permissão de execução: chmod +x initElastic.sh
#
################################################################################

# OPÇÃO BASH: Para em caso de erro
# -e: exit imediatamente se qualquer comando falhar
# Garante que não continuamos executando quando algo dá errado
set -e

echo "=================================================="
echo "INICIALIZANDO ELASTICSEARCH"
echo "=================================================="
echo ""

# === CONFIGURAÇÃO DE CORES PARA OUTPUT ===
# Códigos ANSI para colorir o terminal (melhor experiência visual)
GREEN='\033[0;32m'    # Verde: sucesso
YELLOW='\033[1;33m'   # Amarelo: avisos
RED='\033[0;31m'      # Vermelho: erros
NC='\033[0m'          # No Color: reseta cor

################################################################################
# PASSO 1: VERIFICAR E INICIAR DOCKER
################################################################################
# Docker é necessário para rodar o ElasticSearch em container

echo "1. Verificando Docker..."

# COMANDO: docker info
# - Retorna informações sobre o daemon Docker
# - Se falhar, significa que Docker não está rodando
# 
# REDIRECIONAMENTO:
# > /dev/null 2>&1 : descarta toda saída (stdout e stderr)
# - Queremos apenas o código de retorno (sucesso/falha)
#
# OPERADOR !: inverte o resultado
# - Se docker info falha (retorna não-zero), a condição é verdadeira

if ! docker info > /dev/null 2>&1; then
    # Docker não está rodando
    echo -e "${YELLOW}⚠ Docker não está rodando. Iniciando...${NC}"
    
    # COMANDO: open -a Docker
    # macOS: abre aplicação Docker Desktop
    # Equivalente a clicar no ícone do Docker
    open -a Docker
    
    echo "   Aguardando Docker iniciar..."
    
    # LOOP: Tenta conectar por até 30 segundos
    # {1..30} : sequência de 1 a 30
    for i in {1..30}; do
        # Tenta verificar se Docker já está respondendo
        if docker info > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Docker iniciado com sucesso!${NC}"
            break  # Sai do loop
        fi
        
        # Aguarda 1 segundo antes de tentar novamente
        sleep 1
        
        # Imprime ponto para mostrar progresso (sem quebra de linha)
        echo -n "."
    done
    echo ""  # Quebra de linha após os pontos
    
    # VERIFICAÇÃO FINAL: Se ainda não conseguiu conectar
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Erro: Docker não iniciou. Abra o Docker Desktop manualmente.${NC}"
        exit 1  # Sai do script com código de erro
    fi
else
    # Docker já está rodando
    echo -e "${GREEN}✓ Docker já está rodando${NC}"
fi
echo ""

################################################################################
# PASSO 2: VERIFICAR/CRIAR CONTAINER ELASTICSEARCH
################################################################################
# Container: instância isolada rodando ElasticSearch

echo "2. Verificando container ElasticSearch..."

# COMANDO: docker ps
# - Lista containers Docker
# -a: mostra TODOS (rodando e parados)
# --format '{{.Names}}': mostra apenas os nomes
#
# COMANDO: grep
# -q: quiet (não imprime nada, apenas retorna código)
# ^elasticsearch$: busca nome exato "elasticsearch"
#   ^ = início da linha
#   $ = fim da linha

if docker ps -a --format '{{.Names}}' | grep -q "^elasticsearch$"; then
    echo "   Container 'elasticsearch' encontrado"
    
    # Container existe, mas está rodando?
    # docker ps (sem -a): lista apenas containers RODANDO
    if docker ps --format '{{.Names}}' | grep -q "^elasticsearch$"; then
        echo -e "${GREEN}✓ ElasticSearch já está rodando!${NC}"
        CONTAINER_EXISTS=true
        ALREADY_RUNNING=true
    else
        # Container existe mas está parado
        echo "   Iniciando container existente..."
        
        # COMANDO: docker start
        # - Inicia um container que já existe mas está parado
        docker start elasticsearch
        
        CONTAINER_EXISTS=true
        ALREADY_RUNNING=false
    fi
else
    # Container não existe, precisamos criar
    echo "   Container não encontrado. Criando novo..."
    CONTAINER_EXISTS=false
    ALREADY_RUNNING=false
    
    # LIMPEZA: Remove containers antigos com outros nomes
    # 2>/dev/null: descarta mensagens de erro (caso não existam)
    # || true: garante que não falha mesmo se comando der erro
    docker rm -f es01 2>/dev/null || true
    
    # === CRIAR E INICIAR NOVO CONTAINER ===
    # COMANDO: docker run
    # -d: detached (roda em background)
    # -p: port mapping (porta_host:porta_container)
    # -e: environment variable (variável de ambiente)
    # --name: nome do container
    
    # IMPORTANTE: Usa versão 7.17.4 (última da série 7.x)
    # Versões 8.x removeram a similarity "classic" (TF-IDF)
    # Para fins didáticos de comparação BM25 vs TF-IDF, usamos 7.17.4
    docker run -d \
        -p 9200:9200 \
        -p 9300:9300 \
        -e "discovery.type=single-node" \
        -e "xpack.security.enabled=false" \
        -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
        --name elasticsearch \
        docker.elastic.co/elasticsearch/elasticsearch:7.17.4
    
    # EXPLICAÇÃO DOS PARÂMETROS:
    #
    # -p 9200:9200
    #   Porta HTTP REST API (principal interface do ElasticSearch)
    #   Mapeia porta 9200 do container para porta 9200 do host
    #
    # -p 9300:9300
    #   Porta de comunicação entre nodes (não usada em single-node)
    #
    # discovery.type=single-node
    #   Modo single-node (não forma cluster)
    #   Ideal para desenvolvimento e testes
    #
    # xpack.security.enabled=false
    #   Desabilita autenticação (facilita desenvolvimento)
    #   ATENÇÃO: Não use em produção!
    #
    # ES_JAVA_OPTS=-Xms512m -Xmx512m
    #   Configuração da JVM (Java Virtual Machine)
    #   -Xms: memória inicial (512 MB)
    #   -Xmx: memória máxima (512 MB)
    #   Reduzido para não consumir muita RAM
    #
    # docker.elastic.co/elasticsearch/elasticsearch:7.17.4
    #   Imagem oficial do ElasticSearch versão 7.17.4
    #   Versão 7.x escolhida para suportar similarity "classic" (TF-IDF)
    
    echo -e "${GREEN}✓ Container criado${NC}"
fi
echo ""

################################################################################
# PASSO 3: AGUARDAR ELASTICSEARCH FICAR PRONTO
################################################################################
# ElasticSearch leva alguns segundos para inicializar completamente

# Se já estava rodando, não precisa aguardar
if [ "$ALREADY_RUNNING" = false ]; then
    echo "3. Aguardando ElasticSearch ficar pronto..."
    
    # Configuração do loop de espera
    MAX_ATTEMPTS=30  # Máximo de tentativas (30 segundos)
    ATTEMPT=0        # Contador de tentativas
    
    # LOOP: Tenta conectar até conseguir ou atingir limite
    # [ $ATTEMPT -lt $MAX_ATTEMPTS ]: enquanto tentativas < máximo
    # -lt: less than (menor que)
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        
        # COMANDO: curl
        # -s: silent (não mostra progresso)
        # > /dev/null 2>&1: descarta saída
        # Tenta fazer requisição HTTP para ElasticSearch
        
        if curl -s http://localhost:9200 > /dev/null 2>&1; then
            # Sucesso! ElasticSearch respondeu
            echo -e "${GREEN}✓ ElasticSearch está pronto!${NC}"
            break  # Sai do loop
        fi
        
        # Incrementa contador
        # $((...)) : aritmética em bash
        ATTEMPT=$((ATTEMPT + 1))
        
        # Aguarda 1 segundo
        sleep 1
        
        # Mostra progresso
        echo -n "."
    done
    echo ""
    
    # VERIFICAÇÃO: Atingiu timeout sem sucesso?
    # -eq: equal (igual)
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}❌ Timeout: ElasticSearch não respondeu em 30s${NC}"
        echo "   Verificar logs: docker logs elasticsearch"
        echo "   Possíveis causas:"
        echo "     - Memória insuficiente"
        echo "     - Porta 9200 já em uso"
        echo "     - Erro na inicialização"
        exit 1  # Sai com erro
    fi
else
    echo "3. ElasticSearch já estava rodando"
fi
echo ""

################################################################################
# PASSO 4: EXIBIR INFORMAÇÕES DO ELASTICSEARCH
################################################################################

echo "4. Informações do ElasticSearch:"

# COMANDO: curl -s http://localhost:9200
# Faz requisição GET para a raiz da API do ElasticSearch
# Retorna JSON com informações do cluster: nome, versão, etc.
ES_INFO=$(curl -s http://localhost:9200)

# Tenta formatar JSON de forma legível usando python
# python3 -m json.tool: módulo que formata JSON
# 2>/dev/null: descarta erros caso python não esteja disponível
# || echo "$ES_INFO": se falhar, apenas exibe JSON sem formatação
echo "$ES_INFO" | python3 -m json.tool 2>/dev/null || echo "$ES_INFO"
echo ""

################################################################################
# MENSAGEM FINAL: SUCESSO
################################################################################

echo "=================================================="
echo -e "${GREEN}✓ ELASTICSEARCH PRONTO PARA USO!${NC}"
echo "=================================================="
echo ""

# === INFORMAÇÕES ÚTEIS ===
echo "URLs úteis:"
echo "  - Base: http://localhost:9200"
echo "    (Informações gerais do cluster)"
echo ""
echo "  - Health: http://localhost:9200/_cluster/health"
echo "    (Status de saúde do cluster: green, yellow, red)"
echo ""
echo "  - Índice ementes: http://localhost:9200/ementes/_search"
echo "    (Busca no índice de ementas - após indexar)"
echo ""

# === COMANDOS ÚTEIS ===
echo "Próximos passos e comandos úteis:"
echo ""
echo "  INDEXAR DADOS:"
echo "    python indexa.py"
echo "    (Cria índice e indexa documentos do JSON)"
echo ""
echo "  EXECUTAR BUSCAS:"
echo "    python busca.py"
echo "    (Exemplos didáticos de diferentes tipos de busca)"
echo ""
echo "  VERIFICAR LOGS:"
echo "    docker logs elasticsearch"
echo "    (Útil para debugging)"
echo ""
echo "  LOGS EM TEMPO REAL:"
echo "    docker logs -f elasticsearch"
echo "    (-f: follow, acompanha logs ao vivo)"
echo ""
echo "  PARAR ELASTICSEARCH:"
echo "    docker stop elasticsearch"
echo "    (Para o container mas não remove)"
echo ""
echo "  REINICIAR ELASTICSEARCH:"
echo "    docker restart elasticsearch"
echo "    (Para e inicia novamente)"
echo ""
echo "  REMOVER CONTAINER:"
echo "    docker rm -f elasticsearch"
echo "    (Remove completamente - dados são perdidos!)"
echo ""

################################################################################
# DICAS PARA ALUNOS
################################################################################

echo "DICAS:"
echo "  - Este script pode ser executado múltiplas vezes com segurança"
echo "  - ElasticSearch continuará rodando em background até ser parado"
echo "  - Dados são perdidos ao remover o container (use volumes para persistência)"
echo "  - Em produção, sempre use segurança habilitada (xpack.security)"
echo ""
