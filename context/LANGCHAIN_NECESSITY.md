# 🤔 LangChain é Necessário para pgVector e Ingestão?

## ✅ Resposta Direta: **NÃO, LangChain NÃO é obrigatório**

Você pode usar **pgVector diretamente** com `psycopg` ou `psycopg2` sem precisar do LangChain.

---

## 📊 Comparação: Com vs Sem LangChain

### 🔵 Com LangChain (Atual)

**Vantagens:**
- ✅ Abstração de alto nível
- ✅ Integração fácil com embeddings (OpenAI)
- ✅ Métodos prontos (`add_documents`, `similarity_search`)
- ✅ Menos código para escrever
- ✅ Suporte a múltiplos tipos de documentos

**Desvantagens:**
- ❌ Dependência pesada (muitos pacotes)
- ❌ Menos controle sobre SQL
- ❌ Pode ser "overkill" para casos simples
- ❌ Mais difícil de debugar

**Código atual:**
```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = PGVector(
    embeddings=embeddings,
    collection_name="document_embeddings",
    connection="postgresql://...",
    use_jsonb=True,
)
store.add_documents(documents)
results = store.similarity_search_with_score(query, k=10)
```

---

### 🟢 Sem LangChain (Direto)

**Vantagens:**
- ✅ Controle total sobre SQL
- ✅ Menos dependências
- ✅ Mais leve e rápido
- ✅ Mais fácil de entender o que está acontecendo
- ✅ Melhor para casos específicos

**Desvantagens:**
- ❌ Mais código para escrever
- ❌ Precisa implementar funções de busca manualmente
- ❌ Precisa gerenciar conexões manualmente

**Código equivalente:**
```python
import psycopg
from openai import OpenAI
import numpy as np

# Conectar ao PostgreSQL
conn = psycopg.connect("postgresql://...")

# Criar embeddings diretamente
client = OpenAI()
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
).data[0].embedding

# Inserir no banco
with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO document_embeddings (content, embedding, metadata)
        VALUES (%s, %s, %s)
        """,
        (text, str(embedding), json.dumps(metadata))
    )

# Buscar similaridade
with conn.cursor() as cur:
    cur.execute(
        """
        SELECT content, metadata, 
               1 - (embedding <=> %s::vector) as similarity
        FROM document_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (str(query_embedding), str(query_embedding), k)
    )
    results = cur.fetchall()
```

---

## 🔍 O que o LangChain Faz por Você

### 1. **Gerenciamento de Embeddings**
- LangChain: `OpenAIEmbeddings` abstrai chamadas à API
- Sem LangChain: Usar `openai` diretamente

### 2. **Conexão com PostgreSQL**
- LangChain: `PGVector` gerencia conexões
- Sem LangChain: Usar `psycopg` diretamente

### 3. **Operações de Busca**
- LangChain: `similarity_search_with_score()` pronto
- Sem LangChain: Escrever SQL com operador `<=>` do pgvector

### 4. **Estrutura de Dados**
- LangChain: `Document` com `page_content` e `metadata`
- Sem LangChain: Usar dicionários ou classes próprias

---

## 📝 Exemplo Completo: Ingestão SEM LangChain

```python
import os
import json
import uuid
from datetime import datetime
import psycopg
from psycopg.types.json import Jsonb
from openai import OpenAI
import pypdf

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PGVECTOR_URL = os.getenv("PGVECTOR_URL")
EMBEDDING_MODEL = "text-embedding-3-small"

# Cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def create_embedding(text: str) -> list:
    """Cria embedding usando OpenAI diretamente"""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def load_pdf(pdf_path: str) -> list:
    """Carrega PDF sem LangChain"""
    reader = pypdf.PdfReader(pdf_path)
    pages = []
    for page_num, page in enumerate(reader.pages):
        pages.append({
            "content": page.extract_text(),
            "page": page_num + 1,
            "source": pdf_path
        })
    return pages

def split_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list:
    """Divide texto em chunks sem LangChain"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def ingest_pdf_direct(pdf_path: str):
    """Ingestão completa sem LangChain"""
    # 1. Carregar PDF
    pages = load_pdf(pdf_path)
    
    # 2. Dividir em chunks
    all_chunks = []
    for page in pages:
        chunks = split_text(page["content"])
        for chunk in chunks:
            all_chunks.append({
                "content": chunk,
                "metadata": {
                    "page": page["page"],
                    "source": page["source"],
                    "chunk_id": str(uuid.uuid4()),
                    "processed_at": datetime.now().isoformat()
                }
            })
    
    # 3. Conectar ao PostgreSQL
    conn = psycopg.connect(PGVECTOR_URL)
    
    # 4. Criar tabela se não existir
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS embedding_idx 
            ON document_embeddings 
            USING ivfflat (embedding vector_cosine_ops);
        """)
        conn.commit()
    
    # 5. Processar e inserir cada chunk
    with conn.cursor() as cur:
        for chunk in all_chunks:
            # Criar embedding
            embedding = create_embedding(chunk["content"])
            
            # Inserir no banco
            cur.execute(
                """
                INSERT INTO document_embeddings (content, embedding, metadata)
                VALUES (%s, %s::vector, %s)
                """,
                (
                    chunk["content"],
                    str(embedding),
                    Jsonb(chunk["metadata"])
                )
            )
        
        conn.commit()
    
    conn.close()
    print(f"✅ {len(all_chunks)} documentos ingeridos com sucesso!")
```

---

## 📝 Exemplo Completo: Busca SEM LangChain

```python
import psycopg
from openai import OpenAI
from psycopg.types.json import Jsonb

def search_documents_direct(query: str, k: int = 10):
    """Busca semântica sem LangChain"""
    # 1. Criar embedding da query
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    query_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    
    # 2. Conectar ao PostgreSQL
    conn = psycopg.connect(PGVECTOR_URL)
    
    # 3. Buscar documentos similares
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                content,
                metadata,
                1 - (embedding <=> %s::vector) as similarity_score
            FROM document_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (str(query_embedding), str(query_embedding), k)
        )
        
        results = []
        for row in cur.fetchall():
            results.append({
                "content": row[0],
                "metadata": row[1],
                "score": row[2]
            })
    
    conn.close()
    return results
```

---

## 🎯 Quando Usar Cada Abordagem

### Use LangChain quando:
- ✅ Você quer abstração de alto nível
- ✅ Você precisa de integração com múltiplos sistemas
- ✅ Você está construindo um sistema RAG complexo
- ✅ Você quer menos código e mais produtividade
- ✅ Você não se importa com dependências pesadas

### Use Direto (sem LangChain) quando:
- ✅ Você quer controle total sobre SQL
- ✅ Você precisa de performance máxima
- ✅ Você quer menos dependências
- ✅ Você está fazendo algo específico e simples
- ✅ Você quer entender exatamente o que está acontecendo
- ✅ Você está criando um servidor MCP (pode ser mais leve)

---

## 📦 Dependências Comparadas

### Com LangChain:
```txt
langchain==0.3.27
langchain-community==0.3.27
langchain-core==0.3.74
langchain-openai==0.3.30
langchain-postgres==0.0.15
langchain-text-splitters==0.3.9
psycopg==3.2.9
pgvector==0.3.6
openai==1.102.0
pypdf==6.0.0
```

### Sem LangChain:
```txt
psycopg==3.2.9
pgvector==0.3.6
openai==1.102.0
pypdf==6.0.0
```

**Redução**: De ~10 pacotes para ~4 pacotes principais!

---

## 🔧 Para Servidor MCP

### Recomendação para MCP:

**Use abordagem DIRETA (sem LangChain)** porque:

1. ✅ **Mais leve**: Menos dependências = servidor mais rápido
2. ✅ **Mais controle**: Você controla exatamente o que acontece
3. ✅ **Mais simples**: Menos abstrações = mais fácil de debugar
4. ✅ **Melhor para MCP**: Servidores MCP devem ser leves e focados

### Estrutura Sugerida:

```python
# src/mcp_server.py (sem LangChain)
import psycopg
from openai import OpenAI

# Funções diretas
def create_embedding(text: str) -> list:
    # OpenAI direto
    pass

def insert_document(content: str, embedding: list, metadata: dict):
    # SQL direto com psycopg
    pass

def search_similar(query_embedding: list, k: int = 10):
    # SQL direto com operador <=>
    pass
```

---

## ✅ Conclusão

**LangChain NÃO é necessário**, mas pode ser útil:

- **Para prototipagem rápida**: Use LangChain
- **Para produção/MCP**: Considere usar direto (mais controle, menos dependências)
- **Para sistemas complexos**: LangChain pode ajudar
- **Para casos simples**: Direto é melhor

**Para seu servidor MCP**: Recomendo usar **direto (sem LangChain)** para ter mais controle e menos dependências.
