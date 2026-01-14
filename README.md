# mcp-just-seek-knowledge

## Script de Inicialização do pgvector

O script `init-scripts/01-init-pgvector.sh` é usado automaticamente pelo PostgreSQL durante a inicialização do container.

### Como funciona:

**1. Volume mapeado no docker-compose.yml:**
O diretório local `init-scripts/` é mapeado para `/docker-entrypoint-initdb.d` dentro do container através da configuração de volume no docker-compose.yml.

**2. Comportamento automático do PostgreSQL:**
A imagem oficial do PostgreSQL (incluindo pgvector/pgvector) executa automaticamente todos os arquivos presentes em `/docker-entrypoint-initdb.d` quando:
- O banco de dados é inicializado pela primeira vez (quando o volume de dados está vazio)
- Os arquivos são executados em ordem alfabética (por isso o prefixo 01-)
- Aceita arquivos .sql, .sh e outros executáveis

**3. O que o script faz:**
O script 01-init-pgvector.sh:
- Executa CREATE EXTENSION IF NOT EXISTS vector; para criar a extensão pgvector
- Lista as extensões instaladas para verificação
- Usa set -e para parar em caso de erro

**Importante:**
- Os scripts em init-scripts/ só são executados na primeira inicialização (quando o volume está vazio)
- Se o container já foi iniciado antes, o script não será executado novamente
- Para reexecutar, é necessário remover o volume: docker-compose down -v
