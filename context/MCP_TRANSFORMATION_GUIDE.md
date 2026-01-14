# Guia de Transformação: Sistema RAG para Servidor MCP

## 📋 O que é necessário para transformar em um servidor MCP

Para transformar este projeto em um servidor MCP (Model Context Protocol) utilizável no Cursor, você precisa:

### 1. **Dependências MCP**
- Instalar o SDK MCP para Python: `mcp` ou `modelcontextprotocol`
- O servidor MCP precisa comunicar via stdio (entrada/saída padrão)

### 2. **Estrutura do Servidor MCP**
- Criar um servidor que implementa o protocolo MCP
- Expor ferramentas (tools) que encapsulam as funcionalidades do RAG
- Configurar recursos (resources) se necessário
- Implementar prompts se necessário

### 3. **Arquivo de Configuração**
- Criar `mcp.json` na raiz do projeto ou em `~/.cursor/mcp.json`
- Configurar o servidor para ser executado via stdio

### 4. **Ferramentas (Tools) a Expor**
Com base no projeto atual, as seguintes ferramentas devem ser expostas:

1. **`ingest_document`** - Ingestão de PDF
   - Parâmetros: `pdf_path` (string)
   - Retorna: Status da ingestão

2. **`search_documents`** - Busca semântica
   - Parâmetros: `question` (string), `k` (número, opcional, padrão: 10)
   - Retorna: Contexto relevante encontrado

3. **`ask_question`** - Pergunta completa com RAG
   - Parâmetros: `question` (string)
   - Retorna: Resposta gerada pelo LLM baseada no contexto

### 5. **Recursos (Resources) Opcionais**
- Listar documentos disponíveis
- Estatísticas do banco de dados

---

## 🛠️ Implementação Passo a Passo

### Passo 1: Instalar Dependências MCP

```bash
pip install mcp
# ou
pip install modelcontextprotocol
```

### Passo 2: Criar o Servidor MCP

Criar arquivo `src/mcp_server.py` que:
- Implementa o protocolo MCP
- Expõe as ferramentas mencionadas
- Usa stdio para comunicação

### Passo 3: Configurar mcp.json

Criar arquivo `mcp.json` ou configurar em `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "rag-system": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "env": {
        "PDF_PATH": "/caminho/para/documento.pdf",
        "PGVECTOR_COLLECTION": "document_embeddings",
        "PGVECTOR_URL": "postgresql://postgres:postgres@localhost:5432/rag",
        "OPENAI_API_KEY": "sua_chave_aqui",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_MODEL": "gpt-3.5-turbo"
      }
    }
  }
}
```

### Passo 4: Estrutura do Servidor MCP

O servidor deve:
- Ler requisições JSON do stdin
- Processar chamadas de ferramentas
- Retornar respostas JSON no stdout
- Seguir o protocolo MCP

---

## 📝 Estrutura Esperada do Código

```python
# Exemplo de estrutura básica
import asyncio
import json
import sys
from mcp import Server, Tool

# Importar funções existentes
from ingest import ingest_pdf, load_pdf, get_chunks
from search import search_prompt
from chat import generate_response_with_llm

# Criar servidor MCP
server = Server("rag-system")

# Registrar ferramentas
@server.tool()
async def ingest_document(pdf_path: str) -> str:
    # Implementação usando ingest.py
    pass

@server.tool()
async def search_documents(question: str, k: int = 10) -> str:
    # Implementação usando search.py
    pass

@server.tool()
async def ask_question(question: str) -> str:
    # Implementação usando chat.py
    pass

# Executar servidor
if __name__ == "__main__":
    asyncio.run(server.run())
```

---

## ⚠️ Considerações Importantes

1. **Protocolo MCP**: O servidor deve seguir o protocolo MCP oficial
2. **Comunicação stdio**: Todas as comunicações via stdin/stdout em JSON
3. **Variáveis de Ambiente**: Configurar todas as variáveis necessárias no mcp.json
4. **Dependências**: Garantir que todas as dependências estejam instaladas
5. **Banco de Dados**: PostgreSQL deve estar rodando antes de usar o servidor

---

## 🔍 Verificação

Após implementar:
1. Verificar se o servidor inicia corretamente
2. Testar cada ferramenta individualmente
3. Verificar logs do Cursor para erros
4. Usar `cursor-agent mcp list` para verificar se o servidor está registrado

---

## 📚 Recursos Adicionais

- Documentação MCP: https://modelcontextprotocol.io
- Documentação Cursor MCP: https://docs.cursor.com/pt-BR/context/mcp
- Exemplos de servidores MCP em Python
