# 🔢 O que são Embeddings?

## 📖 Definição Simples

**Embedding** = Representação numérica de texto (ou outros dados) em forma de **vetor** (lista de números).

É como "traduzir" palavras/frases para números que capturam o **significado semântico**.

---

## 🎯 Analogia Simples

Imagine que você quer representar palavras em um mapa:

```
"gato"  → [0.2, 0.8, 0.1, ...]  (1536 números)
"cachorro" → [0.3, 0.7, 0.2, ...]  (1536 números)
"carro" → [0.9, 0.1, 0.8, ...]  (1536 números)
```

**Palavras similares** ficam **próximas** no espaço numérico:
- "gato" e "cachorro" (animais) → vetores próximos
- "carro" (veículo) → vetor distante dos animais

---

## 🔍 Como Funciona na Prática

### Exemplo Visual:

```
Texto: "O gato está dormindo"
         ↓
    [Modelo de Embedding]
         ↓
Vetor: [0.2, 0.8, 0.1, 0.5, ..., 0.3]  (1536 números)
         ↓
    Armazenado no pgVector
```

### Comparação de Similaridade:

```
"gato" → [0.2, 0.8, 0.1, ...]
"cachorro" → [0.3, 0.7, 0.2, ...]
"carro" → [0.9, 0.1, 0.8, ...]

Distância entre "gato" e "cachorro": 0.15 (próximos!)
Distância entre "gato" e "carro": 0.85 (distantes!)
```

---

## ❓ Precisa de um Agente IA para Criar Embeddings?

### ✅ Resposta: **NÃO!**

Você precisa de um **Modelo de Embedding**, não de um **Agente IA**.

### Diferença Importante:

#### 🤖 **Agente IA** (NÃO necessário para embeddings)
- Sistema que **toma decisões**
- Processa informações e **responde**
- Exemplo: ChatGPT, Claude, Gemini
- **Não é necessário** para criar embeddings

#### 🔢 **Modelo de Embedding** (SIM necessário)
- Modelo pré-treinado que **converte texto em números**
- Função matemática: `texto → vetor`
- Exemplos: `text-embedding-3-small`, `text-embedding-ada-002`
- **É necessário** para criar embeddings

---

## 🛠️ Como Criar Embeddings (Sem Agente IA)

### Opção 1: Usar API da OpenAI (Mais Comum)

```python
from openai import OpenAI

client = OpenAI(api_key="sua-chave")

# Criar embedding - SIMPLES!
texto = "O gato está dormindo"
embedding = client.embeddings.create(
    model="text-embedding-3-small",  # Modelo de embedding
    input=texto
).data[0].embedding

# Resultado: lista de 1536 números
print(embedding)  # [0.2, 0.8, 0.1, 0.5, ...]
```

**Não precisa de agente!** Apenas chama a API.

### Opção 2: Usar Modelo Local

```python
from sentence_transformers import SentenceTransformer

# Carregar modelo local
model = SentenceTransformer('all-MiniLM-L6-v2')

# Criar embedding
texto = "O gato está dormindo"
embedding = model.encode(texto)

# Resultado: lista de números
print(embedding)  # [0.2, 0.8, 0.1, ...]
```

**Não precisa de agente!** Apenas usa o modelo.

### Opção 3: Usar LangChain (Abstração)

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embedding = embeddings.embed_query("O gato está dormindo")
```

**Ainda não precisa de agente!** LangChain só facilita o uso.

---

## 🔄 Fluxo Completo no Seu Projeto

### 1. **Texto Original**
```
"O sistema RAG permite buscar informações em documentos"
```

### 2. **Criar Embedding** (sem agente!)
```python
from openai import OpenAI

client = OpenAI()
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="O sistema RAG permite buscar informações em documentos"
).data[0].embedding
```

### 3. **Resultado: Vetor**
```python
[0.234, 0.567, 0.891, ..., 0.123]  # 1536 números
```

### 4. **Armazenar no pgVector**
```sql
INSERT INTO document_embeddings (content, embedding)
VALUES (
    'O sistema RAG permite buscar informações em documentos',
    '[0.234, 0.567, 0.891, ...]'::vector
);
```

### 5. **Buscar Similaridade**
```sql
-- Pergunta: "Como funciona busca em documentos?"
-- 1. Criar embedding da pergunta (mesmo processo)
-- 2. Buscar no banco

SELECT content, 
       1 - (embedding <=> '[0.245, 0.578, 0.892, ...]'::vector) as similarity
FROM document_embeddings
ORDER BY embedding <=> '[0.245, 0.578, 0.892, ...]'::vector
LIMIT 10;
```

---

## 📊 Comparação: Agente vs Modelo de Embedding

### 🤖 Agente IA (ChatGPT, Claude)
```
Entrada: "Explique o que é RAG"
         ↓
    [Processa, pensa, decide]
         ↓
Saída: "RAG é um sistema que..."
```

**Características:**
- Toma decisões
- Gera texto novo
- Entende contexto complexo
- **NÃO é necessário para embeddings**

### 🔢 Modelo de Embedding (text-embedding-3-small)
```
Entrada: "Explique o que é RAG"
         ↓
    [Converte para números]
         ↓
Saída: [0.2, 0.8, 0.1, ...]  (vetor)
```

**Características:**
- Função matemática simples
- Converte texto → números
- Não toma decisões
- Não gera texto
- **É necessário para embeddings**

---

## 🎯 No Seu Projeto RAG

### O que você usa:

1. **Modelo de Embedding** ✅
   - `text-embedding-3-small` (OpenAI)
   - Converte texto em vetores
   - **Não é um agente!**

2. **LLM (Agente IA)** ✅ (opcional, para respostas)
   - `gpt-3.5-turbo` (OpenAI)
   - Gera respostas baseadas no contexto
   - **Este sim é um agente**, mas só usado em `chat.py`

### Fluxo no seu código:

```python
# ingest.py - Cria embeddings (SEM agente)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# ↑ Isso é um MODELO, não um agente!

# search.py - Busca usando embeddings (SEM agente)
store.similarity_search_with_score(question, k=10)
# ↑ Usa os vetores para buscar, sem agente

# chat.py - Gera resposta (COM agente LLM)
llm = ChatOpenAI(model="gpt-3.5-turbo")
# ↑ Este sim é um agente, mas só para gerar respostas
```

---

## 💡 Resumo Visual

```
┌─────────────────────────────────────────┐
│  TEXTO: "O gato está dormindo"          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  MODELO DE EMBEDDING                    │
│  (text-embedding-3-small)               │
│  Função: texto → números                │
│  NÃO é um agente!                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  VETOR: [0.2, 0.8, 0.1, ..., 0.3]      │
│  (1536 números)                         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  ARMAZENAR NO pgVector                  │
│  (PostgreSQL com extensão pgvector)     │
└─────────────────────────────────────────┘
```

---

## ✅ Conclusão

### Para criar embeddings você precisa:
- ✅ **Modelo de Embedding** (ex: `text-embedding-3-small`)
- ✅ **API ou biblioteca** para chamar o modelo
- ❌ **NÃO precisa de Agente IA**

### Agente IA é usado apenas para:
- Gerar respostas finais (`chat.py`)
- Processar e interpretar informações
- **NÃO é necessário para criar embeddings**

### No seu projeto:
- **Embeddings**: Criados por modelo (sem agente)
- **Busca**: Usa vetores diretamente (sem agente)
- **Respostas**: Usa LLM/agente (opcional, só em `chat.py`)

---

## 🔧 Exemplo Prático Completo

```python
# 1. Criar embedding (SEM agente)
from openai import OpenAI

client = OpenAI(api_key="sua-chave")

texto = "O sistema RAG permite buscar informações"
embedding = client.embeddings.create(
    model="text-embedding-3-small",  # Modelo, não agente!
    input=texto
).data[0].embedding

# embedding = [0.234, 0.567, ..., 0.123]  (1536 números)

# 2. Armazenar no banco
import psycopg

conn = psycopg.connect("postgresql://...")
with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO document_embeddings (content, embedding) VALUES (%s, %s::vector)",
        (texto, str(embedding))
    )
conn.commit()

# 3. Buscar similaridade (SEM agente)
query = "Como buscar dados?"
query_embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

with conn.cursor() as cur:
    cur.execute(
        """
        SELECT content, 
               1 - (embedding <=> %s::vector) as similarity
        FROM document_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT 10
        """,
        (str(query_embedding), str(query_embedding))
    )
    results = cur.fetchall()

# 4. (Opcional) Gerar resposta com LLM/agente
from openai import OpenAI

llm_client = OpenAI()
response = llm_client.chat.completions.create(
    model="gpt-3.5-turbo",  # Este sim é um agente!
    messages=[
        {"role": "system", "content": "Baseado no contexto..."},
        {"role": "user", "content": query}
    ]
)
```

---

## 📚 Resumo Final

| Conceito | O que é | Precisa para Embeddings? |
|----------|---------|-------------------------|
| **Embedding** | Vetor numérico que representa texto | ✅ É o resultado |
| **Modelo de Embedding** | Função que converte texto → vetor | ✅ Sim, necessário |
| **Agente IA** | Sistema que toma decisões e responde | ❌ Não necessário |
| **LLM** | Modelo de linguagem (tipo de agente) | ❌ Não necessário (só para respostas) |

**Para criar embeddings**: Use um **modelo de embedding**, não um agente!
