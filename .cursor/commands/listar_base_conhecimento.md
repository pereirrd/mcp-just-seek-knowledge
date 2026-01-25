# /listar_base_conhecimento — Listar catálogo da base de conhecimento

Você deve **listar todos os `service_name` existentes** na base de conhecimento, usando o MCP **`mcp-just-seek-knowledge`** e a tool **`list_catalog`**, e então **enriquecer a listagem** exibindo o `metadata` de cada `service_name`.

## Regras de execução (obrigatórias)

- **Chame exatamente a tool `list_catalog`** do MCP `mcp-just-seek-knowledge`.
- **Não passe argumentos** (a tool não requer `arguments`).
- **Não invente nomes nem metadados**: mostre somente o que vier das tools.

## Execução (obrigatório)

### 1) Listar catálogo

- Tool: **`mcp-just-seek-knowledge.list_catalog`**
- Arguments: **nenhum**

### 2) Buscar `metadata` por `service_name` (enriquecimento)

Como `list_catalog` retorna apenas `services` e `count`, para obter `metadata` você deve, para **cada** `service_name` retornado, chamar:

- Tool: **`mcp-just-seek-knowledge.search`**
- Arguments:
  - `query`: o próprio `service_name` (ex.: `"billing-api"`)
  - `service_name`: o mesmo `service_name` (para filtrar)
  - `k`: `1`

Depois, para cada chamada, use `results[0]` (se existir) e extraia:
- `service_name`
- `metadata`
- (opcional) `updated_at` / `created_at` para ajudar no layout

## Saída final esperada

- Exiba um layout amigável com:
  - **Total**: `count`
  - **Tabela** (ou lista formatada) com colunas:
    - `service_name`
    - `metadata` (renderizar como JSON legível; se vazio/nulo, mostrar `{}` ou `null`)
    - (opcional) `updated_at`

Se algum `service_name` não retornar `results` na busca, mostre a linha com `metadata` como `null` e sinalize que não foi possível enriquecer aquele item.
