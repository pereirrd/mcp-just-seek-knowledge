# 📚 Resumo de Contexto - Sistema RAG e MCP

## 🎯 Visão Geral

Este documento resume todo o conhecimento adquirido sobre:
- Sistema RAG (Retrieval-Augmented Generation)
- pgVector e PostgreSQL
- Embeddings
- Servidores MCP (Model Context Protocol)
- LangChain vs Implementação Direta

---

## 1. 🔢 O que são Embeddings?

### Definição
**Embedding** = Representação numérica de texto em forma de vetor (lista de números).

### Características
- Texto similar → Vetores próximos no espaço numérico
- Texto diferente → Vetores distantes
- Permite busca semântica (por significado, não palavras exatas)

### Como Criar Embeddings
- **NÃO precisa de agente IA**
- Precisa de **Modelo de Embedding** (ex: `text-embedding-3-small`)
- Usa API ou biblioteca para chamar o modelo
- Exemplo: `openai.embeddings.create(model="text-embedding-3-small", input=texto)`

### Modelos Comuns
- `text-embedding-3-small` → 1536 dimensões
- `text-embedding-3-large` → 3072 dimensões
- `text-embedding-ada-002` → 1536 dimensões

---

## 2. 🗄️ pgVector - Estrutura de Tabela

### Colunas Obrigatórias

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,           -- Identificador único
    content TEXT NOT NULL,            -- Texto original
    embedding vector(1536) NOT NULL  -- Vetor de embedding
);
```

### Estrutura Recomendada (Completa)

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,                              -- Metadados adicionais
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para performance
CREATE INDEX idx_embedding_ivfflat 
ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Dimensões do Vector
- Depende do modelo de embedding usado
- Todos os embeddings na mesma tabela devem ter a mesma dimensão
- Mais comum: **1536** (text-embedding-3-small)

### Operadores de Busca
- `<=>` : Distância cosseno (mais comum)
- `<->` : Distância euclidiana
- `<#>` : Distância produto interno negativo

---

## 3. 🔄 Sistema RAG - Como Funciona

### Pipeline Completo

```
1. INGESTÃO
   PDF → Carregar → Dividir em chunks → Criar embeddings → Armazenar no pgVector

2. BUSCA
   Pergunta → Criar embedding da pergunta → Buscar documentos similares → Retornar contexto

3. GERAÇÃO (Opcional)
   Contexto + Pergunta → LLM → Resposta final
```

### Componentes Necessários
1. **Carregamento de Documentos**: PDF, TXT, etc.
2. **Chunking**: Dividir texto em pedaços menores
3. **Embeddings**: Converter chunks em vetores
4. **Armazenamento**: PostgreSQL com pgVector
5. **Busca**: Similaridade vetorial
6. **LLM** (opcional): Gerar respostas baseadas no contexto

---

## 4. 🤖 LangChain vs Implementação Direta

### Com LangChain

**Vantagens:**
- ✅ Abstração de alto nível
- ✅ Menos código
- ✅ Integração fácil com múltiplos sistemas
- ✅ Métodos prontos (`add_documents`, `similarity_search`)

**Desvantagens:**
- ❌ Dependências pesadas (~10 pacotes)
- ❌ Menos controle sobre SQL
- ❌ Mais difícil de debugar

**Quando usar:**
- Prototipagem rápida
- Sistemas complexos com múltiplas integrações

### Sem LangChain (Direto)

**Vantagens:**
- ✅ Controle total sobre SQL
- ✅ Menos dependências (~4 pacotes)
- ✅ Mais leve e rápido
- ✅ Mais fácil de entender

**Desvantagens:**
- ❌ Mais código para escrever
- ❌ Precisa implementar funções manualmente

**Quando usar:**
- Servidores MCP (devem ser leves)
- Casos específicos e simples
- Quando precisa de performance máxima

### Dependências Comparadas

**Com LangChain:**
```
langchain, langchain-community, langchain-core,
langchain-openai, langchain-postgres, langchain-text-splitters,
psycopg, pgvector, openai, pypdf
```

**Sem LangChain:**
```
psycopg, pgvector, openai, pypdf
```

---

## 5. 🔌 Servidor MCP (Model Context Protocol)

### O que é MCP?
Protocolo que permite ao Cursor se conectar a ferramentas e fontes de dados externas.

### Arquitetura MCP

**NÃO precisa de agente IA no servidor!**
- O **Cursor JÁ É o agente IA**
- O servidor MCP apenas **expõe ferramentas (tools)**
- O Cursor decide quando e como usar cada ferramenta

### Componentes Necessários

1. **Servidor MCP** (`mcp_server.py`)
   - Implementa protocolo JSON-RPC 2.0 via stdio
   - Expõe ferramentas (tools)
   - Lê JSON do stdin, escreve JSON no stdout

2. **Arquivo de Configuração** (`mcp.json`)
   - Define comando para executar servidor
   - Variáveis de ambiente
   - Localização: `~/.cursor/mcp.json` ou `.cursor/mcp.json`

3. **Ferramentas (Tools)**
   - Funções que o Cursor pode chamar
   - Exemplos: `search_documents`, `ingest_document`, `ask_question`

### Protocolo MCP

**Handshake Inicial:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "rag-system", "version": "1.0.0"}
  }
}
```

**Listar Ferramentas:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "result": {
    "tools": [
      {
        "name": "search_documents",
        "description": "Busca documentos relevantes",
        "inputSchema": {...}
      }
    ]
  }
}
```

**Chamar Ferramenta:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_documents",
    "arguments": {"question": "Como funciona RAG?"}
  }
}
```

### Abordagem Recomendada para MCP

**Híbrida**: Expor ambas as opções
- `search_documents` - Retorna dados brutos do pgVector
- `ask_question` - Busca + LLM (resposta completa)
- `ingest_document` - Ingesta novos documentos

---

## 6. 📊 Estrutura de Projeto RAG

### Estrutura de Arquivos

```
projeto-rag/
├── src/
│   ├── ingest.py          # Pipeline de ingestão
│   ├── search.py           # Busca semântica
│   ├── chat.py             # Interface de chat (opcional)
│   └── mcp_server.py       # Servidor MCP (novo)
├── docker-compose.yml      # PostgreSQL com pgVector
├── requirements.txt        # Dependências Python
├── mcp.json               # Configuração MCP
└── .env                   # Variáveis de ambiente
```

### Fluxo de Dados

```
Documentos → ingest.py → Chunks → Embeddings → pgVector
                                              ↓
                                    search.py → Busca Semântica
                                              ↓
                                    chat.py → LLM → Resposta
                                              ↓
                                    mcp_server.py → Expõe para Cursor
```

---

## 7. 🔧 Implementação Prática

### Criar Embedding (Sem LangChain)

```python
from openai import OpenAI

client = OpenAI(api_key="sua-chave")
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Texto aqui"
).data[0].embedding
# Resultado: [0.234, 0.567, ..., 0.123]  (1536 números)
```

### Inserir no pgVector (Sem LangChain)

```python
import psycopg
from psycopg.types.json import Jsonb

conn = psycopg.connect("postgresql://...")

with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO document_embeddings (content, embedding, metadata)
        VALUES (%s, %s::vector, %s)
        """,
        (
            "Texto do documento",
            str(embedding),  # Lista como string
            Jsonb({"source": "documento.pdf"})
        )
    )
conn.commit()
```

### Buscar Similaridade (Sem LangChain)

```python
import psycopg

conn = psycopg.connect("postgresql://...")

# Criar embedding da query
query_embedding = create_embedding("Pergunta aqui")

with conn.cursor() as cur:
    cur.execute(
        """
        SELECT content, metadata,
               1 - (embedding <=> %s::vector) as similarity
        FROM document_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT 10
        """,
        (str(query_embedding), str(query_embedding))
    )
    results = cur.fetchall()
```

---

## 8. ✅ Checklist para Novo Projeto MCP

### Configuração Inicial
- [ ] PostgreSQL com pgVector rodando (Docker)
- [ ] Tabela criada com estrutura correta
- [ ] Variáveis de ambiente configuradas
- [ ] Dependências Python instaladas

### Implementação
- [ ] Servidor MCP implementado (`mcp_server.py`)
- [ ] Ferramentas expostas (tools)
- [ ] Integração com pgVector
- [ ] Tratamento de erros
- [ ] Logs para debug

### Configuração MCP
- [ ] Arquivo `mcp.json` criado
- [ ] Caminhos absolutos configurados
- [ ] Variáveis de ambiente no `mcp.json`
- [ ] Testado manualmente

### Testes
- [ ] Servidor inicia corretamente
- [ ] Cursor detecta servidor (`cursor-agent mcp list`)
- [ ] Ferramentas funcionam corretamente
- [ ] Busca retorna resultados relevantes

---

## 9. 📚 Conceitos-Chave

### Embeddings
- Representação numérica de texto
- Permite busca semântica
- Não precisa de agente IA para criar

### pgVector
- Extensão PostgreSQL para vetores
- Tipo `vector(dimensões)`
- Operadores: `<=>`, `<->`, `<#>`
- Índices: IVFFlat, HNSW

### RAG
- Retrieval-Augmented Generation
- Busca contexto relevante + Gera resposta
- Pipeline: Ingestão → Busca → Geração

### MCP
- Model Context Protocol
- Permite Cursor usar ferramentas externas
- Comunicação via JSON-RPC 2.0
- Servidor não precisa ser agente IA

### LangChain
- Framework para RAG
- Abstração de alto nível
- Não obrigatório, mas útil para prototipagem

---

## 10. 🎯 Decisões Arquiteturais

### Para Servidor MCP: Usar Direto (Sem LangChain)
**Motivos:**
- Mais leve
- Menos dependências
- Mais controle
- Melhor para produção

### Para Prototipagem: Usar LangChain
**Motivos:**
- Mais rápido
- Menos código
- Abstrações úteis

### Abordagem Híbrida para MCP
- Expor `search_documents` (dados brutos)
- Expor `ask_question` (resposta completa)
- Cursor escolhe a melhor ferramenta

---

## 11. 🚀 Próximo Projeto: Base de Conhecimento APIs Java

### Objetivo
Criar um servidor MCP que fornece uma base de conhecimento sobre projetos de API Java, permitindo ao Cursor buscar informações sobre:
- Padrões de projeto Java
- Estruturas de API REST
- Boas práticas
- Exemplos de código
- Documentação técnica

### Funcionalidades Principais

1. **Ingestão de Documentos**
   - Carregar documentação de APIs Java
   - Processar código-fonte Java
   - Ingerir exemplos e tutoriais

2. **Busca Semântica**
   - Buscar por conceitos (não apenas palavras-chave)
   - Encontrar padrões relacionados
   - Retornar contexto relevante

3. **Ferramentas MCP**
   - `search_java_api` - Buscar informações sobre APIs Java
   - `search_pattern` - Buscar padrões de projeto
   - `ask_java_question` - Pergunta completa sobre Java/APIs
   - `ingest_java_docs` - Ingerir nova documentação

### Estrutura do Projeto

```
java-api-knowledge-mcp/
├── src/
│   ├── mcp_server.py          # Servidor MCP principal
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── java_loader.py     # Carregar arquivos Java
│   │   ├── doc_loader.py      # Carregar documentação
│   │   └── chunker.py          # Dividir em chunks
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_service.py  # Criar embeddings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # Conexão PostgreSQL
│   │   ├── schema.py           # Criar tabelas
│   │   └── repository.py       # Operações CRUD
│   └── search/
│       ├── __init__.py
│       └── search_service.py  # Busca semântica
├── docker-compose.yml          # PostgreSQL com pgVector
├── requirements.txt           # Dependências Python
├── mcp.json                   # Configuração MCP
├── .env.example              # Exemplo de variáveis
└── README.md                 # Documentação
```

### Estrutura do Banco de Dados

**Tabela Principal:**
```sql
CREATE TABLE java_api_knowledge (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para performance
CREATE INDEX idx_java_knowledge_ivfflat 
ON java_api_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Estrutura de Metadata (JSONB):**
```json
{
  "source_type": "java_file|documentation|example|tutorial",
  "file_path": "/path/to/file.java",
  "class_name": "UserController",
  "method_name": "createUser",
  "package": "com.example.api.controllers",
  "tags": ["REST", "Controller", "Spring Boot"],
  "language": "java",
  "framework": "Spring Boot",
  "version": "1.0.0"
}
```

### Componentes de Implementação

#### 1. Serviço de Embeddings
- Classe `EmbeddingService` para criar embeddings
- Suporte a embedding único e batch
- Configurável via variáveis de ambiente

#### 2. Repositório de Dados
- Classe `KnowledgeRepository` para operações CRUD
- Métodos: `insert_document`, `search_similar`
- Integração com PostgreSQL/pgVector

#### 3. Carregador de Arquivos Java
- Classe `JavaFileLoader` para carregar arquivos `.java`
- Extração automática de metadados (package, classe, framework)
- Detecção de frameworks (Spring Boot, JPA, etc.)

#### 4. Chunker Inteligente
- Classe `JavaChunker` para dividir código Java
- Divisão por métodos (preferencial)
- Fallback para divisão por tamanho
- Configurável (chunk_size, overlap)

#### 5. Servidor MCP
- Classe `JavaAPIMCPServer` implementando protocolo JSON-RPC 2.0
- Ferramentas expostas: `search_java_api`, `ask_java_question`, `ingest_java_docs`
- Integração com serviços de embedding, busca e repositório

### Dependências do Projeto

```txt
psycopg==3.2.9
pgvector==0.3.6
openai==1.102.0
python-dotenv==1.1.1
```

**Nota**: Projeto usa implementação direta (sem LangChain) para ser mais leve e adequado para servidor MCP.

### Variáveis de Ambiente

```env
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/java_knowledge
OPENAI_API_KEY=sua_chave_api_openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MODEL=gpt-3.5-turbo
```

### Fontes de Conhecimento Sugeridas

- Spring Boot Documentation
- Java API Documentation
- REST API Best Practices
- Design Patterns em Java
- Exemplos de código de projetos open-source

### Metadados Sugeridos

- `source_type`: Tipo da fonte (java_file, documentation, example, tutorial)
- `framework`: Framework usado (Spring Boot, JAX-RS, etc.)
- `pattern`: Padrão de projeto (MVC, Repository, etc.)
- `tags`: Tags relevantes
- `version`: Versão da API/framework

---

## 📝 Próximos Passos

1. **Criar estrutura do projeto** (diretórios e arquivos base)
2. **Configurar PostgreSQL com pgVector** (docker-compose.yml)
3. **Implementar serviços base** (embeddings, repository, connection)
4. **Implementar carregadores** (Java loader, documentação loader)
5. **Implementar chunker inteligente** (divisão por métodos)
6. **Implementar servidor MCP** (protocolo JSON-RPC 2.0)
7. **Configurar mcp.json** (integração com Cursor)
8. **Testar integração** (verificar se Cursor detecta servidor)
9. **Ingerir base de conhecimento inicial** (documentação e exemplos)
10. **Validar busca semântica** (testar queries e resultados)

---

**Data de Criação**: 2025-01-27  
**Última Atualização**: 2025-01-27  
**Contexto**: Sistema RAG com pgVector e MCP  
**Próximo Projeto**: MCP com base de conhecimento de APIs Java
