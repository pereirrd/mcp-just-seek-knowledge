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
- [ ] Criar módulo `src/database/schema.py`
- [ ] Definir estrutura da tabela de conhecimento (com versionamento):
  - [ ] `id` - Identificador único (SERIAL PRIMARY KEY)
  - [ ] `service_name` - Nome do serviço analisado (VARCHAR/TEXT, NOT NULL)
  - [ ] `version` - Versão do registro (INTEGER, NOT NULL, DEFAULT 1)
  - [ ] `content` - Conteúdo do conhecimento (TEXT NOT NULL)
  - [ ] `embedding` - Vetor de embedding (vector(1536) NOT NULL)
  - [ ] `metadata` - Metadados adicionais (JSONB)
  - [ ] `is_current` - Marca versão atual (BOOLEAN, NOT NULL, DEFAULT true)
  - [ ] `created_at` - Data de criação (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - [ ] `updated_at` - Data de atualização (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- [ ] Definir constraint UNIQUE para `(service_name, version)`
- [ ] Definir índices:
  - [ ] Índice IVFFlat para busca vetorial (apenas em `is_current = true`)
  - [ ] Índice composto para `(service_name, version)`
  - [ ] Índice para `service_name` e `is_current` (para buscar versão atual)
- [ ] Criar função SQL para limpar versões antigas (manter apenas últimas 5 por service_name)
- [ ] Criar trigger para atualizar `updated_at` automaticamente
- [ ] Criar função/procedimento para gerenciar versionamento ao inserir/atualizar

**Decisões:**
- `service_name` é obrigatório e necessário para identificar serviços e permitir updates
- **Versionamento**: Sistema mantém histórico das últimas 5 versões por `service_name`
- `version` incrementa a cada atualização do mesmo `service_name`
- `is_current` marca a versão mais recente para busca semântica
- Metadata JSONB permite flexibilidade para armazenar informações adicionais
- Limpeza automática: Ao inserir nova versão, remover versões antigas além das 5 mais recentes

**Modelagem do Schema:**
```sql
CREATE TABLE java_api_knowledge (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    is_current BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_name, version)
);

-- Índice para busca vetorial (apenas versões atuais)
CREATE INDEX idx_knowledge_embedding_current 
ON java_api_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE is_current = true;

-- Índice composto para service_name e version
CREATE INDEX idx_knowledge_service_version 
ON java_api_knowledge (service_name, version);

-- Índice para buscar versão atual por service_name
CREATE INDEX idx_knowledge_service_current 
ON java_api_knowledge (service_name, is_current) 
WHERE is_current = true;

-- Função para manter apenas últimas 5 versões
CREATE OR REPLACE FUNCTION keep_latest_versions(p_service_name VARCHAR)
RETURNS void AS $$
DECLARE
    max_version INTEGER;
    min_version_to_keep INTEGER;
BEGIN
    -- Obter versão máxima
    SELECT MAX(version) INTO max_version 
    FROM java_api_knowledge 
    WHERE service_name = p_service_name;
    
    -- Calcular versão mínima a manter (últimas 5)
    min_version_to_keep := GREATEST(1, max_version - 4);
    
    -- Remover versões antigas
    DELETE FROM java_api_knowledge 
    WHERE service_name = p_service_name 
    AND version < min_version_to_keep;
END;
$$ LANGUAGE plpgsql;

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
- Script SQL para criação da tabela com versionamento
- Script SQL para criação de índices otimizados
- Função para limpeza automática de versões antigas
- Trigger para atualizar `updated_at`
- Procedimento para gerenciar versionamento

---

### 2.2 Implementar Gerenciamento de Conexão
**Atividades:**
- [ ] Criar módulo `src/database/connection.py`
- [ ] Implementar classe/módulo para gerenciar conexões
- [ ] Implementar função de conexão com PostgreSQL
- [ ] Implementar função para criar schema (tabela e índices)
- [ ] Implementar função para verificar se schema existe
- [ ] Adicionar tratamento de erros de conexão
- [ ] Adicionar logs para debug

**Entregáveis:**
- Módulo `connection.py` funcional
- Função para inicializar schema do banco

---

### 2.3 Implementar Repositório de Dados (com LangChain)
**Atividades:**
- [ ] Criar módulo `src/database/repository.py`
- [ ] Implementar classe usando `PGVector` do LangChain
- [ ] Configurar conexão com PostgreSQL
- [ ] Configurar filtro padrão para `is_current = true` nas buscas semânticas
- [ ] Implementar métodos básicos:
  - [ ] Inserir documento (com embedding, version 1)
  - [ ] Buscar por similaridade (apenas `is_current = true`)
  - [ ] Buscar por service_name (versão atual)
  - [ ] Buscar histórico por service_name (todas as versões)
  - [ ] Criar nova versão (update com versionamento)
  - [ ] Chamar função de limpeza de versões antigas
- [ ] Integrar com serviço de embeddings
- [ ] Implementar métodos específicos para versionamento:
  - [ ] Obter versão atual por service_name
  - [ ] Obter próxima versão para service_name
  - [ ] Marcar versão anterior como não atual

**Decisões:**
- Usar `PGVector` do LangChain para abstrair operações
- Busca semântica sempre filtra por `is_current = true`
- Manter compatibilidade com estrutura de metadados incluindo versionamento

**Entregáveis:**
- Módulo `repository.py` com operações CRUD e versionamento
- Integração com LangChain PGVector
- Métodos para gerenciar versões

---

## 🔢 Fase 3: Serviços de Embeddings

### 3.1 Implementar Serviço de Embeddings
**Atividades:**
- [ ] Criar módulo `src/embeddings/embedding_service.py`
- [ ] Implementar classe usando `OpenAIEmbeddings` do LangChain
- [ ] Configurar modelo de embedding (text-embedding-3-small)
- [ ] Implementar método para criar embedding de texto
- [ ] Implementar método para criar embeddings em batch (otimização)
- [ ] Adicionar tratamento de erros
- [ ] Adicionar logs

**Entregáveis:**
- Serviço de embeddings funcional
- Suporte a embedding único e batch

---

## 🔧 Fase 4: Serviços de Negócio

### 4.1 Implementar Serviço de Ingest
**Atividades:**
- [ ] Criar módulo `src/services/ingest_service.py`
- [ ] Implementar função/classe para ingerir conhecimento:
  - [ ] Receber conteúdo do conhecimento
  - [ ] Receber service_name (obrigatório)
  - [ ] Receber metadados (opcional)
  - [ ] Criar embedding do conteúdo
  - [ ] Inserir no banco de dados
- [ ] Validar dados de entrada
- [ ] Tratar erros de ingestão
- [ ] Retornar resultado da operação (sucesso/erro)
- [ ] Adicionar logs

**Entregáveis:**
- Serviço de ingest funcional
- Validação e tratamento de erros

---

### 4.2 Implementar Serviço de Update
**Atividades:**
- [ ] Criar módulo `src/services/update_service.py`
- [ ] Implementar função/classe para atualizar conhecimento (com versionamento):
  - [ ] Receber service_name (obrigatório)
  - [ ] Receber novo conteúdo
  - [ ] Receber metadados atualizados (opcional)
  - [ ] Buscar versão atual por service_name
  - [ ] Se service_name não existe: Criar novo registro (version 1) - comportamento de upsert
  - [ ] Se service_name existe:
    - [ ] Marcar versão atual como `is_current = false`
    - [ ] Calcular nova versão (versão máxima + 1)
    - [ ] Criar novo embedding do conteúdo atualizado
    - [ ] Inserir novo registro com `is_current = true` e nova versão
    - [ ] Chamar função SQL para limpar versões antigas (manter apenas últimas 5)
  - [ ] Retornar informação da versão criada
- [ ] Implementar transação para garantir consistência (marcar antiga como não atual + inserir nova)
- [ ] Validar dados de entrada
- [ ] Tratar erros de atualização
- [ ] Retornar resultado da operação (incluindo versão criada)
- [ ] Adicionar logs

**Decisões Tomadas:**
- ✅ **Estratégia de Update**: Versionamento (manter histórico das últimas 5 versões)
- ✅ **Comportamento quando service_name não existe**: Criar novo registro (upsert - version 1)
- ✅ **Limpeza de versões**: Manter apenas as últimas 5 versões por service_name
- ✅ **Busca semântica**: Usar apenas registros com `is_current = true` para busca

**Entregáveis:**
- Serviço de update funcional com versionamento
- Lógica de upsert implementada
- Limpeza automática de versões antigas

---

### 4.3 Implementar Serviço de Search
**Atividades:**
- [ ] Criar módulo `src/services/search_service.py`
- [ ] Implementar função/classe para buscar conhecimento:
  - [ ] Receber query (texto de busca)
  - [ ] Receber parâmetros opcionais (k, threshold, etc.)
  - [ ] Criar embedding da query
  - [ ] Buscar documentos similares no banco (apenas `is_current = true`)
  - [ ] Filtrar por threshold de similaridade (opcional)
  - [ ] Retornar resultados ordenados por relevância
- [ ] Implementar filtros opcionais:
  - [ ] Filtrar por service_name (versão atual)
  - [ ] Filtrar por metadados
- [ ] Formatar resultados de retorno (incluir service_name, version quando relevante)
- [ ] Tratar erros de busca
- [ ] Adicionar logs

**Decisões:**
- Busca semântica sempre utiliza apenas versões atuais (`is_current = true`)
- Busca por service_name retorna apenas a versão atual

**Entregáveis:**
- Serviço de search funcional
- Busca semântica com filtros opcionais
- Integração com sistema de versionamento

---

## 🔌 Fase 5: Servidor MCP

### 5.1 Implementar Estrutura Base do Servidor MCP
**Atividades:**
- [ ] Criar módulo `src/mcp/mcp_server.py`
- [ ] Implementar classe principal do servidor MCP
- [ ] Implementar protocolo JSON-RPC 2.0:
  - [ ] Handshake inicial (`initialize`)
  - [ ] Listar ferramentas (`tools/list`)
  - [ ] Chamar ferramenta (`tools/call`)
- [ ] Implementar leitura de stdin (JSON-RPC)
- [ ] Implementar escrita em stdout (JSON-RPC)
- [ ] Implementar tratamento de erros JSON-RPC
- [ ] Adicionar logs

**Entregáveis:**
- Servidor MCP básico funcional
- Protocolo JSON-RPC 2.0 implementado

---

### 5.2 Implementar Tool: Ingest
**Atividades:**
- [ ] Criar handler para tool `ingest` no servidor MCP
- [ ] Definir schema de entrada (inputSchema):
  - [ ] `service_name` - Nome do serviço (string, required)
  - [ ] `content` - Conteúdo do conhecimento (string, required)
  - [ ] `metadata` - Metadados adicionais (object, optional)
- [ ] Integrar com `ingest_service`
- [ ] Validar parâmetros de entrada
- [ ] Tratar erros e retornar respostas apropriadas
- [ ] Formatar resposta JSON-RPC
- [ ] Adicionar logs

**Entregáveis:**
- Tool `ingest` funcional
- Schema de entrada documentado

---

### 5.3 Implementar Tool: Update
**Atividades:**
- [ ] Criar handler para tool `update` no servidor MCP
- [ ] Definir schema de entrada (inputSchema):
  - [ ] `service_name` - Nome do serviço (string, required)
  - [ ] `content` - Novo conteúdo (string, required)
  - [ ] `metadata` - Metadados atualizados (object, optional)
- [ ] Integrar com `update_service`
- [ ] Validar parâmetros de entrada
- [ ] Tratar erros (ex: service_name não existe)
- [ ] Formatar resposta JSON-RPC
- [ ] Adicionar logs

**Entregáveis:**
- Tool `update` funcional
- Schema de entrada documentado

---

### 5.4 Implementar Tool: Search
**Atividades:**
- [ ] Criar handler para tool `search` no servidor MCP
- [ ] Definir schema de entrada (inputSchema):
  - [ ] `query` - Texto de busca (string, required)
  - [ ] `k` - Número de resultados (integer, optional, default: 10)
  - [ ] `service_name` - Filtrar por serviço (string, optional)
  - [ ] `threshold` - Threshold de similaridade (float, optional)
- [ ] Integrar com `search_service`
- [ ] Validar parâmetros de entrada
- [ ] Tratar erros de busca
- [ ] Formatar resposta JSON-RPC com resultados
- [ ] Adicionar logs

**Entregáveis:**
- Tool `search` funcional
- Schema de entrada documentado

---

### 5.5 Criar Entry Point do Servidor
**Atividades:**
- [ ] Criar arquivo `src/mcp_server.py` (ou ajustar estrutura)
- [ ] Implementar função `main()` ou `run()`
- [ ] Carregar variáveis de ambiente
- [ ] Inicializar serviços (database, embeddings, etc.)
- [ ] Inicializar servidor MCP
- [ ] Iniciar loop principal do servidor
- [ ] Tratar sinal de interrupção (Ctrl+C)
- [ ] Adicionar logs de inicialização

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

1. **Estratégia de Update**: ✅ **Versionamento (manter histórico)**
   - Sistema mantém histórico das últimas 5 versões por `service_name`
   - Cada atualização cria nova versão (versão anterior marcada como `is_current = false`)
   - Versões antigas além das 5 mais recentes são removidas automaticamente
   - Busca semântica utiliza apenas versões atuais (`is_current = true`)

2. **Comportamento quando service_name não existe no update**: ✅ **Criar novo registro (upsert)**
   - Se `service_name` não existe, criar novo registro com `version = 1`
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
- **Service Name**: É obrigatório para ingest e update. É fundamental para identificar serviços e permitir updates. Deve ser único e identificável.
- **Versionamento**: Sistema mantém histórico das últimas 5 versões por service_name. Cada atualização cria nova versão, mantendo a anterior marcada como não atual. Versões antigas são limpas automaticamente.
- **Update com Upsert**: Se service_name não existe no update, cria novo registro (comportamento de upsert).
- **Busca Semântica**: Busca utiliza apenas versões atuais (`is_current = true`) para garantir resultados mais relevantes.
- **Embeddings**: Usar modelo text-embedding-3-small (1536 dimensões) como padrão.
- **PostgreSQL**: Usar Docker para facilitar desenvolvimento e deploy.

---

**Data de Criação**: 2025-01-27  
**Status**: Planejamento  
**Última Atualização**: 2025-01-27