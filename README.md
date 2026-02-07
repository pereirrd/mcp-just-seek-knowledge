[Português](README.pt-br.md) | [Español](README.es.md)

# mcp-just-seek-knowledge

MCP (Model Context Protocol) server that stores and searches AI-generated knowledge about software projects, allowing Cursor to access information about project structures, design patterns, best practices, and technical documentation.

---

## 📋 About the Project

### Objective

Create an MCP server that stores and searches AI-generated knowledge about software projects.

### Technology Stack

- **Language**: Python
- **Embedding Framework**: LangChain
- **Database**: PostgreSQL with pgVector
- **Protocol**: MCP (Model Context Protocol) for Cursor integration

### Main Features

1. **Ingest**: Create new records in the knowledge base
2. **Update**: Update existing records in the knowledge base
3. **Search**: Semantic search in the database
4. **List Catalog**: List all existing `service_name` in the database (exposed as MCP tool)
5. **Delete**: Delete records by `service_name` (available via CLI script, not exposed as MCP tool)

---

## 🛠️ Environment Setup

### Complete Setup Process

#### 1. Clone the project or navigate to it (if needed)

```bash
cd /home/pereirrd/dev/git/pereirrd/mcp-just-seek-knowledge
```

#### 2. Create and activate virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/WSL:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure environment variables

Create a `.env` file in the project root (copy from `.env.example` if it exists, or create manually):

```bash
# Example .env
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5433/software_design_knowledge
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=software_design_knowledge
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**Note:** PostgreSQL variables can also be configured in Cursor's `mcp.json` (see section below).

#### 5. Start PostgreSQL (if using Docker Compose)

```bash
docker-compose up -d
```

This will create PostgreSQL with pgvector automatically on port `5433`.

**Important:** If port `5432` is already in use, `docker-compose.yml` is configured to automatically use port `5433`.

#### 6. Test the MCP server (optional)

```bash
python src/mcp_server.py
```

The server should start without errors and automatically create the `software_design_knowledge` table if it doesn't exist.

### Verify Installation

To verify if dependencies were installed correctly:

```bash
pip list | grep -E "langchain|psycopg|openai|python-dotenv"
```

Or test imports directly:

```bash
python -c "from src.database.connection import get_connection_string; from src.mcp.mcp_server import MCPServer; print('✅ Dependencies installed correctly!')"
```

---

## ⚙️ Cursor Configuration

To add this MCP server to Cursor, configure the `~/.cursor/mcp.json` file (global configuration) or `.cursor/mcp.json` in the project root (local configuration).

### Example configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/absolute/path/to/project/src/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Important:**
- Use absolute paths in the `args` field
- Configure all necessary environment variables
- Cursor loads this file automatically on startup
- After adding, restart Cursor to load the MCP server

### Note about Cursor

When configuring MCP in Cursor (`~/.cursor/mcp.json`), Cursor will use the system Python or the one active in PATH. Recommendations:

#### Option 1: Use global Python (install dependencies globally)

If you prefer to use the system's global Python:

```bash
pip install -r requirements.txt
```

And configure `mcp.json` with:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/absolute/path/to/project/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

#### Option 2: Use virtual environment Python (recommended)

To use the project's virtual environment, specify the full path to the venv Python in `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "/absolute/path/to/mcp-just-seek-knowledge/venv/bin/python",
      "args": ["/absolute/path/to/mcp-just-seek-knowledge/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Advantages of Option 2:**
- Isolates project dependencies
- Avoids conflicts with other Python projects
- Facilitates version management

**Note:** The project's `.env` file will be automatically loaded by the MCP server, so you don't need to repeat PostgreSQL variables in `mcp.json` (unless you prefer).

---

## 🚀 Implementation

### Preparation and Structure

#### Directory Structure

Created `src/` structure with organized subdirectories:

- `src/database/` - Database management
- `src/embeddings/` - Embedding services
- `src/services/` - Business services (ingest, update, search)
- `src/mcp/` - MCP server and handlers

`__init__.py` files created in all Python packages.

#### Dependency Configuration

`requirements.txt` file created with all necessary dependencies:

- **LangChain Framework**: langchain, langchain-community, langchain-core, langchain-openai, langchain-postgres
- **PostgreSQL**: psycopg, pgvector
- **OpenAI**: openai
- **Utilities**: python-dotenv

#### Environment Variables

`.env.example` file created with all necessary variables:

- `PGVECTOR_URL` - PostgreSQL connection URL
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL`
- `EMBEDDING_DIMENSION`

`.gitignore` file configured to exclude `.env` and Python and IDE files.

#### Docker and PostgreSQL

`docker-compose.yml` file created with:

- PostgreSQL service using `pgvector/pgvector:pg16` image
- Volume configuration for persistence
- Healthcheck configured
- Ports and environment variables configured

Initialization script `init-scripts/01-init-pgvector.sh` to automatically create the pgvector extension.

---

### Database Configuration

#### Database Schema (`src/database/schema.py`)

**Structure of `software_design_knowledge` table (software project knowledge):**

- `id` - Unique identifier (SERIAL PRIMARY KEY)
- `service_name` - Service name (VARCHAR(255) NOT NULL UNIQUE)
- `content` - Knowledge content (TEXT NOT NULL)
- `embedding` - Embedding vector (vector(1536) NOT NULL)
- `metadata` - Additional metadata (JSONB)
- `created_at` - Creation date (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` - Update date (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

**Indexes:**

- IVFFlat index for optimized vector search
- Index for `service_name` for service searches

**Triggers:**

- Automatic trigger to update `updated_at` on updates

#### Connection Management (`src/database/connection.py`)

Implemented functions:

- `get_connection_string()` - Gets connection string from environment variables
- `create_connection()` - Creates PostgreSQL connections
- `schema_exists()` - Checks if table exists
- `create_schema()` - Creates complete schema (table, indexes, triggers)
- `initialize_database()` - Initializes the database

Error handling and logging implemented.

#### Data Repository (`src/database/repository.py`)

**`KnowledgeRepository` class** implemented using `psycopg` directly.

**Implemented methods:**

- `insert()` - Insert document into database
- `update()` - Update document by service_name
- `upsert()` - Insert or update (upsert behavior)
- `delete()` - Delete document by service_name
- `get_by_service_name()` - Search document by service_name
- `similarity_search()` - Semantic search using pgVector (`<=>` operator)

**Features:**

- Support for optional filters (similarity threshold, service_name filter)
- Integration with JSONB metadata structure


---

### Embedding Services

**`EmbeddingService` class** (`src/embeddings/embedding_service.py`) using `OpenAIEmbeddings` from LangChain.

**Features:**
- Single and batch embedding creation
- Configuration via environment variables (default model: `text-embedding-3-small`)
- Error handling and logging

---

### Business Services

**Four main services implemented:**

#### Ingest Service (`src/services/ingest_service.py`)
- Adds new knowledge to the database
- Validates `service_name` and `content`
- Automatically creates embedding
- Complete error handling

#### Update Service (`src/services/update_service.py`)
- Updates existing knowledge (upsert behavior)
- If `service_name` doesn't exist, creates new record
- If exists, updates existing record
- Automatically updates embedding

#### Search Service (`src/services/search_service.py`)
- Semantic search by similarity
- Optional parameters: `k` (number of results), `threshold` (minimum similarity), `service_name` (filter)
- Returns results ordered by relevance

#### List Catalog Service (`src/services/list_catalog_service.py`)
- Lists all existing `service_name` in the database
- Does not use embeddings (repository only)

**Common features:**
- Integration with `EmbeddingService` and `KnowledgeRepository`
- Input validation
- Error handling
- Detailed logging
- Structured returns

---

## 🗑️ CLI Scripts

### Record Deletion

The project includes a CLI script for record deletion that **is not exposed as an MCP tool**. This functionality is only available via command line for administrative operations.

#### Script: `src/database/delete_service.py`

**Functionality:**
- Deletes a record from the knowledge base by `service_name`
- Validates record existence before deletion
- Provides clear feedback on operation result

**Usage:**

```bash
python src/database/delete_service.py <service_name>
```

**Examples:**

```bash
# Delete a specific service
python src/database/delete_service.py user-service

# The script returns:
# - ✓ "Record deleted successfully" if the record was found and removed
# - ✗ "Record not found" if the service_name doesn't exist
# - ✗ "Error deleting record" in case of operation failure
```

**Features:**
- Parameter validation (service_name cannot be empty)
- Error handling with detailed logging
- Appropriate exit codes (0 for success, 1 for failure)
- Clear feedback messages for the user

**Note:** This functionality is not available as an MCP tool for security and access control reasons. Use only for necessary administrative operations.

---

## 📚 pgvector Initialization Script

The `init-scripts/01-init-pgvector.sh` script is automatically used by PostgreSQL during container initialization.

### How it works

**1. Volume mapped in docker-compose.yml**

The local `init-scripts/` directory is mapped to `/docker-entrypoint-initdb.d` inside the container through volume configuration in docker-compose.yml.

**2. PostgreSQL automatic behavior**

The official PostgreSQL image (including pgvector/pgvector) automatically executes all files present in `/docker-entrypoint-initdb.d` when:

- The database is initialized for the first time (when the data volume is empty)
- Files are executed in alphabetical order (hence the 01- prefix)
- Accepts .sql, .sh and other executable files

**3. What the script does**

The `01-init-pgvector.sh` script:

- Executes `CREATE EXTENSION IF NOT EXISTS vector;` to create the pgvector extension
- Lists installed extensions for verification
- Uses `set -e` to stop on error

### Important

- Scripts in `init-scripts/` are only executed on first initialization (when volume is empty)
- If the container has been started before, the script will not be executed again
- To re-execute, it's necessary to remove the volume: `docker-compose down -v`

---

## ⌨️ Cursor Commands (Slash Commands)

This repository includes custom Cursor commands in `.cursor/commands/`, which help **create, update, and list** the knowledge base in the MCP `mcp-just-seek-knowledge`.

### Available commands

- **`/criar_base_conhecimento`**: analyzes the entire open workspace (all projects/directories), reads documentation (including Swagger/OpenAPI) and **creates** a unique record for the workspace using `mcp-just-seek-knowledge.ingest`.
- **`/atualizar_base_conhecimento`**: same analysis as the previous command, but **updates** (upsert) the workspace record using `mcp-just-seek-knowledge.update`.
- **`/listar_base_conhecimento`**: lists existing `service_name` via `mcp-just-seek-knowledge.list_catalog` and presents a friendly layout with `count`, `service_name` and `metadata` (enriched via `mcp-just-seek-knowledge.search`).

### How to use

1. Ensure the MCP `mcp-just-seek-knowledge` is configured in Cursor (`~/.cursor/mcp.json` or `.cursor/mcp.json`).
2. Open the project(s) in the Cursor workspace.
3. In Cursor chat, execute a command by typing:
   - `/criar_base_conhecimento`
   - `/atualizar_base_conhecimento`
   - `/listar_base_conhecimento`
