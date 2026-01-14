# 📋 Requisitos para Transformar em Servidor MCP

## O que é necessário

Para transformar este projeto RAG em um servidor MCP utilizável no Cursor, você precisa implementar os seguintes componentes:

---

## 1. 📦 Dependências Adicionais

### Instalar SDK MCP para Python

```bash
# Opção 1: Usando o pacote oficial (se disponível)
pip install mcp

# Opção 2: Implementação manual do protocolo MCP
# O MCP usa comunicação JSON via stdio, então você pode implementar manualmente
# usando apenas bibliotecas padrão do Python
```

**Nota**: O protocolo MCP é baseado em JSON-RPC 2.0 e comunicação via stdio (stdin/stdout). Você pode implementar manualmente ou usar um SDK se disponível.

---

## 2. 🏗️ Estrutura do Servidor MCP

### Componentes Necessários:

#### A. **Servidor Principal** (`src/mcp_server.py`)
- Implementa o protocolo MCP
- Lê requisições JSON do `stdin`
- Processa chamadas de ferramentas
- Retorna respostas JSON no `stdout`
- Gerencia o ciclo de vida do servidor

#### B. **Ferramentas (Tools) a Expor**

1. **`ingest_document`**
   - **Descrição**: Ingesta um documento PDF no sistema RAG
   - **Parâmetros**:
     - `pdf_path` (string, obrigatório): Caminho para o arquivo PDF
   - **Retorno**: Status da ingestão (sucesso/erro)

2. **`search_documents`**
   - **Descrição**: Busca documentos relevantes usando busca semântica
   - **Parâmetros**:
     - `question` (string, obrigatório): Pergunta ou query de busca
     - `k` (integer, opcional, padrão: 10): Número de resultados a retornar
   - **Retorno**: Lista de documentos relevantes com scores

3. **`ask_question`**
   - **Descrição**: Faz uma pergunta completa usando RAG (busca + LLM)
   - **Parâmetros**:
     - `question` (string, obrigatório): Pergunta do usuário
   - **Retorno**: Resposta gerada pelo LLM baseada no contexto

#### C. **Recursos (Resources) Opcionais**

1. **`document_stats`**
   - **Descrição**: Retorna estatísticas sobre documentos armazenados
   - **Retorno**: Número de documentos, tamanho do banco, etc.

---

## 3. 📝 Arquivo de Configuração MCP

### Localização do arquivo:
- **Opção 1**: `~/.cursor/mcp.json` (configuração global do Cursor)
- **Opção 2**: `.cursor/mcp.json` na raiz do projeto (configuração local)

### Estrutura do `mcp.json`:

```json
{
  "mcpServers": {
    "rag-system": {
      "command": "python",
      "args": [
        "/caminho/absoluto/para/projeto/src/mcp_server.py"
      ],
      "env": {
        "PDF_PATH": "/caminho/para/documento.pdf",
        "PGVECTOR_COLLECTION": "document_embeddings",
        "PGVECTOR_URL": "postgresql://postgres:postgres@localhost:5432/rag",
        "OPENAI_API_KEY": "sua_chave_api_openai",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_MODEL": "gpt-3.5-turbo"
      }
    }
  }
}
```

**Importante**: 
- Use caminhos absolutos no `args`
- Configure todas as variáveis de ambiente necessárias
- O Cursor carrega este arquivo automaticamente ao iniciar

---

## 4. 🔌 Protocolo MCP - Estrutura Básica

### Mensagens MCP seguem o padrão JSON-RPC 2.0:

#### Requisição (do Cursor para o servidor):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "ask_question",
    "arguments": {
      "question": "Qual é o conteúdo do documento?"
    }
  }
}
```

#### Resposta (do servidor para o Cursor):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Resposta gerada pelo LLM..."
      }
    ]
  }
}
```

### Handshake Inicial:

O servidor deve responder ao `initialize`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "rag-system",
      "version": "1.0.0"
    }
  }
}
```

### Listar Ferramentas Disponíveis:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "ingest_document",
        "description": "Ingesta um documento PDF no sistema RAG",
        "inputSchema": {
          "type": "object",
          "properties": {
            "pdf_path": {
              "type": "string",
              "description": "Caminho para o arquivo PDF"
            }
          },
          "required": ["pdf_path"]
        }
      },
      {
        "name": "search_documents",
        "description": "Busca documentos relevantes usando busca semântica",
        "inputSchema": {
          "type": "object",
          "properties": {
            "question": {
              "type": "string",
              "description": "Pergunta ou query de busca"
            },
            "k": {
              "type": "integer",
              "description": "Número de resultados",
              "default": 10
            }
          },
          "required": ["question"]
        }
      },
      {
        "name": "ask_question",
        "description": "Faz uma pergunta completa usando RAG",
        "inputSchema": {
          "type": "object",
          "properties": {
            "question": {
              "type": "string",
              "description": "Pergunta do usuário"
            }
          },
          "required": ["question"]
        }
      }
    ]
  }
}
```

---

## 5. 🔧 Implementação Técnica

### Estrutura Básica do Servidor:

```python
import sys
import json
import asyncio
from typing import Any, Dict

# Importar funções existentes
from ingest import ingest_pdf, load_pdf, get_chunks
from search import search_prompt, create_vector_store
from chat import generate_response_with_llm

class MCPServer:
    def __init__(self):
        self.tools = {
            "ingest_document": self.handle_ingest,
            "search_documents": self.handle_search,
            "ask_question": self.handle_ask
        }
    
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
        """Responde ao handshake inicial"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "rag-system",
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
                        "name": "ingest_document",
                        "description": "Ingesta um documento PDF no sistema RAG",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pdf_path": {
                                    "type": "string",
                                    "description": "Caminho para o arquivo PDF"
                                }
                            },
                            "required": ["pdf_path"]
                        }
                    },
                    # ... outras ferramentas
                ]
            }
        }
    
    async def handle_tool_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Processa chamada de ferramenta"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name in self.tools:
            try:
                result = await self.tools[tool_name](arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                }
            except Exception as e:
                return self.error_response(request_id, -32000, str(e))
        else:
            return self.error_response(request_id, -32601, f"Tool '{tool_name}' not found")
    
    async def handle_ingest(self, arguments: Dict[str, Any]) -> str:
        """Handler para ingest_document"""
        pdf_path = arguments.get("pdf_path")
        # Usar funções de ingest.py
        # ...
        return "Documento ingerido com sucesso"
    
    async def handle_search(self, arguments: Dict[str, Any]) -> str:
        """Handler para search_documents"""
        question = arguments.get("question")
        k = arguments.get("k", 10)
        # Usar funções de search.py
        # ...
        return "Resultados da busca"
    
    async def handle_ask(self, arguments: Dict[str, Any]) -> str:
        """Handler para ask_question"""
        question = arguments.get("question")
        # Usar generate_response_with_llm de chat.py
        return generate_response_with_llm(question)
    
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
    server = MCPServer()
    asyncio.run(server.run())
```

---

## 6. ✅ Checklist de Implementação

- [ ] Instalar dependências MCP (se usar SDK) ou implementar protocolo manualmente
- [ ] Criar `src/mcp_server.py` com implementação do servidor MCP
- [ ] Adaptar funções existentes (`ingest.py`, `search.py`, `chat.py`) para serem chamadas pelo servidor
- [ ] Criar arquivo `mcp.json` com configuração do servidor
- [ ] Configurar variáveis de ambiente no `mcp.json`
- [ ] Testar servidor manualmente (enviar JSON via stdin)
- [ ] Verificar se o Cursor detecta o servidor (`cursor-agent mcp list`)
- [ ] Testar cada ferramenta através do Cursor
- [ ] Adicionar tratamento de erros robusto
- [ ] Adicionar logs para debug (opcional)

---

## 7. 🧪 Testando o Servidor

### Teste Manual (via terminal):

```bash
# Enviar requisição de inicialização
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python src/mcp_server.py

# Enviar requisição para listar ferramentas
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python src/mcp_server.py

# Enviar requisição para chamar ferramenta
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"ask_question","arguments":{"question":"Teste"}}}' | python src/mcp_server.py
```

### Verificar no Cursor:

```bash
# Listar servidores MCP configurados
cursor-agent mcp list

# Verificar logs do Cursor para erros
# (logs geralmente em ~/.cursor/logs/)
```

---

## 8. 📚 Recursos Adicionais

- **Documentação MCP**: https://modelcontextprotocol.io
- **Documentação Cursor MCP**: https://docs.cursor.com/pt-BR/context/mcp
- **Especificação JSON-RPC 2.0**: https://www.jsonrpc.org/specification
- **Exemplos de servidores MCP**: GitHub do ModelContextProtocol

---

## 9. ⚠️ Considerações Importantes

1. **Comunicação stdio**: Todo o protocolo funciona via stdin/stdout
2. **JSON-RPC 2.0**: O MCP usa JSON-RPC 2.0 como base
3. **Assíncrono**: Use `asyncio` para operações assíncronas (importante para chamadas de API)
4. **Variáveis de Ambiente**: Todas devem estar configuradas no `mcp.json`
5. **Caminhos Absolutos**: Use caminhos absolutos no `mcp.json`
6. **Banco de Dados**: PostgreSQL deve estar rodando antes de usar o servidor
7. **Tratamento de Erros**: Implemente tratamento robusto de erros
8. **Logs**: Considere adicionar logs para facilitar debug

---

## 10. 🎯 Resumo Executivo

**O que você precisa fazer:**

1. **Criar servidor MCP** (`src/mcp_server.py`) que:
   - Implementa protocolo JSON-RPC 2.0 via stdio
   - Expõe 3 ferramentas: `ingest_document`, `search_documents`, `ask_question`
   - Integra com código existente (`ingest.py`, `search.py`, `chat.py`)

2. **Configurar `mcp.json`** com:
   - Comando para executar o servidor
   - Variáveis de ambiente necessárias
   - Caminhos absolutos

3. **Testar** a integração com o Cursor

**Complexidade**: Média-Alta (requer conhecimento de JSON-RPC e protocolos de comunicação)

**Tempo estimado**: 4-8 horas para implementação completa e testes
