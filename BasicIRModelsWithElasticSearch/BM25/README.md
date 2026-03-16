# BM25 com ElasticSearch

Este diretório contém scripts para indexação e busca de ementas jurídicas usando ElasticSearch com o algoritmo BM25.

## Arquivos

- **initElastic.sh** - Script shell para iniciar Docker e ElasticSearch automaticamente
- **indexa.py** - Script para indexar ementas no ElasticSearch
- **busca.py** - Script de exemplo com diferentes tipos de buscas BM25
- **requirements.txt** - Dependências Python

## 🚀 Início Rápido

```bash
cd BasicIRModelsWithElasticSearch/BM25

# 1. Iniciar Docker e ElasticSearch (automático)
./initElastic.sh

# 2. Instalar dependências Python (primeira vez)
pip install -r requirements.txt

# 3. Indexar documentos
python indexa.py

# 4. Executar buscas de exemplo
python busca.py
```

## Requisitos

### 1. Instalar Python e dependências

```bash
# Opção 1: Instalar do requirements.txt
cd BasicIRModelsWithElasticSearch/BM25
pip install -r requirements.txt

# Opção 2: Instalar manualmente
pip install elasticsearch
```

### 2. Instalar e iniciar ElasticSearch

#### Opção Recomendada: Usar o script automatizado

```bash
./initElastic.sh
```

Este script:
- ✅ Verifica e inicia o Docker automaticamente
- ✅ Cria ou inicia o container ElasticSearch
- ✅ Aguarda o serviço ficar pronto
- ✅ Exibe informações e status
- ✅ Trata erros e timeouts

#### Alternativa: Instalação manual

##### macOS (usando Homebrew):
```bash
# Instalar
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full

# Iniciar
brew services start elastic/tap/elasticsearch-full

# Ou iniciar temporariamente
elasticsearch
```

#### Docker:
```bash
docker run -d -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  --name elasticsearch \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### 3. Verificar se ElasticSearch está rodando

```bash
curl http://localhost:9200
```

Deve retornar informações sobre o cluster ElasticSearch.

## Uso

### Indexar documentos

```bash
cd BasicIRModelsWithElasticSearch/BM25
python indexa.py
```

O script irá:
1. Conectar ao ElasticSearch local (porta 9200)
2. Criar o índice `ementes` com mapeamento apropriado
3. Ler os documentos de `../../dataSetExemplo/exEmentas.json`
4. Indexar todos os documentos
5. Exibir estatísticas da indexação

### Verificar o índice criado

```bash
# Ver informações do índice
curl http://localhost:9200/ementes

# Ver mapeamento
curl http://localhost:9200/ementes/_mapping

# Contar documentos
curl http://localhost:9200/ementes/_count

# Buscar todos os documentos (limitado a 10)
curl http://localhost:9200/ementes/_search?pretty
```

### Realizar buscas (script Python)

```bash
python busca.py
```

O script `busca.py` demonstra diferentes tipos de consultas:
- Busca simples em um campo
- Busca multi-campo com boost
- Busca booleana (termos obrigatórios e opcionais)
- Busca com filtros
- Busca por frase exata

## Estrutura dos Documentos

Cada documento possui os seguintes campos:

- **id** (keyword) - Identificador único do documento
- **title** (text) - Título da ementa/processo
- **highlight** (text) - Texto completo da ementa
- **judging_organ** (text) - Órgão julgador
- **type** (keyword) - Tipo de documento (ex: ACORDAO)

## Configuração do Índice

O índice é criado com as seguintes configurações:

- **Analyzer**: `brazilian_analyzer` com stopwords em português
- **Campos text**: Analisados para busca por texto completo
- **Campos keyword**: Para filtros e agregações exatas
- **Source**: Habilitado para todos os campos

## Algoritmo BM25

O ElasticSearch usa BM25 como algoritmo padrão de ranking desde a versão 5.0. BM25 (Best Matching 25) é uma função de ranking probabilística que considera:

- **Term Frequency (TF)**: Frequência do termo no documento
- **Inverse Document Frequency (IDF)**: Raridade do termo no corpus
- **Document Length Normalization**: Normalização pelo tamanho do documento

### Parâmetros BM25

- **k1** (default: 1.2): Controla saturação da frequência do termo
- **b** (default: 0.75): Controla o impacto do tamanho do documento

## Exemplo de Busca

### Via Python

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Busca simples
resultado = es.search(
    index='ementes',
    body={
        'query': {
            'match': {
                'highlight': 'responsabilidade civil danos morais'
            }
        },
        'size': 10
    }
)

for hit in resultado['hits']['hits']:
    print(f"Score: {hit['_score']}")
    print(f"Título: {hit['_source']['title']}")
    print(f"Órgão: {hit['_source']['judging_organ']}")
    print('-' * 80)
```

### Via curl

```bash
# Busca simples
curl -X GET "http://localhost:9200/ementes/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "highlight": "responsabilidade civil"
    }
  },
  "size": 5
}
'

# Busca multi-campo com boost
curl -X GET "http://localhost:9200/ementes/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "multi_match": {
      "query": "apelação",
      "fields": ["title^2", "highlight"]
    }
  }
}
'

# Busca booleana
curl -X GET "http://localhost:9200/ementes/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "highlight": "civil" }}
      ],
      "should": [
        { "match": { "highlight": "danos morais" }}
      ]
    }
  }
}
'
```

## Gerenciamento do ElasticSearch

### Iniciar ElasticSearch
```bash
# Usando o script (recomendado)
./initElastic.sh

# Ou manualmente via Docker
docker start elasticsearch

# Ou via Homebrew
brew services start elastic/tap/elasticsearch-full
```

### Verificar status
```bash
# Status do container
docker ps

# Health check
curl http://localhost:9200/_cluster/health?pretty

# Ver logs
docker logs elasticsearch

# Logs em tempo real
docker logs -f elasticsearch
```

### Parar ElasticSearch
```bash
# Via Docker
docker stop elasticsearch

# Via Homebrew
brew services stop elastic/tap/elasticsearch-full
```

### Reiniciar ElasticSearch
```bash
# Via Docker
docker restart elasticsearch

# Via Homebrew
brew services restart elastic/tap/elasticsearch-full
```

## Troubleshooting

### Docker não está rodando
```
Error: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```
**Solução**: Execute `./initElastic.sh` (inicia automaticamente) ou abra o Docker Desktop manualmente.

### ElasticSearch não está rodando
```
Erro: Erro ao conectar ao ElasticSearch
```
**Solução**: Execute `./initElastic.sh` ou inicie manualmente com `docker start elasticsearch`.

### Arquivo JSON não encontrado
```
Erro: Arquivo não encontrado: ../../dataSetExemplo/exEmentas.json
```
**Solução**: Verifique se o arquivo existe no caminho correto ou ajuste a variável `CAMINHO_JSON` no script.

### Problemas de memória
Se tiver muitos documentos, pode ser necessário aumentar a memória do ElasticSearch editando `jvm.options`:
```
-Xms1g
-Xmx1g
```
