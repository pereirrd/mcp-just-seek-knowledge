# 🗺️ Roteiro de Atividades - Servidor MCP: Base de Conhecimento APIs Java

## 📋 Contexto do Projeto

### Objetivo
Criar um servidor MCP que armazena e busca conhecimento gerado por IA sobre projetos Java de APIs REST, permitindo ao Cursor acessar informações sobre:
- Estruturas de APIs REST
- Padrões de projeto
- Boas práticas
- Documentação técnica

### Decisões Arquiteturais
- **Linguagem**: Python
- **Framework para Embeddings**: LangChain
- **Banco de Dados**: PostgreSQL com pgVector
- **Protocolo**: MCP (Model Context Protocol) para integração com Cursor
- **Dados**: Conhecimento gerado por IA (não código Java direto)

### Funcionalidades Principais
1. **Ingest**: Criar novos registros na base de conhecimento
2. **Update**: Atualizar registros existentes na base de conhecimento
3. **Search**: Buscar conhecimento semântico na base

---

## 🎯 Fase 1: Preparação e Estrutura Inicial

### 1.1 Criar Estrutura de Diretórios
**Atividades:**
- [x] Criar diretório raiz do projeto
- [x] Criar estrutura de diretórios `src/`
- [x] Criar subdiretórios:
  - [x] `src/database/` - Gerenciamento de banco de dados
  - [x] `src/embeddings/` - Serviços de embeddings
  - [x] `src/services/` - Serviços de negócio (ingest, update, search)
  - [x] `src/mcp/` - Servidor MCP e handlers
- [x] Criar arquivos `__init__.py` nos pacotes Python

**Entregáveis:**
- Estrutura de diretórios completa
- Arquivos `__init__.py` criados

---

### 1.2 Configurar Dependências
**Atividades:**
- [x] Criar arquivo `requirements.txt`
- [x] Adicionar dependências:
  - [x] `langchain` - Framework principal
  - [x] `langchain-community` - Comunidade LangChain
  - [x] `langchain-core` - Core do LangChain
  - [x] `langchain-openai` - Integração OpenAI
  - [x] `langchain-postgres` - Integração PostgreSQL/pgVector
  - [x] `psycopg` - Driver PostgreSQL
  - [x] `pgvector` - Extensão pgVector
  - [x] `openai` - Cliente OpenAI
  - [x] `python-dotenv` - Gerenciamento de variáveis de ambiente
- [x] Definir versões específicas das dependências

**Entregáveis:**
- Arquivo `requirements.txt` com todas as dependências

---

### 1.3 Configurar Variáveis de Ambiente
**Atividades:**
- [x] Criar arquivo `.env.example`
- [x] Definir variáveis necessárias:
  - [x] `PGVECTOR_URL` - URL de conexão PostgreSQL
  - [x] `POSTGRES_DB` - Nome do banco de dados
  - [x] `POSTGRES_USER` - Usuário PostgreSQL
  - [x] `POSTGRES_PASSWORD` - Senha PostgreSQL
  - [x] `OPENAI_API_KEY` - Chave API OpenAI
  - [x] `OPENAI_EMBEDDING_MODEL` - Modelo de embedding (ex: text-embedding-3-small)
  - [x] `EMBEDDING_DIMENSION` - Dimensão dos embeddings (ex: 1536)
- [x] Documentar cada variável no `.env.example`
- [x] Criar arquivo `.gitignore` para excluir `.env`

**Entregáveis:**
- Arquivo `.env.example` com todas as variáveis
- Arquivo `.gitignore` atualizado

---

### 1.4 Configurar Docker e PostgreSQL
**Atividades:**
- [x] Criar arquivo `docker-compose.yml`
- [x] Configurar serviço PostgreSQL com pgVector
- [x] Configurar volumes para persistência
- [x] Configurar healthcheck
- [x] Criar script de inicialização da extensão pgvector
- [x] Documentar como iniciar o banco

**Entregáveis:**
- Arquivo `docker-compose.yml` funcional
- Documentação de como iniciar o banco

---

## 🗄️ Fase 2: Configuração do Banco de Dados

### 2.1 Definir Schema do Banco
**Atividades:**
- [x] Criar módulo `src/database/schema.py`
- [x] Definir estrutura da tabela de conhecimento:
  - [x] `id` - Identificador único (SERIAL PRIMARY KEY)
  - [x] `service_name` - Nome do serviço analisado (VARCHAR/TEXT, NOT NULL, UNIQUE)
  - [x] `content` - Conteúdo do conhecimento (TEXT NOT NULL)
  - [x] `embedding` - Vetor de embedding (vector(1536) NOT NULL)
  - [x] `metadata` - Metadados adicionais (JSONB)
  - [x] `created_at` - Data de criação (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - [x] `updated_at` - Data de atualização (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- [x] Definir constraint UNIQUE para `service_name`
- [x] Definir índices:
  - [x] Índice IVFFlat para busca vetorial
  - [x] Índice para `service_name` (para buscas por serviço)
- [x] Criar trigger para atualizar `updated_at` automaticamente

**Decisões:**
- `service_name` é obrigatório, único e necessário para identificar serviços e permitir updates
- Metadata JSONB permite flexibilidade para armazenar informações adicionais
- Um registro por `service_name` - atualizações sobrescrevem o registro existente

**Modelagem do Schema:**
```sql
CREATE TABLE java_api_knowledge (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca vetorial
CREATE INDEX idx_knowledge_embedding 
ON java_api_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice para service_name
CREATE INDEX idx_knowledge_service_name 
ON java_api_knowledge (service_name);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_java_api_knowledge_updated_at
BEFORE UPDATE ON java_api_knowledge
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

**Entregáveis:**
- Script SQL para criação da tabela
- Script SQL para criação de índices otimizados
- Trigger para atualizar `updated_at`

---

### 2.2 Implementar Gerenciamento de Conexão
**Atividades:**
- [x] Criar módulo `src/database/connection.py`
- [x] Implementar classe/módulo para gerenciar conexões
- [x] Implementar função de conexão com PostgreSQL
- [x] Implementar função para criar schema (tabela e índices)
- [x] Implementar função para verificar se schema existe
- [x] Adicionar tratamento de erros de conexão
- [x] Adicionar logs para debug

**Entregáveis:**
- Módulo `connection.py` funcional
- Função para inicializar schema do banco

---

### 2.3 Implementar Repositório de Dados (com LangChain)
**Atividades:**
- [x] Criar módulo `src/database/repository.py`
- [x] Implementar classe usando `PGVector` do LangChain
- [x] Configurar conexão com PostgreSQL
- [x] Implementar métodos básicos:
  - [x] Inserir documento (com embedding)
  - [x] Buscar por similaridade
  - [x] Buscar por service_name
  - [x] Atualizar documento por service_name
- [x] Integrar com serviço de embeddings

**Decisões:**
- Usar `PGVector` do LangChain para abstrair operações
- Manter compatibilidade com estrutura de metadados

**Entregáveis:**
- Módulo `repository.py` com operações CRUD
- Integração com LangChain PGVector

---

## 🔢 Fase 3: Serviços de Embeddings

### 3.1 Implementar Serviço de Embeddings
**Atividades:**
- [x] Criar módulo `src/embeddings/embedding_service.py`
- [x] Implementar classe usando `OpenAIEmbeddings` do LangChain
- [x] Configurar modelo de embedding (text-embedding-3-small)
- [x] Implementar método para criar embedding de texto
- [x] Implementar método para criar embeddings em batch (otimização)
- [x] Adicionar tratamento de erros
- [x] Adicionar logs

**Entregáveis:**
- Serviço de embeddings funcional
- Suporte a embedding único e batch

---

## 🔧 Fase 4: Serviços de Negócio

### 4.1 Implementar Serviço de Ingest
**Atividades:**
- [x] Criar módulo `src/services/ingest_service.py`
- [x] Implementar função/classe para ingerir conhecimento:
  - [x] Receber conteúdo do conhecimento
  - [x] Receber service_name (obrigatório)
  - [x] Receber metadados (opcional)
  - [x] Criar embedding do conteúdo
  - [x] Inserir no banco de dados
- [x] Validar dados de entrada
- [x] Tratar erros de ingestão
- [x] Retornar resultado da operação (sucesso/erro)
- [x] Adicionar logs

**Entregáveis:**
- Serviço de ingest funcional
- Validação e tratamento de erros

---

### 4.2 Implementar Serviço de Update
**Atividades:**
- [x] Criar módulo `src/services/update_service.py`
- [x] Implementar função/classe para atualizar conhecimento:
  - [x] Receber service_name (obrigatório)
  - [x] Receber novo conteúdo
  - [x] Receber metadados atualizados (opcional)
  - [x] Se service_name não existe: Criar novo registro - comportamento de upsert
  - [x] Se service_name existe: Atualizar registro existente (conteúdo, embedding, metadados, updated_at)
  - [x] Criar novo embedding do conteúdo atualizado
  - [x] Atualizar registro no banco de dados
- [x] Validar dados de entrada
- [x] Tratar erros de atualização
- [x] Retornar resultado da operação
- [x] Adicionar logs

**Decisões Tomadas:**
- ✅ **Estratégia de Update**: Atualização direta do registro (sem versionamento)
- ✅ **Comportamento quando service_name não existe**: Criar novo registro (upsert)
- ✅ **Campo updated_at**: Atualizado automaticamente via trigger do banco de dados

**Entregáveis:**
- Serviço de update funcional
- Lógica de upsert implementada

---

### 4.3 Implementar Serviço de Search
**Atividades:**
- [x] Criar módulo `src/services/search_service.py`
- [x] Implementar função/classe para buscar conhecimento:
  - [x] Receber query (texto de busca)
  - [x] Receber parâmetros opcionais (k, threshold, etc.)
  - [x] Criar embedding da query
  - [x] Buscar documentos similares no banco
  - [x] Filtrar por threshold de similaridade (opcional)
  - [x] Retornar resultados ordenados por relevância
- [x] Implementar filtros opcionais:
  - [x] Filtrar por service_name
  - [x] Filtrar por metadados
- [x] Formatar resultados de retorno (incluir service_name)
- [x] Tratar erros de busca
- [x] Adicionar logs

**Decisões:**
- Busca semântica utiliza todos os registros da tabela

**Entregáveis:**
- Serviço de search funcional
- Busca semântica com filtros opcionais

---

## 🔌 Fase 5: Servidor MCP

### 5.1 Implementar Estrutura Base do Servidor MCP
**Atividades:**
- [x] Criar módulo `src/mcp/mcp_server.py`
- [x] Implementar classe principal do servidor MCP
- [x] Implementar protocolo JSON-RPC 2.0:
  - [x] Handshake inicial (`initialize`)
  - [x] Listar ferramentas (`tools/list`)
  - [x] Chamar ferramenta (`tools/call`)
- [x] Implementar leitura de stdin (JSON-RPC)
- [x] Implementar escrita em stdout (JSON-RPC)
- [x] Implementar tratamento de erros JSON-RPC
- [x] Adicionar logs

**Entregáveis:**
- Servidor MCP básico funcional
- Protocolo JSON-RPC 2.0 implementado

---

### 5.2 Implementar Tool: Ingest
**Atividades:**
- [x] Criar handler para tool `ingest` no servidor MCP
- [x] Definir schema de entrada (inputSchema):
  - [x] `service_name` - Nome do serviço (string, required)
  - [x] `content` - Conteúdo do conhecimento (string, required)
  - [x] `metadata` - Metadados adicionais (object, optional)
- [x] Integrar com `ingest_service`
- [x] Validar parâmetros de entrada
- [x] Tratar erros e retornar respostas apropriadas
- [x] Formatar resposta JSON-RPC
- [x] Adicionar logs

**Entregáveis:**
- Tool `ingest` funcional
- Schema de entrada documentado

---

### 5.3 Implementar Tool: Update
**Atividades:**
- [x] Criar handler para tool `update` no servidor MCP
- [x] Definir schema de entrada (inputSchema):
  - [x] `service_name` - Nome do serviço (string, required)
  - [x] `content` - Novo conteúdo (string, required)
  - [x] `metadata` - Metadados atualizados (object, optional)
- [x] Integrar com `update_service`
- [x] Validar parâmetros de entrada
- [x] Tratar erros (ex: service_name não existe)
- [x] Formatar resposta JSON-RPC
- [x] Adicionar logs

**Entregáveis:**
- Tool `update` funcional
- Schema de entrada documentado

---

### 5.4 Implementar Tool: Search
**Atividades:**
- [x] Criar handler para tool `search` no servidor MCP
- [x] Definir schema de entrada (inputSchema):
  - [x] `query` - Texto de busca (string, required)
  - [x] `k` - Número de resultados (integer, optional, default: 10)
  - [x] `service_name` - Filtrar por serviço (string, optional)
  - [x] `threshold` - Threshold de similaridade (float, optional)
- [x] Integrar com `search_service`
- [x] Validar parâmetros de entrada
- [x] Tratar erros de busca
- [x] Formatar resposta JSON-RPC com resultados
- [x] Adicionar logs

**Entregáveis:**
- Tool `search` funcional
- Schema de entrada documentado

---

### 5.5 Criar Entry Point do Servidor
**Atividades:**
- [x] Criar arquivo `src/mcp_server.py` (ou ajustar estrutura)
- [x] Implementar função `main()` ou `run()`
- [x] Carregar variáveis de ambiente
- [x] Inicializar serviços (database, embeddings, etc.)
- [x] Inicializar servidor MCP
- [x] Iniciar loop principal do servidor
- [x] Tratar sinal de interrupção (Ctrl+C)
- [x] Adicionar logs de inicialização

**Entregáveis:**
- Entry point funcional do servidor
- Servidor iniciando corretamente

---

## ⚙️ Fase 6: Configuração MCP

### 6.1 Criar Arquivo de Configuração MCP
**Atividades:**
- [ ] Criar arquivo `mcp.json` (ou `.cursor/mcp.json`)
- [ ] Configurar servidor MCP:
  - [ ] Nome do servidor
  - [ ] Comando para executar (python + script)
  - [ ] Argumentos do comando
  - [ ] Variáveis de ambiente
- [ ] Usar caminhos absolutos para o script
- [ ] Passar variáveis de ambiente do `.env`
- [ ] Documentar configuração

**Decisões:**
- Localização do arquivo (projeto vs `~/.cursor/`)
- Como gerenciar variáveis de ambiente no `mcp.json`

**Entregáveis:**
- Arquivo `mcp.json` configurado
- Documentação da configuração

---

## 🧪 Fase 7: Testes e Validação

### 7.1 Testes Unitários Básicos
**Atividades:**
- [ ] Criar estrutura de testes (`tests/` ou `src/tests/`)
- [ ] Testar serviços de embeddings
- [ ] Testar repositório de dados (mocks)
- [ ] Testar serviços de negócio (ingest, update, search)
- [ ] Testar handlers MCP (mocks)
- [ ] Validar schemas de entrada/saída

**Entregáveis:**
- Testes unitários básicos
- Cobertura mínima de funcionalidades críticas

---

### 7.2 Testes de Integração
**Atividades:**
- [ ] Testar integração com PostgreSQL (Docker)
- [ ] Testar fluxo completo de ingest
- [ ] Testar fluxo completo de update
- [ ] Testar fluxo completo de search
- [ ] Testar casos de erro
- [ ] Validar performance básica

**Entregáveis:**
- Testes de integração funcionais
- Validação de fluxos completos

---

### 7.3 Testar Integração com Cursor
**Atividades:**
- [ ] Verificar se Cursor detecta o servidor MCP
- [ ] Testar tool `ingest` via Cursor
- [ ] Testar tool `update` via Cursor
- [ ] Testar tool `search` via Cursor
- [ ] Validar respostas JSON-RPC
- [ ] Testar tratamento de erros via Cursor

**Entregáveis:**
- Integração com Cursor funcionando
- Todas as tools testadas

---

## 📚 Fase 8: Documentação

### 8.1 Documentação do Projeto
**Atividades:**
- [ ] Criar/atualizar `README.md`:
  - [ ] Descrição do projeto
  - [ ] Requisitos
  - [ ] Instalação
  - [ ] Configuração
  - [ ] Uso
  - [ ] Estrutura do projeto
- [ ] Documentar variáveis de ambiente
- [ ] Documentar estrutura do banco de dados
- [ ] Documentar APIs das tools MCP
- [ ] Adicionar exemplos de uso

**Entregáveis:**
- README completo e atualizado
- Documentação de APIs

---

## 🚀 Fase 9: Refinamento e Otimização

### 9.1 Otimizações
**Atividades:**
- [ ] Revisar queries SQL para performance
- [ ] Otimizar criação de embeddings (batch)
- [ ] Revisar índices do banco
- [ ] Otimizar uso de memória
- [ ] Revisar logs e mensagens de erro

**Entregáveis:**
- Código otimizado
- Performance validada

---

### 9.2 Melhorias e Ajustes
**Atividades:**
- [ ] Revisar tratamento de erros
- [ ] Melhorar mensagens de log
- [ ] Validar casos extremos
- [ ] Revisar estrutura de metadados
- [ ] Considerar funcionalidades adicionais (se necessário)

**Entregáveis:**
- Código revisado e melhorado
- Robustez validada

---

## 📊 Resumo das Fases

| Fase | Descrição | Prioridade | Complexidade |
|------|-----------|------------|--------------|
| 1 | Preparação e Estrutura | Alta | Baixa |
| 2 | Banco de Dados | Alta | Média |
| 3 | Embeddings | Alta | Baixa |
| 4 | Serviços de Negócio | Alta | Média |
| 5 | Servidor MCP | Alta | Alta |
| 6 | Configuração MCP | Alta | Baixa |
| 7 | Testes | Média | Média |
| 8 | Documentação | Média | Baixa |
| 9 | Refinamento | Baixa | Média |

---

## 🔑 Decisões Tomadas

1. **Estratégia de Update**: ✅ **Atualização direta (sem versionamento)**
   - Sistema não mantém histórico - cada `service_name` tem apenas um registro
   - Atualizações sobrescrevem o registro existente
   - Campo `updated_at` é atualizado automaticamente via trigger

2. **Comportamento quando service_name não existe no update**: ✅ **Criar novo registro (upsert)**
   - Se `service_name` não existe, criar novo registro
   - Comportamento de upsert permite usar update mesmo para novos serviços

3. **Localização do arquivo mcp.json**: ✅ **No projeto (`.cursor/mcp.json`)**
   - Arquivo de configuração MCP será criado em `.cursor/mcp.json` no projeto

## 🔑 Decisões Pendentes

4. **Estrutura de Metadata**:
   - [ ] Definir campos obrigatórios
   - [ ] Definir campos opcionais
   - [ ] Validar estrutura

5. **Tratamento de Erros no MCP**:
   - [ ] Níveis de erro
   - [ ] Mensagens de erro
   - [ ] Logs de erro

---

## 📝 Notas Importantes

- **LangChain**: Decisão tomada de usar LangChain apesar da recomendação geral de usar direto para MCP. Isso deve ser considerado nas implementações.
- **Conhecimento Gerado por IA**: O projeto não ingere código Java diretamente, mas conhecimento gerado por IA sobre projetos Java de APIs REST.
- **Service Name**: É obrigatório para ingest e update. É fundamental para identificar serviços e permitir updates. Deve ser único e identificável (constraint UNIQUE no banco).
- **Modelo de Dados Simplificado**: Sistema não mantém histórico - cada service_name tem apenas um registro. Atualizações sobrescrevem o registro existente e atualizam o campo `updated_at`.
- **Update com Upsert**: Se service_name não existe no update, cria novo registro (comportamento de upsert).
- **Embeddings**: Usar modelo text-embedding-3-small (1536 dimensões) como padrão.
- **PostgreSQL**: Usar Docker para facilitar desenvolvimento e deploy.

---

**Data de Criação**: 2025-01-27  
**Status**: Planejamento  
**Última Atualização**: 2025-01-27