$ErrorActionPreference = 'Stop'

function Write-Status {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )

    Write-Host $Message -ForegroundColor $Color
}

function Test-DockerRunning {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'

    try {
        & docker info 1>$null 2>$null
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Get-DockerContainerNames {
    param(
        [switch]$All
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'

    try {
        if ($All) {
            $output = & docker ps -a --format '{{.Names}}' 2>$null
        }
        else {
            $output = & docker ps --format '{{.Names}}' 2>$null
        }

        if ($LASTEXITCODE -ne 0 -or -not $output) {
            return @()
        }

        return @($output)
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Start-DockerDesktop {
    $dockerDesktopPaths = @(
        "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$Env:LocalAppData\Programs\Docker\Docker\Docker Desktop.exe"
    )

    $dockerDesktopExe = $dockerDesktopPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($dockerDesktopExe) {
        Start-Process -FilePath $dockerDesktopExe | Out-Null
        return
    }

    Start-Process -FilePath "Docker Desktop" | Out-Null
}

function Invoke-ElasticRequest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri
    )

    return Invoke-RestMethod -Uri $Uri -TimeoutSec 5
}

Write-Host "=================================================="
Write-Host "INICIALIZANDO ELASTICSEARCH"
Write-Host "=================================================="
Write-Host ""

Write-Host "1. Verificando Docker..."

if (-not (Test-DockerRunning)) {
    Write-Status "[AVISO] Docker nao esta rodando. Iniciando..." Yellow

    try {
        Start-DockerDesktop
    }
    catch {
        Write-Status "[ERRO] Falha ao tentar abrir o Docker Desktop: $($_.Exception.Message)" Red
        exit 1
    }

    Write-Host "   Aguardando Docker iniciar..."

    for ($i = 0; $i -lt 30; $i++) {
        if (Test-DockerRunning) {
            Write-Status "[OK] Docker iniciado com sucesso!" Green
            break
        }

        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
    }

    Write-Host ""

    if (-not (Test-DockerRunning)) {
        Write-Status "[ERRO] Docker nao iniciou. Abra o Docker Desktop manualmente." Red
        exit 1
    }
}
else {
    Write-Status "[OK] Docker ja esta rodando" Green
}

Write-Host ""
Write-Host "2. Verificando container ElasticSearch..."

$allContainers = Get-DockerContainerNames -All
$runningContainers = Get-DockerContainerNames
$containerExists = $allContainers -contains 'elasticsearch'
$alreadyRunning = $false

if ($containerExists) {
    Write-Host "   Container 'elasticsearch' encontrado"

    if ($runningContainers -contains 'elasticsearch') {
        Write-Status "[OK] ElasticSearch ja esta rodando!" Green
        $alreadyRunning = $true
    }
    else {
        Write-Host "   Iniciando container existente..."
        & docker start elasticsearch 2>$null | Out-Null

        if ($LASTEXITCODE -ne 0) {
        Write-Status "[ERRO] Falha ao iniciar o container 'elasticsearch'." Red
            exit 1
        }
    }
}
else {
    Write-Host "   Container nao encontrado. Criando novo..."

    try {
        & docker rm -f es01 1>$null 2>$null
    }
    catch {
    }

    & docker run -d `
        -p 9200:9200 `
        -p 9300:9300 `
        -e "discovery.type=single-node" `
        -e "xpack.security.enabled=false" `
        -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" `
        --name elasticsearch `
        docker.elastic.co/elasticsearch/elasticsearch:7.17.4 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Write-Status "[ERRO] Falha ao criar o container ElasticSearch." Red
        exit 1
    }

    Write-Status "[OK] Container criado" Green
}

Write-Host ""

if (-not $alreadyRunning) {
    Write-Host "3. Aguardando ElasticSearch ficar pronto..."

    $maxAttempts = 30
    $attempt = 0
    $elasticReady = $false

    while ($attempt -lt $maxAttempts) {
        try {
            $null = Invoke-ElasticRequest -Uri 'http://localhost:9200'
            $elasticReady = $true
            Write-Status "[OK] ElasticSearch esta pronto!" Green
            break
        }
        catch {
            $attempt++
            Start-Sleep -Seconds 1
            Write-Host "." -NoNewline
        }
    }

    Write-Host ""

    if (-not $elasticReady) {
        Write-Status "[ERRO] Timeout: ElasticSearch nao respondeu em 30s" Red
        Write-Host "   Verificar logs: docker logs elasticsearch"
    Write-Host "   Possiveis causas:"
        Write-Host "     - Memoria insuficiente"
        Write-Host "     - Porta 9200 ja em uso"
        Write-Host "     - Erro na inicializacao"
        exit 1
    }
}
else {
    Write-Host "3. ElasticSearch ja estava rodando"
}

Write-Host ""
Write-Host "4. Informacoes do ElasticSearch:"

try {
    $esInfo = Invoke-ElasticRequest -Uri 'http://localhost:9200'
    $esInfo | ConvertTo-Json -Depth 10
}
catch {
    Write-Status "[ERRO] Nao foi possivel obter informacoes do ElasticSearch: $($_.Exception.Message)" Red
    exit 1
}

Write-Host ""
Write-Host "=================================================="
Write-Status "[OK] ELASTICSEARCH PRONTO PARA USO!" Green
Write-Host "=================================================="
Write-Host ""

Write-Host "URLs uteis:"
Write-Host "  - Base: http://localhost:9200"
Write-Host "    (Informacoes gerais do cluster)"
Write-Host ""
Write-Host "  - Health: http://localhost:9200/_cluster/health"
Write-Host "    (Status de saude do cluster: green, yellow, red)"
Write-Host ""
Write-Host "  - Indice ementes: http://localhost:9200/ementes/_search"
Write-Host "    (Busca no indice de ementas - apos indexar)"
Write-Host ""

Write-Host "Proximos passos e comandos uteis:"
Write-Host ""
Write-Host "  INDEXAR DADOS:"
Write-Host "    python indexa.py"
Write-Host "    (Cria indice e indexa documentos do JSON)"
Write-Host ""
Write-Host "  EXECUTAR BUSCAS:"
Write-Host "    python busca.py"
Write-Host "    (Exemplos didaticos de diferentes tipos de busca)"
Write-Host ""
Write-Host "  VERIFICAR LOGS:"
Write-Host "    docker logs elasticsearch"
Write-Host "    (Util para debugging)"
Write-Host ""
Write-Host "  LOGS EM TEMPO REAL:"
Write-Host "    docker logs -f elasticsearch"
Write-Host "    (-f: follow, acompanha logs ao vivo)"
Write-Host ""
Write-Host "  PARAR ELASTICSEARCH:"
Write-Host "    docker stop elasticsearch"
Write-Host "    (Para o container mas nao remove)"
Write-Host ""
Write-Host "  REINICIAR ELASTICSEARCH:"
Write-Host "    docker restart elasticsearch"
Write-Host "    (Para e inicia novamente)"
Write-Host ""
Write-Host "  REMOVER CONTAINER:"
Write-Host "    docker rm -f elasticsearch"
Write-Host "    (Remove completamente - dados sao perdidos!)"
Write-Host ""

Write-Host "DICAS:"
Write-Host "  - Este script pode ser executado multiplas vezes com seguranca"
Write-Host "  - ElasticSearch continuara rodando em background ate ser parado"
Write-Host "  - Dados sao perdidos ao remover o container (use volumes para persistencia)"
Write-Host "  - Em producao, sempre use seguranca habilitada (xpack.security)"
Write-Host ""
