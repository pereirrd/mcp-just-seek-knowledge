# 🏗️ Decisão de Arquitetura: Servidor MCP para Cursor

## ❓ Pergunta: Preciso de um agente IA ou só expor dados do pgVector?

## ✅ Resposta: **NÃO precisa de agente IA no servidor**

O **Cursor JÁ É o agente IA**. O servidor MCP deve apenas **expor ferramentas (tools)** que o Cursor pode usar quando necessário.

---

## 🎯 Duas Abordagens Possíveis

### Abordagem 1: Apenas Dados do pgVector (Simples)

**Ferramentas expostas:**
- `search_documents` - Retorna documentos relevantes do pgVector
- `ingest_document` - Ingesta novos documentos

**Como funciona:**
```
Cursor → search_documents("pergunta") → Retorna documentos brutos → Cursor processa e responde
```

**Vantagens:**
- ✅ Implementação mais simples
- ✅ Cursor tem controle total sobre o processamento
- ✅ Mais flexível (Cursor decide como usar os dados)
- ✅ Não usa API OpenAI no servidor

**Desvantagens:**
- ❌ Cursor precisa processar os dados
- ❌ Pode consumir mais tokens do Cursor
- ❌ Respostas podem ser menos contextualizadas

---

### Abordagem 2: Funcionalidade Completa com LLM (Recomendada)

**Ferramentas expostas:**
- `search_documents` - Busca no pgVector (dados brutos)
- `ask_question` - Busca + LLM (resposta completa)
- `ingest_document` - Ingesta documentos

**Como funciona:**
```
Cursor → ask_question("pergunta") → Busca pgVector + LLM → Retorna resposta pronta
```

**Vantagens:**
- ✅ Respostas já processadas e contextualizadas
- ✅ Menos processamento no Cursor
- ✅ Melhor experiência do usuário
- ✅ Aproveita todo o sistema RAG já implementado

**Desvantagens:**
- ❌ Mais complexo (mas código já existe!)
- ❌ Usa API OpenAI no servidor (mas já está configurado)

---

## 🎯 Recomendação: **Abordagem Híbrida**

Expor **ambas as opções** para dar flexibilidade ao Cursor:

### Ferramentas Recomendadas:

1. **`search_documents`** (dados brutos)
   - Quando o Cursor quer processar os dados
   - Quando precisa apenas dos documentos relevantes
   - Quando quer fazer múltiplas buscas e combinar resultados

2. **`ask_question`** (resposta completa)
   - Quando o usuário faz uma pergunta direta
   - Quando precisa de resposta contextualizada
   - Quando quer aproveitar o sistema RAG completo

3. **`ingest_document`** (ingestão)
   - Para adicionar novos documentos ao sistema

---

## 📊 Comparação Visual

### Abordagem 1: Apenas Dados
```
┌─────────┐     search_documents      ┌──────────┐
│ Cursor │ ──────────────────────────>│ pgVector │
│ (IA)   │ <──────────────────────────│ (dados)  │
└─────────┘     [documentos brutos]    └──────────┘
     │
     │ Processa e responde
     ▼
┌─────────┐
│ Usuário │
└─────────┘
```

### Abordagem 2: Completa (Recomendada)
```
┌─────────┐     ask_question          ┌──────────┐     ┌──────────┐
│ Cursor │ ─────────────────────────>│ Servidor │ ───>│ pgVector │
│ (IA)   │ <──────────────────────────│ MCP      │ <───│ (dados)  │
└─────────┘     [resposta pronta]     └──────────┘     └──────────┘
     │                                      │
     │                                      │ LLM
     │                                      ▼
     │                                 ┌──────────┐
     │                                 │ OpenAI   │
     │                                 └──────────┘
     │
     ▼
┌─────────┐
│ Usuário │
└─────────┘
```

---

## 💡 Por que Abordagem Híbrida?

1. **Flexibilidade**: Cursor escolhe a melhor ferramenta para cada situação
2. **Eficiência**: `ask_question` para respostas rápidas, `search_documents` para análise
3. **Aproveitamento**: Usa todo o código RAG já implementado
4. **Simplicidade**: Não precisa criar novo agente IA (Cursor já é o agente)

---

## 🔧 Implementação Sugerida

### Estrutura de Ferramentas:

```python
# Ferramenta 1: Busca simples (dados brutos)
@tool("search_documents")
async def search_documents(question: str, k: int = 10):
    """
    Busca documentos relevantes no pgVector.
    Retorna documentos brutos para processamento pelo Cursor.
    """
    # Usa search.py - retorna documentos com scores
    store = create_vector_store()
    results = store.similarity_search_with_score(question, k=k)
    return {
        "documents": [
            {"content": doc.page_content, "score": score, "metadata": doc.metadata}
            for doc, score in results
        ]
    }

# Ferramenta 2: Pergunta completa (resposta pronta)
@tool("ask_question")
async def ask_question(question: str):
    """
    Faz uma pergunta completa usando RAG.
    Retorna resposta processada pelo LLM baseada no contexto.
    """
    # Usa chat.py - retorna resposta completa
    return generate_response_with_llm(question)

# Ferramenta 3: Ingestão
@tool("ingest_document")
async def ingest_document(pdf_path: str):
    """
    Ingesta um documento PDF no sistema RAG.
    """
    # Usa ingest.py
    documents = load_pdf(pdf_path)
    chunks = get_chunks(documents)
    success = store_embeddings_pgvector(chunks)
    return {"status": "success" if success else "error"}
```

---

## ✅ Conclusão

**Você NÃO precisa criar um agente IA no servidor MCP.**

**Recomendação**: Expor **ambas as ferramentas** (`search_documents` e `ask_question`) para dar flexibilidade ao Cursor, que já é o agente IA e decide quando usar cada uma.

**Vantagens desta abordagem:**
- ✅ Aproveita todo o código RAG já implementado
- ✅ Cursor tem flexibilidade para escolher a melhor ferramenta
- ✅ Não precisa criar novo agente IA
- ✅ Implementação simples (apenas expor funções existentes)
