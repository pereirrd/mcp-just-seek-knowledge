# Roadmap - Nova tool MCP `list_catalog`

## Objetivo

Criar uma nova tool MCP chamada `list_catalog` que **lista todos os valores da coluna `service_name`** presentes na tabela `software_design_knowledge`, retornando ao Cursor uma lista dos serviços/projetos que já temos conhecimento armazenado.

> Observação: neste momento **não implementar nada**. Este documento apenas guia a implementação passo a passo.

---

## Estrutura atual (padrão do projeto)

- **Servidor MCP / roteamento**: `src/mcp/mcp_server.py`
  - `tools/list`: retorna a lista de tools a partir dos JSON em `src/mcp/prompts/`
  - `tools/call`: roteia pelo `name` e formata o resultado como JSON string no campo `result.content[0].text`
- **Definições das tools (schema/descrição)**: `src/mcp/prompts/{tool}.json`
  - Ex.: `ingest.json`, `update.json`, `search.json`
- **Camada de negócio**: `src/services/*_service.py`
  - Ex.: `IngestService`, `UpdateService`, `SearchService`
- **Persistência (Postgres + pgvector)**: `src/database/repository.py` (`KnowledgeRepository`)

---

## Contrato esperado da tool `list_catalog`

### Nome
- `name`: `list_catalog`

### Input
- **Sem parâmetros obrigatórios**.
- `inputSchema` recomendado: objeto vazio (aceitando opcionalmente `include_counts`/`limit` no futuro, mas **não é necessário agora**).

### Output (payload retornado pela tool)
Retornar um JSON (será serializado como texto pelo `MCPServer`) no formato:

- `services`: lista ordenada de `service_name` (strings)
- `count`: total de serviços retornados

Exemplo:

```json
{
  "count": 3,
  "services": ["billing-api", "frontend-app", "user-service"]
}
```

---

## Roadmap de implementação (passo a passo)

### 1) Prompt da tool (schema MCP)
- **Criar** `src/mcp/prompts/list_catalog.json`
- **Seguir o padrão** dos arquivos existentes (`name`, `description`, `inputSchema`)
- `inputSchema.required`: vazio

Checklist:
- [x] Arquivo existe e é JSON válido
- [x] `name` exatamente `list_catalog`
- [x] Descrição explica que a tool lista os `service_name` existentes

---

### 2) Repositório: listar `service_name`
- **Adicionar** um método no `KnowledgeRepository` em `src/database/repository.py`:
  - Nome sugerido: `list_service_names() -> List[str]`
  - Query sugerida:
    - `SELECT service_name FROM software_design_knowledge ORDER BY service_name ASC`
  - Tratamento:
    - Sempre retornar lista (vazia se não houver registros)
    - Log em nível `debug/info` com quantidade retornada

Checklist:
- [x] Método novo no repositório
- [x] Usa conexão e cursor no padrão do arquivo
- [x] Retorna lista ordenada de strings

---

### 3) Service: orquestrar regra de negócio
- **Criar** um service em `src/services/` seguindo o padrão atual:
  - Nome de arquivo sugerido: `list_catalog_service.py`
  - Classe sugerida: `ListCatalogService`
  - Responsabilidade:
    - Chamar `KnowledgeRepository.list_service_names()`
    - Montar payload: `{ "count": <int>, "services": <list[str]> }`

Checklist:
- [x] Service isolado (mesmo padrão dos demais)
- [x] Sem dependência de embeddings (apenas repositório)
- [x] Output estável e previsível

---

### 4) MCPServer: expor a tool
Alterações em `src/mcp/mcp_server.py`:

- **Registrar no `tools/list`**
  - Incluir `"list_catalog"` em `tool_names`
- **Instanciar o service**
  - `self.list_catalog_service = ListCatalogService()`
- **Roteamento no `tools/call`**
  - Adicionar `elif tool_name == "list_catalog": result = self._handle_list_catalog(arguments)`
- **Criar handler**
  - Método sugerido: `_handle_list_catalog(self, arguments: Dict[str, Any]) -> Dict[str, Any]`
  - Sem validação de args (ou validar que `arguments` é dict)

Checklist:
- [x] `tools/list` retorna a nova definição carregando `prompts/list_catalog.json`
- [x] `tools/call` aceita `name=list_catalog`
- [x] Resposta segue o formato já usado (`content[0].type=text`, `text` com JSON identado)

---

### 5) Documentação
- **Atualizar** `README.md` para listar a nova tool em “Funcionalidades Principais”
- Opcional: adicionar uma seção curta “Como usar `list_catalog`”

Checklist:
- [x] README menciona `list_catalog`
- [x] Exemplo de retorno consistente com a implementação

---

## Critérios de aceite

- [ ] `tools/list` inclui `list_catalog`
- [ ] `tools/call` com `name=list_catalog` retorna JSON com `services` e `count`
- [ ] Lista corresponde a todos os `service_name` existentes na base
- [ ] Lista vem ordenada ascendente
- [ ] Não altera dados (somente leitura)

---

## Notas e decisões

- A tabela possui `service_name` **UNIQUE**, então não é necessário `DISTINCT` (mas pode ser usado por segurança sem custo relevante).
- Por ora, a tool não precisa de filtros; se no futuro houver muita cardinalidade, pode-se adicionar `limit`/`prefix`/paginação.

