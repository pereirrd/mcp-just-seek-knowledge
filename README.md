# mcp-just-seek-knowledge

Servidor MCP (Model Context Protocol) que armazena e busca conhecimento gerado por IA sobre projetos Java de APIs REST, permitindo ao Cursor acessar informações sobre estruturas de APIs, padrões de projeto, boas práticas e documentação técnica.

---

## 📋 Sobre o Projeto

### Objetivo

Criar um servidor MCP que armazena e busca conhecimento gerado por IA sobre projetos Java de APIs REST.

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

Arquivo `.gitignore` configurado para excluir `.env` e arquivos Python/IDE.

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

**Estrutura da tabela `java_api_knowledge`:**

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

#### Serviço de Embeddings (`src/embeddings/embedding_service.py`)

**Classe `EmbeddingService`** implementada usando `OpenAIEmbeddings` do LangChain.

**Funcionalidades:**

- Método `create_embedding()` - Criar embedding de um texto único
- Método `create_embeddings_batch()` - Criar embeddings em batch (otimização)
- Configuração do modelo via variáveis de ambiente (padrão: `text-embedding-3-small`)
- Tratamento de erros implementado
- Logging para debug
- Suporte a configuração flexível (modelo e API key via variáveis de ambiente ou parâmetros)

**Métodos internos:**

- Embedding único usando `embed_query()`
- Embeddings em batch usando `embed_documents()`

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
