# 📊 Estrutura da Tabela pgVector

## 🎯 Colunas Necessárias

### Estrutura Mínima (Básica)

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536)
);
```

### Estrutura Recomendada (Completa)

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📋 Descrição das Colunas

### 1. **`id`** (Obrigatório)
```sql
id SERIAL PRIMARY KEY
```
- **Tipo**: `SERIAL` (auto-incremento)
- **Função**: Identificador único de cada registro
- **Obrigatório**: ✅ Sim (chave primária)

### 2. **`content`** (Obrigatório)
```sql
content TEXT NOT NULL
```
- **Tipo**: `TEXT`
- **Função**: Armazena o texto original do documento/chunk
- **Obrigatório**: ✅ Sim
- **Por quê**: Você precisa do texto original para retornar ao usuário

### 3. **`embedding`** (Obrigatório - Principal!)
```sql
embedding vector(1536)
```
- **Tipo**: `vector(dimensões)`
- **Função**: Armazena o vetor de embedding
- **Obrigatório**: ✅ Sim (é o propósito do pgvector!)
- **Dimensões**: 
  - `text-embedding-3-small` → **1536**
  - `text-embedding-ada-002` → **1536**
  - `text-embedding-3-large` → **3072**
  - Ajuste conforme o modelo usado

### 4. **`metadata`** (Opcional mas Recomendado)
```sql
metadata JSONB
```
- **Tipo**: `JSONB` (JSON binário)
- **Função**: Armazena metadados adicionais
- **Obrigatório**: ❌ Não, mas muito útil
- **Exemplos de uso**:
  - Origem do documento (PDF path)
  - Número da página
  - Data de processamento
  - Tags/categorias
  - Qualquer informação adicional

### 5. **`created_at`** (Opcional)
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```
- **Tipo**: `TIMESTAMP`
- **Função**: Data/hora de criação do registro
- **Obrigatório**: ❌ Não, mas útil para auditoria

---

## 🔧 Criação Completa da Tabela

### Passo 1: Habilitar Extensão pgvector

```sql
-- Conectar ao banco de dados
-- Executar antes de criar a tabela

CREATE EXTENSION IF NOT EXISTS vector;
```

### Passo 2: Criar a Tabela

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Passo 3: Criar Índices para Performance

```sql
-- Índice IVFFlat (recomendado para até ~1M registros)
CREATE INDEX idx_embedding_ivfflat 
ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- OU Índice HNSW (recomendado para >1M registros)
CREATE INDEX idx_embedding_hnsw 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);
```

**Importante**: Execute `ANALYZE document_embeddings;` antes de criar índice IVFFlat.

---

## 📐 Dimensões do Vector

### Como Determinar a Dimensão?

A dimensão depende do **modelo de embedding** usado:

| Modelo OpenAI | Dimensões |
|---------------|-----------|
| `text-embedding-3-small` | **1536** |
| `text-embedding-3-large` | **3072** |
| `text-embedding-ada-002` | **1536** |

### Verificar Dimensão do Embedding

```python
from openai import OpenAI

client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="teste"
)

print(len(response.data[0].embedding))  # 1536
```

### Criar Tabela com Dimensão Dinâmica

```sql
-- Para text-embedding-3-small (1536)
CREATE TABLE document_embeddings (
    embedding vector(1536)
);

-- Para text-embedding-3-large (3072)
CREATE TABLE document_embeddings (
    embedding vector(3072)
);
```

**⚠️ Atenção**: Todos os embeddings na mesma tabela devem ter a mesma dimensão!

---

## 💾 Inserção de Dados

### Método 1: SQL Direto

```sql
INSERT INTO document_embeddings (content, embedding, metadata)
VALUES (
    'Texto do documento aqui',
    '[0.234, 0.567, 0.891, ..., 0.123]'::vector,
    '{"source": "documento.pdf", "page": 1}'::jsonb
);
```

### Método 2: Python com psycopg

```python
import psycopg
from psycopg.types.json import Jsonb

conn = psycopg.connect("postgresql://...")

embedding = [0.234, 0.567, 0.891, ..., 0.123]  # 1536 números

with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO document_embeddings (content, embedding, metadata)
        VALUES (%s, %s::vector, %s)
        """,
        (
            "Texto do documento",
            str(embedding),  # Converter lista para string
            Jsonb({"source": "documento.pdf", "page": 1})
        )
    )
conn.commit()
```

### Método 3: Python com NumPy (Mais Eficiente)

```python
import psycopg
import numpy as np
from psycopg.types.json import Jsonb

conn = psycopg.connect("postgresql://...")

# Embedding como array NumPy
embedding = np.array([0.234, 0.567, 0.891, ..., 0.123])

with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO document_embeddings (content, embedding, metadata)
        VALUES (%s, %s::vector, %s)
        """,
        (
            "Texto do documento",
            embedding.tolist(),  # Converter para lista
            Jsonb({"source": "documento.pdf"})
        )
    )
conn.commit()
```

---

## 🔍 Busca por Similaridade

### SQL Direto

```sql
-- Buscar documentos similares
SELECT 
    content,
    metadata,
    1 - (embedding <=> '[0.234, 0.567, ...]'::vector) as similarity
FROM document_embeddings
ORDER BY embedding <=> '[0.234, 0.567, ...]'::vector
LIMIT 10;
```

### Operadores pgvector

- `<=>` : Distância cosseno (1 - cosine similarity)
- `<->` : Distância euclidiana
- `<#>` : Distância produto interno negativo

**Mais comum**: `<=>` (distância cosseno)

---

## 🎯 Estrutura Completa com Índices

### Script SQL Completo

```sql
-- 1. Habilitar extensão
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar tabela
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Coletar estatísticas (necessário para IVFFlat)
ANALYZE document_embeddings;

-- 4. Criar índice IVFFlat
CREATE INDEX IF NOT EXISTS idx_embedding_ivfflat 
ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- OU criar índice HNSW (melhor para grandes volumes)
-- CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
-- ON document_embeddings 
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 200);
```

---

## 📊 Comparação: Com vs Sem LangChain

### Com LangChain (Atual)

```python
from langchain_postgres import PGVector

# LangChain cria a tabela automaticamente!
store = PGVector(
    embeddings=embeddings,
    collection_name="document_embeddings",
    connection=PGVECTOR_URL,
    use_jsonb=True,
)

# Estrutura criada automaticamente:
# - uuid (id)
# - content (texto)
# - embedding (vector)
# - metadata (jsonb)
# - cmetadata (jsonb adicional)
```

**Vantagem**: Criação automática  
**Desvantagem**: Menos controle sobre estrutura

### Sem LangChain (Direto)

```sql
-- Você controla tudo!
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Vantagem**: Controle total  
**Desvantagem**: Precisa criar manualmente

---

## 🔧 Função Python para Criar Tabela

### Versão Completa

```python
import psycopg

def create_embeddings_table(
    connection_string: str,
    table_name: str = "document_embeddings",
    vector_dimensions: int = 1536
):
    """
    Cria tabela para armazenar embeddings no pgvector
    
    Args:
        connection_string: String de conexão PostgreSQL
        table_name: Nome da tabela
        vector_dimensions: Dimensões do vetor (1536 para text-embedding-3-small)
    """
    conn = psycopg.connect(connection_string)
    
    with conn.cursor() as cur:
        # 1. Habilitar extensão
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Criar tabela
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({vector_dimensions}) NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. Coletar estatísticas
        cur.execute(f"ANALYZE {table_name};")
        
        # 4. Criar índice IVFFlat
        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_ivfflat 
            ON {table_name} 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        conn.commit()
    
    conn.close()
    print(f"✅ Tabela {table_name} criada com sucesso!")

# Uso
create_embeddings_table(
    connection_string="postgresql://postgres:postgres@localhost:5432/rag",
    table_name="document_embeddings",
    vector_dimensions=1536
)
```

---

## 📋 Checklist de Colunas

### Obrigatórias ✅
- [ ] `id` - Identificador único
- [ ] `content` - Texto original
- [ ] `embedding` - Vetor de embedding

### Recomendadas ⭐
- [ ] `metadata` - Metadados em JSONB
- [ ] `created_at` - Timestamp de criação

### Opcionais (Dependem do caso)
- [ ] `source` - Origem do documento (se não usar metadata)
- [ ] `page` - Número da página (se não usar metadata)
- [ ] `chunk_id` - ID do chunk (se não usar metadata)
- [ ] `updated_at` - Timestamp de atualização

---

## 🎯 Estrutura Recomendada para Seu Projeto

### Opção 1: Simples (Mínima)

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);
```

### Opção 2: Completa (Recomendada)

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para performance
CREATE INDEX idx_embedding_ivfflat 
ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Opção 3: Com Colunas Adicionais

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    source TEXT,
    page INTEGER,
    chunk_id UUID,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ✅ Resumo

### Colunas Mínimas Necessárias:
1. **`id`** - Identificador único
2. **`content`** - Texto original
3. **`embedding vector(dimensões)`** - Vetor de embedding

### Dimensões Comuns:
- **1536** - `text-embedding-3-small` (mais comum)
- **3072** - `text-embedding-3-large`

### Índices Recomendados:
- **IVFFlat** - Para até ~1M registros
- **HNSW** - Para >1M registros

### Estrutura no Seu Projeto:
```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
