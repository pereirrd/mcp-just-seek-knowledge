# 🚀 Guia: Novo Projeto MCP - Base de Conhecimento APIs Java

## 🎯 Objetivo

Criar um servidor MCP que fornece uma base de conhecimento sobre projetos de API Java, permitindo ao Cursor buscar informações sobre:
- Padrões de projeto Java
- Estruturas de API REST
- Boas práticas
- Exemplos de código
- Documentação técnica

---

## 📋 Requisitos do Projeto

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

---

## 🏗️ Estrutura do Projeto

### Diretórios

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

---

## 🗄️ Estrutura do Banco de Dados

### Tabela Principal

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

### Estrutura de Metadata (JSONB)

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

---

## 🔧 Implementação - Sem LangChain

### 1. Serviço de Embeddings

```python
# src/embeddings/embedding_service.py
from openai import OpenAI
import os

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    def create_embedding(self, text: str) -> list:
        """Cria embedding para um texto"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def create_embeddings_batch(self, texts: list[str]) -> list[list]:
        """Cria embeddings para múltiplos textos"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
```

### 2. Repositório de Dados

```python
# src/database/repository.py
import psycopg
from psycopg.types.json import Jsonb
from typing import List, Dict, Any

class KnowledgeRepository:
    def __init__(self, connection_string: str):
        self.conn = psycopg.connect(connection_string)
    
    def insert_document(self, content: str, embedding: list, metadata: dict):
        """Insere documento na base de conhecimento"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO java_api_knowledge (content, embedding, metadata)
                VALUES (%s, %s::vector, %s)
                """,
                (content, str(embedding), Jsonb(metadata))
            )
        self.conn.commit()
    
    def search_similar(self, query_embedding: list, k: int = 10) -> List[Dict[str, Any]]:
        """Busca documentos similares"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM java_api_knowledge
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (str(query_embedding), str(query_embedding), k)
            )
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2],
                    "score": row[3]
                })
            return results
```

### 3. Carregador de Arquivos Java

```python
# src/ingest/java_loader.py
import os
from pathlib import Path
from typing import List, Dict

class JavaFileLoader:
    def __init__(self):
        self.supported_extensions = {'.java'}
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """Carrega um arquivo Java"""
        path = Path(file_path)
        
        if path.suffix not in self.supported_extensions:
            raise ValueError(f"Formato não suportado: {path.suffix}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair metadados do arquivo
        metadata = self._extract_metadata(content, file_path)
        
        return {
            "content": content,
            "metadata": metadata
        }
    
    def load_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Carrega todos os arquivos Java de um diretório"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.java'):
                    file_path = os.path.join(root, filename)
                    try:
                        files.append(self.load_file(file_path))
                    except Exception as e:
                        print(f"Erro ao carregar {file_path}: {e}")
        return files
    
    def _extract_metadata(self, content: str, file_path: str) -> dict:
        """Extrai metadados do código Java"""
        import re
        
        metadata = {
            "source_type": "java_file",
            "file_path": file_path,
            "language": "java"
        }
        
        # Extrair package
        package_match = re.search(r'package\s+([\w.]+);', content)
        if package_match:
            metadata["package"] = package_match.group(1)
        
        # Extrair classe
        class_match = re.search(r'public\s+class\s+(\w+)', content)
        if class_match:
            metadata["class_name"] = class_match.group(1)
        
        # Detectar framework
        if '@RestController' in content or '@Controller' in content:
            metadata["framework"] = "Spring Boot"
            metadata["tags"] = ["REST", "Controller"]
        elif '@Entity' in content:
            metadata["framework"] = "JPA"
            metadata["tags"] = ["Entity", "Database"]
        
        return metadata
```

### 4. Chunker Inteligente

```python
# src/ingest/chunker.py
from typing import List, Dict
import re

class JavaChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_java_file(self, content: str, metadata: dict) -> List[Dict[str, Any]]:
        """Divide arquivo Java em chunks inteligentes"""
        chunks = []
        
        # Tentar dividir por métodos primeiro
        methods = self._extract_methods(content)
        
        if methods:
            for method in methods:
                chunks.append({
                    "content": method["content"],
                    "metadata": {
                        **metadata,
                        "method_name": method["name"],
                        "chunk_type": "method"
                    }
                })
        else:
            # Fallback: dividir por tamanho
            chunks = self._chunk_by_size(content, metadata)
        
        return chunks
    
    def _extract_methods(self, content: str) -> List[Dict[str, str]]:
        """Extrai métodos do código Java"""
        methods = []
        pattern = r'(public|private|protected)\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\}'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            method_content = match.group(0)
            method_name_match = re.search(r'(\w+)\s*\(', method_content)
            if method_name_match:
                methods.append({
                    "name": method_name_match.group(1),
                    "content": method_content
                })
        
        return methods
    
    def _chunk_by_size(self, content: str, metadata: dict) -> List[Dict[str, Any]]:
        """Divide texto por tamanho"""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end]
            
            chunks.append({
                "content": chunk,
                "metadata": {
                    **metadata,
                    "chunk_type": "text"
                }
            })
            
            start = end - self.overlap
        
        return chunks
```

### 5. Servidor MCP

```python
# src/mcp_server.py
import sys
import json
import asyncio
from typing import Any, Dict

from embeddings.embedding_service import EmbeddingService
from database.repository import KnowledgeRepository
from search.search_service import SearchService

class JavaAPIMCPServer:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.repository = KnowledgeRepository(os.getenv("PGVECTOR_URL"))
        self.search_service = SearchService(self.repository, self.embedding_service)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições MCP"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id)
        elif method == "tools/call":
            return await self.handle_tool_call(request_id, params)
        else:
            return self.error_response(request_id, -32601, "Method not found")
    
    def handle_initialize(self, request_id: int) -> Dict[str, Any]:
        """Handshake inicial"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "java-api-knowledge",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_list_tools(self, request_id: int) -> Dict[str, Any]:
        """Lista ferramentas disponíveis"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "search_java_api",
                        "description": "Busca informações sobre APIs Java",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Pergunta ou termo de busca sobre APIs Java"
                                },
                                "k": {
                                    "type": "integer",
                                    "description": "Número de resultados",
                                    "default": 10
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "ask_java_question",
                        "description": "Faz uma pergunta completa sobre Java/APIs usando RAG",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "Pergunta sobre Java ou APIs"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "ingest_java_docs",
                        "description": "Ingere documentação ou código Java na base de conhecimento",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "Caminho para arquivo Java ou documentação"
                                }
                            },
                            "required": ["file_path"]
                        }
                    }
                ]
            }
        }
    
    async def handle_tool_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Processa chamada de ferramenta"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "search_java_api":
                result = await self.search_java_api(arguments)
            elif tool_name == "ask_java_question":
                result = await self.ask_java_question(arguments)
            elif tool_name == "ingest_java_docs":
                result = await self.ingest_java_docs(arguments)
            else:
                return self.error_response(request_id, -32601, f"Tool '{tool_name}' not found")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        except Exception as e:
            return self.error_response(request_id, -32000, str(e))
    
    async def search_java_api(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Busca informações sobre APIs Java"""
        query = arguments.get("query")
        k = arguments.get("k", 10)
        
        results = await self.search_service.search(query, k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def ask_java_question(self, arguments: Dict[str, Any]) -> str:
        """Pergunta completa usando RAG"""
        question = arguments.get("question")
        
        # Buscar contexto
        results = await self.search_service.search(question, k=5)
        
        # Formatar contexto
        context = "\n\n".join([
            f"**{r['metadata'].get('class_name', 'Documento')}**\n{r['content']}"
            for r in results
        ])
        
        # Gerar resposta com LLM
        from openai import OpenAI
        llm = OpenAI()
        
        response = llm.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em APIs Java. Responda baseado apenas no contexto fornecido."
                },
                {
                    "role": "user",
                    "content": f"Contexto:\n{context}\n\nPergunta: {question}"
                }
            ]
        )
        
        return response.choices[0].message.content
    
    async def ingest_java_docs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ingere documentação Java"""
        file_path = arguments.get("file_path")
        
        # Carregar arquivo
        from ingest.java_loader import JavaFileLoader
        loader = JavaFileLoader()
        file_data = loader.load_file(file_path)
        
        # Dividir em chunks
        from ingest.chunker import JavaChunker
        chunker = JavaChunker()
        chunks = chunker.chunk_java_file(file_data["content"], file_data["metadata"])
        
        # Criar embeddings e inserir
        ingested_count = 0
        for chunk in chunks:
            embedding = self.embedding_service.create_embedding(chunk["content"])
            self.repository.insert_document(
                chunk["content"],
                embedding,
                chunk["metadata"]
            )
            ingested_count += 1
        
        return {
            "status": "success",
            "file": file_path,
            "chunks_ingested": ingested_count
        }
    
    def error_response(self, request_id: int, code: int, message: str) -> Dict[str, Any]:
        """Gera resposta de erro"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    async def run(self):
        """Loop principal do servidor"""
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = self.error_response(
                    None, -32700, f"Parse error: {str(e)}"
                )
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    server = JavaAPIMCPServer()
    asyncio.run(server.run())
```

---

## 📝 Configuração

### requirements.txt

```txt
psycopg==3.2.9
pgvector==0.3.6
openai==1.102.0
python-dotenv==1.1.1
```

### docker-compose.yml

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: postgres_java_knowledge
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: java_knowledge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d java_knowledge"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  bootstrap_vector_ext:
    image: pgvector/pgvector:pg17
    depends_on:
      postgres:
        condition: service_healthy
    entrypoint: ["/bin/sh", "-c"]
    command: >
      PGPASSWORD=postgres
      psql "postgresql://postgres@postgres:5432/java_knowledge" -v ON_ERROR_STOP=1
      -c "CREATE EXTENSION IF NOT EXISTS vector;"
    restart: "no"

volumes:
  postgres_data:
```

### mcp.json

```json
{
  "mcpServers": {
    "java-api-knowledge": {
      "command": "python",
      "args": [
        "/caminho/absoluto/para/projeto/src/mcp_server.py"
      ],
      "env": {
        "PGVECTOR_URL": "postgresql://postgres:postgres@localhost:5432/java_knowledge",
        "OPENAI_API_KEY": "sua_chave_aqui",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_MODEL": "gpt-3.5-turbo"
      }
    }
  }
}
```

### .env.example

```env
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/java_knowledge
OPENAI_API_KEY=sua_chave_api_openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MODEL=gpt-3.5-turbo
```

---

## 🚀 Próximos Passos

1. **Criar estrutura do projeto**
2. **Configurar PostgreSQL com pgVector**
3. **Implementar serviços base** (embeddings, repository)
4. **Implementar carregadores** (Java, documentação)
5. **Implementar servidor MCP**
6. **Testar integração com Cursor**
7. **Ingerir base de conhecimento inicial**

---

## 📚 Fontes de Conhecimento

### Documentação para Ingerir
- Spring Boot Documentation
- Java API Documentation
- REST API Best Practices
- Design Patterns em Java
- Exemplos de código de projetos open-source

### Estrutura de Metadados Sugerida
- `source_type`: Tipo da fonte
- `framework`: Framework usado (Spring Boot, JAX-RS, etc.)
- `pattern`: Padrão de projeto (MVC, Repository, etc.)
- `tags`: Tags relevantes
- `version`: Versão da API/framework

---

**Este guia fornece uma base sólida para criar o servidor MCP de conhecimento sobre APIs Java!**
