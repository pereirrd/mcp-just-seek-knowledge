# /atualizar_base_conhecimento — Atualizar base de conhecimento do workspace

Você deve **criar uma base de conhecimento completa** sobre o projeto/produto usando **todo o workspace aberto** no Cursor (todos os projetos e diretórios disponíveis), lendo documentação e análises já existentes, e então **atualizando/persistindo o resultado** no MCP **`mcp-just-seek-knowledge`** usando a tool **`update`**.

## Regras de execução (obrigatórias)

- **Use TODO o workspace**: trate cada pasta raiz do workspace como um projeto (monorepo/multi-repo). Analise **cada diretório relevante**.
- **Não invente**: tudo deve ser baseado em evidências do repositório (arquivos e código). Quando afirmar algo, indique **quais arquivos** sustentam aquilo.
- **Aproveite análises existentes**: antes de produzir conclusões, leia e incorpore a documentação interna do repo (ex.: `README.md`, `docs/`, `context/`, `adr/`, `architecture/`, `diagrams/`, etc.).
- **Preferência por `update`**: atualize a base usando `mcp-just-seek-knowledge.update` (comportamento upsert: se não existir, cria).

## O que analisar no workspace (checklist)

### 1) Mapa do(s) projeto(s)

- Identifique os projetos no workspace (cada pasta raiz).
- Para cada projeto, gere:
  - propósito do produto/serviço
  - limites de contexto (bounded contexts), módulos e responsabilidades
  - principais fluxos de negócio (regras de negócio e invariantes)

### 2) Arquitetura e decisões

- Arquitetura (monólito, microserviços, modular monolith, hexagonal, clean, onion, etc.)
- Camadas e fronteiras (API, domínio, infra, persistência, clients externos)
- Principais decisões e trade-offs (procure ADRs, docs, comentários, commits)
- Estratégias de validação, erros, retries, idempotência, versionamento

### 3) Bibliotecas, frameworks e stack

- Linguagem e runtime(s)
- Frameworks e libs principais (e por quê)
- Build/test/tooling (ex.: Maven/Gradle, npm/pnpm, Poetry/pip, Go modules, etc.)
- Observabilidade (logs/metrics/traces), authn/authz, feature flags, caching

### 4) Integrações e contratos (principalmente APIs)

- **Documentação de APIs**:
  - Encontre e leia arquivos **Swagger/OpenAPI** (`openapi.*`, `swagger.*`, `*.yaml`, `*.yml`, `*.json`) e documentação correlata.
  - Extraia: base paths, autenticação, principais resources/rotas, modelos, erros, paginação, versionamento.
- Integrações externas (mensageria, filas, banco, outros serviços, webhooks)
- Contratos de entrada/saída e compatibilidade

### 5) Dados e persistência

- Bancos usados, modelos (ERD se houver), migrações
- Estratégia de transações/consistência, índices, constraints, caches

### 6) Execução e deploy

- Como rodar local, ambientes, variáveis, containers, k8s/terraform, CI/CD
- Pontos de risco operacional (start-up, migrations, jobs, dependências)

## Como produzir a Base de Conhecimento (formato)

Crie um documento (por projeto) com as seções abaixo, no máximo **objetivo e útil**:

- **Visão geral**: o que é, quem usa, objetivos e não-objetivos
- **Arquitetura**: módulos, fluxos, dependências, diagrama textual
- **Domínio/Regras de negócio**: entidades, eventos, invariantes, casos principais
- **APIs**: resumo do OpenAPI/Swagger, endpoints chave, auth, erros
- **Dados**: bancos, tabelas/coleções, migrações, consistência
- **Integrações**: entradas/saídas, filas, webhooks, clientes externos
- **Stack e tooling**: libs/frameworks, como buildar/testar/rodar
- **Operação**: observabilidade, SLOs (se existir), alertas, runbooks
- **Riscos e dívidas**: hotspots, pontos frágeis, melhorias recomendadas
- **Links e referências**: caminhos de arquivos importantes no repo

## Persistência no MCP (obrigatório)

1) Defina **um único** `service_name` representativo para **o workspace como um todo**:
   - Preferência: nome do produto/repositório/pasta raiz principal.
   - Se o workspace tiver múltiplas pastas raiz, escolha um nome agregador (ex.: `meu-produto`, `plataforma-x`, `workspace-empresa-y`).
   - Regra prática: escolha um nome que você reutilizaria para buscar esse conhecimento depois.

2) Faça **uma única** chamada para atualizar/persistir a base de conhecimento do workspace inteiro:

- Tool: **`mcp-just-seek-knowledge.update`**
- Arguments:
  - `service_name`: conforme definido acima (único para o workspace)
  - `content`: a Base de Conhecimento do **workspace inteiro**, incluindo as seções por projeto/diretório quando aplicável
  - `metadata` (opcional, recomendado):
    - `workspace_roots`: lista das pastas raiz analisadas
    - `sources`: lista curta de arquivos/diretórios usados (ex.: `README.md`, `docs/openapi.yaml`, `context/`)
    - `tech_stack`: lista resumida de tecnologias detectadas

## Saída final esperada

- Uma chamada de `update` contendo uma base de conhecimento completa e reutilizável para o **workspace inteiro**.
