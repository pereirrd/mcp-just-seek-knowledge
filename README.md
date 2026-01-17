# mcp-just-seek-knowledge

Servidor MCP (Model Context Protocol) que armazena e busca conhecimento gerado por IA sobre projetos de software, permitindo ao Cursor acessar informações sobre estruturas de projetos, padrões de projeto, boas práticas e documentação técnica.

---

## 📋 Sobre o Projeto

### Objetivo

Criar um servidor MCP que armazena e busca conhecimento gerado por IA sobre projetos de software.

### Stack Tecnológica

- **Linguagem**: Python
- **Framework para Embeddings**: LangChain
- **Banco de Dados**: PostgreSQL com pgVector
- **Protocolo**: MCP (Model Context Protocol) para integração com Cursor

### Funcionalidades Principais

1. **Ingest**: Criar novos registros na base de conhecimento
2. **Update**: Atualizar registros existentes na base de conhecimento
3. **Search**: Buscar conhecimento semântico na base

---

## 🛠️ Configuração do Ambiente

### Processo Completo de Configuração

#### 1. Clone o projeto ou navegue até ele (se necessário)

```bash
cd /home/pereirrd/dev/git/pereirrd/mcp-just-seek-knowledge
```

#### 2. Crie e ative ambiente virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No Linux/WSL:
source venv/bin/activate

# No Windows:
# venv\Scripts\activate
```

#### 3. Instale dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (copie de `.env.example` se existir, ou crie manualmente):

```bash
# Exemplo de .env
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5433/software_design_knowledge
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=software_design_knowledge
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
OPENAI_API_KEY=sua_chave_api_openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**Nota:** As variáveis do PostgreSQL também podem ser configuradas no `mcp.json` do Cursor (veja seção abaixo).

#### 5. Inicie PostgreSQL (se usar Docker Compose)

```bash
docker-compose up -d
```

Isso criará o PostgreSQL com pgvector automaticamente na porta `5433`.

**Importante:** Se a porta `5432` já estiver em uso, o `docker-compose.yml` está configurado para usar a porta `5433` automaticamente.

#### 6. Teste o servidor MCP (opcional)

```bash
python src/mcp_server.py
```

O servidor deve iniciar sem erros e criar automaticamente a tabela `software_design_knowledge` se não existir.

### Verificar Instalação

Para verificar se as dependências foram instaladas corretamente:

```bash
pip list | grep -E "langchain|psycopg|openai|python-dotenv"
```

Ou teste os imports diretamente:

```bash
python -c "from src.database.connection import get_connection_string; from src.mcp.mcp_server import MCPServer; print('✅ Dependências instaladas corretamente!')"
```

---

## ⚙️ Configuração no Cursor

Para adicionar este servidor MCP no Cursor, configure o arquivo `~/.cursor/mcp.json` (configuração global) ou `.cursor/mcp.json` na raiz do projeto (configuração local).

### Exemplo de configuração (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/caminho/absoluto/para/projeto/src/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sua_chave_api_openai",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Importante:**
- Use caminhos absolutos no campo `args`
- Configure todas as variáveis de ambiente necessárias
- O Cursor carrega este arquivo automaticamente ao iniciar
- Após adicionar, reinicie o Cursor para carregar o servidor MCP

### Nota sobre o Cursor

Ao configurar o MCP no Cursor (`~/.cursor/mcp.json`), o Cursor usará o Python do sistema ou o ativo no PATH. Recomendações:

#### Opção 1: Usar o Python global (instalar dependências globalmente)

Se preferir usar o Python global do sistema:

```bash
pip install -r requirements.txt
```

E configure o `mcp.json` com:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/caminho/absoluto/para/projeto/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

#### Opção 2: Usar o Python do ambiente virtual (recomendado)

Para usar o ambiente virtual do projeto, especifique o caminho completo do Python do venv no `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "/caminho/absoluto/para/mcp-just-seek-knowledge/venv/bin/python",
      "args": ["/caminho/absoluto/para/mcp-just-seek-knowledge/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Vantagens da Opção 2:**
- Isola as dependências do projeto
- Evita conflitos com outros projetos Python
- Facilita gerenciamento de versões

**Nota:** O arquivo `.env` do projeto será carregado automaticamente pelo servidor MCP, então você não precisa repetir as variáveis do PostgreSQL no `mcp.json` (a menos que prefira).

---

## 🚀 Implementação

### Preparação e Estrutura

#### Estrutura de Diretórios

Criada estrutura `src/` com subdiretórios organizados:

- `src/database/` - Gerenciamento de banco de dados
- `src/embeddings/` - Serviços de embeddings
- `src/services/` - Serviços de negócio (ingest, update, search)
- `src/mcp/` - Servidor MCP e handlers

Arquivos `__init__.py` criados em todos os pacotes Python.

#### Configuração de Dependências

Arquivo `requirements.txt` criado com todas as dependências necessárias:

- **LangChain Framework**: langchain, langchain-community, langchain-core, langchain-openai, langchain-postgres
- **PostgreSQL**: psycopg, pgvector
- **OpenAI**: openai
- **Utilidades**: python-dotenv

#### Variáveis de Ambiente

Arquivo `.env.example` criado com todas as variáveis necessárias:

- `PGVECTOR_URL` - URL de conexão PostgreSQL
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL`
- `EMBEDDING_DIMENSION`

Arquivo `.gitignore` configurado para excluir `.env` e arquivos Python e de IDE.

#### Docker e PostgreSQL

Arquivo `docker-compose.yml` criado com:

- Serviço PostgreSQL usando imagem `pgvector/pgvector:pg16`
- Configuração de volumes para persistência
- Healthcheck configurado
- Portas e variáveis de ambiente configuradas

Script de inicialização `init-scripts/01-init-pgvector.sh` para criar a extensão pgvector automaticamente.

---

### Configuração do Banco de Dados

#### Schema do Banco (`src/database/schema.py`)

**Estrutura da tabela `software_design_knowledge` (conhecimento de projetos de software):**

- `id` - Identificador único (SERIAL PRIMARY KEY)
- `service_name` - Nome do serviço (VARCHAR(255) NOT NULL UNIQUE)
- `content` - Conteúdo do conhecimento (TEXT NOT NULL)
- `embedding` - Vetor de embedding (vector(1536) NOT NULL)
- `metadata` - Metadados adicionais (JSONB)
- `created_at` - Data de criação (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` - Data de atualização (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

**Índices:**

- Índice IVFFlat para busca vetorial otimizada
- Índice para `service_name` para buscas por serviço

**Triggers:**

- Trigger automático para atualizar `updated_at` em atualizações

#### Gerenciamento de Conexão (`src/database/connection.py`)

Funções implementadas:

- `get_connection_string()` - Obtém string de conexão das variáveis de ambiente
- `create_connection()` - Cria conexões PostgreSQL
- `schema_exists()` - Verifica se a tabela existe
- `create_schema()` - Cria schema completo (tabela, índices, triggers)
- `initialize_database()` - Inicializa o banco de dados

Tratamento de erros e logging implementados.

#### Repositório de Dados (`src/database/repository.py`)

**Classe `KnowledgeRepository`** implementada usando `psycopg` diretamente.

**Métodos implementados:**

- `insert()` - Inserir documento no banco
- `update()` - Atualizar documento por service_name
- `upsert()` - Inserir ou atualizar (comportamento upsert)
- `get_by_service_name()` - Buscar documento por service_name
- `similarity_search()` - Busca semântica usando pgVector (operador `<=>`)

**Funcionalidades:**

- Suporte a filtros opcionais (threshold de similaridade, filtro por service_name)
- Integração com estrutura de metadados JSONB


---

### Serviços de Embeddings

**Classe `EmbeddingService`** (`src/embeddings/embedding_service.py`) usando `OpenAIEmbeddings` do LangChain.

**Funcionalidades:**
- Criação de embedding único e em batch
- Configuração via variáveis de ambiente (modelo padrão: `text-embedding-3-small`)
- Tratamento de erros e logging

---

### Serviços de Negócio

**Três serviços principais implementados:**

#### Ingest Service (`src/services/ingest_service.py`)
- Adiciona novo conhecimento na base
- Valida `service_name` e `content`
- Cria embedding automaticamente
- Tratamento de erros completo

#### Update Service (`src/services/update_service.py`)
- Atualiza conhecimento existente (comportamento upsert)
- Se `service_name` não existe, cria novo registro
- Se existe, atualiza o registro existente
- Atualiza embedding automaticamente

#### Search Service (`src/services/search_service.py`)
- Busca semântica por similaridade
- Parâmetros opcionais: `k` (número de resultados), `threshold` (similaridade mínima), `service_name` (filtro)
- Retorna resultados ordenados por relevância

**Funcionalidades comuns:**
- Integração com `EmbeddingService` e `KnowledgeRepository`
- Validação de entrada
- Tratamento de erros
- Logging detalhado
- Retornos estruturados

---

## 📚 Script de Inicialização do pgvector

O script `init-scripts/01-init-pgvector.sh` é usado automaticamente pelo PostgreSQL durante a inicialização do container.

### Como funciona

**1. Volume mapeado no docker-compose.yml**

O diretório local `init-scripts/` é mapeado para `/docker-entrypoint-initdb.d` dentro do container através da configuração de volume no docker-compose.yml.

**2. Comportamento automático do PostgreSQL**

A imagem oficial do PostgreSQL (incluindo pgvector/pgvector) executa automaticamente todos os arquivos presentes em `/docker-entrypoint-initdb.d` quando:

- O banco de dados é inicializado pela primeira vez (quando o volume de dados está vazio)
- Os arquivos são executados em ordem alfabética (por isso o prefixo 01-)
- Aceita arquivos .sql, .sh e outros executáveis

**3. O que o script faz**

O script `01-init-pgvector.sh`:

- Executa `CREATE EXTENSION IF NOT EXISTS vector;` para criar a extensão pgvector
- Lista as extensões instaladas para verificação
- Usa `set -e` para parar em caso de erro

### Importante

- Os scripts em `init-scripts/` só são executados na primeira inicialização (quando o volume está vazio)
- Se o container já foi iniciado antes, o script não será executado novamente
- Para reexecutar, é necessário remover o volume: `docker-compose down -v`

---
