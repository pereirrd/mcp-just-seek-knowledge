[English](README.md) | [Português](README.pt-br.md)

# mcp-just-seek-knowledge

Servidor MCP (Model Context Protocol) que almacena y busca conocimiento generado por IA sobre proyectos de software, permitiendo a Cursor acceder a información sobre estructuras de proyectos, patrones de diseño, mejores prácticas y documentación técnica.

---

## 📋 Sobre el Proyecto

### Objetivo

Crear un servidor MCP que almacena y busca conocimiento generado por IA sobre proyectos de software.

### Stack Tecnológico

- **Lenguaje**: Python
- **Framework para Embeddings**: LangChain
- **Base de Datos**: PostgreSQL con pgVector
- **Protocolo**: MCP (Model Context Protocol) para integración con Cursor

### Funcionalidades Principales

1. **Ingest**: Crear nuevos registros en la base de conocimiento
2. **Update**: Actualizar registros existentes en la base de conocimiento
3. **Search**: Buscar conocimiento semántico en la base
4. **List Catalog**: Listar todos los `service_name` existentes en la base (expuesta como tool del MCP)
5. **Delete**: Eliminar registros por `service_name` (disponible vía script CLI, no expuesta como tool del MCP)

---

## 🛠️ Configuración del Entorno

### Proceso Completo de Configuración

#### 1. Clona el proyecto o navega hasta él (si es necesario)

```bash
cd /home/pereirrd/dev/git/pereirrd/mcp-just-seek-knowledge
```

#### 2. Crea y activa el entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/WSL:
source venv/bin/activate

# En Windows:
# venv\Scripts\activate
```

#### 3. Instala dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configura variables de entorno

Crea un archivo `.env` en la raíz del proyecto (copia de `.env.example` si existe, o créalo manualmente):

```bash
# Ejemplo de .env
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5433/software_design_knowledge
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=software_design_knowledge
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
OPENAI_API_KEY=tu_clave_api_openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**Nota:** Las variables de PostgreSQL también pueden configurarse en el `mcp.json` de Cursor (ver sección abajo).

#### 5. Inicia PostgreSQL (si usas Docker Compose)

```bash
docker-compose up -d
```

Esto creará PostgreSQL con pgvector automáticamente en el puerto `5433`.

**Importante:** Si el puerto `5432` ya está en uso, el `docker-compose.yml` está configurado para usar el puerto `5433` automáticamente.

#### 6. Prueba el servidor MCP (opcional)

```bash
python src/mcp_server.py
```

El servidor debe iniciar sin errores y crear automáticamente la tabla `software_design_knowledge` si no existe.

### Verificar Instalación

Para verificar si las dependencias fueron instaladas correctamente:

```bash
pip list | grep -E "langchain|psycopg|openai|python-dotenv"
```

O prueba los imports directamente:

```bash
python -c "from src.database.connection import get_connection_string; from src.mcp.mcp_server import MCPServer; print('✅ Dependencias instaladas correctamente!')"
```

---

## ⚙️ Configuración en Cursor

Para agregar este servidor MCP en Cursor, configura el archivo `~/.cursor/mcp.json` (configuración global) o `.cursor/mcp.json` en la raíz del proyecto (configuración local).

### Ejemplo de configuración (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/ruta/absoluta/al/proyecto/src/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "tu_clave_api_openai",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Importante:**
- Usa rutas absolutas en el campo `args`
- Configura todas las variables de entorno necesarias
- Cursor carga este archivo automáticamente al iniciar
- Después de agregar, reinicia Cursor para cargar el servidor MCP

### Nota sobre Cursor

Al configurar el MCP en Cursor (`~/.cursor/mcp.json`), Cursor usará el Python del sistema o el activo en PATH. Recomendaciones:

#### Opción 1: Usar el Python global (instalar dependencias globalmente)

Si prefieres usar el Python global del sistema:

```bash
pip install -r requirements.txt
```

Y configura el `mcp.json` con:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "python",
      "args": ["/ruta/absoluta/al/proyecto/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

#### Opción 2: Usar el Python del entorno virtual (recomendado)

Para usar el entorno virtual del proyecto, especifica la ruta completa del Python del venv en `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-just-seek-knowledge": {
      "command": "/ruta/absoluta/a/mcp-just-seek-knowledge/venv/bin/python",
      "args": ["/ruta/absoluta/a/mcp-just-seek-knowledge/src/mcp_server.py"],
      "env": {
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "EMBEDDING_DIMENSION": "1536"
      }
    }
  }
}
```

**Ventajas de la Opción 2:**
- Aísla las dependencias del proyecto
- Evita conflictos con otros proyectos Python
- Facilita la gestión de versiones

**Nota:** El archivo `.env` del proyecto será cargado automáticamente por el servidor MCP, así que no necesitas repetir las variables de PostgreSQL en `mcp.json` (a menos que prefieras).

---

## 🚀 Implementación

### Preparación y Estructura

#### Estructura de Directorios

Creada estructura `src/` con subdirectorios organizados:

- `src/database/` - Gestión de base de datos
- `src/embeddings/` - Servicios de embeddings
- `src/services/` - Servicios de negocio (ingest, update, search)
- `src/mcp/` - Servidor MCP y handlers

Archivos `__init__.py` creados en todos los paquetes Python.

#### Configuración de Dependencias

Archivo `requirements.txt` creado con todas las dependencias necesarias:

- **LangChain Framework**: langchain, langchain-community, langchain-core, langchain-openai, langchain-postgres
- **PostgreSQL**: psycopg, pgvector
- **OpenAI**: openai
- **Utilidades**: python-dotenv

#### Variables de Entorno

Archivo `.env.example` creado con todas las variables necesarias:

- `PGVECTOR_URL` - URL de conexión PostgreSQL
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL`
- `EMBEDDING_DIMENSION`

Archivo `.gitignore` configurado para excluir `.env` y archivos Python y de IDE.

#### Docker y PostgreSQL

Archivo `docker-compose.yml` creado con:

- Servicio PostgreSQL usando imagen `pgvector/pgvector:pg16`
- Configuración de volúmenes para persistencia
- Healthcheck configurado
- Puertos y variables de entorno configuradas

Script de inicialización `init-scripts/01-init-pgvector.sh` para crear la extensión pgvector automáticamente.

---

### Configuración de la Base de Datos

#### Schema de la Base (`src/database/schema.py`)

**Estructura de la tabla `software_design_knowledge` (conocimiento de proyectos de software):**

- `id` - Identificador único (SERIAL PRIMARY KEY)
- `service_name` - Nombre del servicio (VARCHAR(255) NOT NULL UNIQUE)
- `content` - Contenido del conocimiento (TEXT NOT NULL)
- `embedding` - Vector de embedding (vector(1536) NOT NULL)
- `metadata` - Metadatos adicionales (JSONB)
- `created_at` - Fecha de creación (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `updated_at` - Fecha de actualización (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

**Índices:**

- Índice IVFFlat para búsqueda vectorial optimizada
- Índice para `service_name` para búsquedas por servicio

**Triggers:**

- Trigger automático para actualizar `updated_at` en actualizaciones

#### Gestión de Conexión (`src/database/connection.py`)

Funciones implementadas:

- `get_connection_string()` - Obtiene string de conexión de las variables de entorno
- `create_connection()` - Crea conexiones PostgreSQL
- `schema_exists()` - Verifica si la tabla existe
- `create_schema()` - Crea schema completo (tabla, índices, triggers)
- `initialize_database()` - Inicializa la base de datos

Manejo de errores y logging implementados.

#### Repositorio de Datos (`src/database/repository.py`)

**Clase `KnowledgeRepository`** implementada usando `psycopg` directamente.

**Métodos implementados:**

- `insert()` - Insertar documento en la base
- `update()` - Actualizar documento por service_name
- `upsert()` - Insertar o actualizar (comportamiento upsert)
- `delete()` - Eliminar documento por service_name
- `get_by_service_name()` - Buscar documento por service_name
- `similarity_search()` - Búsqueda semántica usando pgVector (operador `<=>`)

**Funcionalidades:**

- Soporte a filtros opcionales (threshold de similitud, filtro por service_name)
- Integración con estructura de metadatos JSONB


---

### Servicios de Embeddings

**Clase `EmbeddingService`** (`src/embeddings/embedding_service.py`) usando `OpenAIEmbeddings` de LangChain.

**Funcionalidades:**
- Creación de embedding único y en batch
- Configuración vía variables de entorno (modelo por defecto: `text-embedding-3-small`)
- Manejo de errores y logging

---

### Servicios de Negocio

**Cuatro servicios principales implementados:**

#### Ingest Service (`src/services/ingest_service.py`)
- Agrega nuevo conocimiento a la base
- Valida `service_name` y `content`
- Crea embedding automáticamente
- Manejo de errores completo

#### Update Service (`src/services/update_service.py`)
- Actualiza conocimiento existente (comportamiento upsert)
- Si `service_name` no existe, crea nuevo registro
- Si existe, actualiza el registro existente
- Actualiza embedding automáticamente

#### Search Service (`src/services/search_service.py`)
- Búsqueda semántica por similitud
- Parámetros opcionales: `k` (número de resultados), `threshold` (similitud mínima), `service_name` (filtro)
- Retorna resultados ordenados por relevancia

#### List Catalog Service (`src/services/list_catalog_service.py`)
- Lista todos los `service_name` existentes en la base
- No utiliza embeddings (solo repositorio)

**Funcionalidades comunes:**
- Integración con `EmbeddingService` y `KnowledgeRepository`
- Validación de entrada
- Manejo de errores
- Logging detallado
- Retornos estructurados

---

## 🗑️ Scripts CLI

### Eliminación de Registros

El proyecto incluye un script CLI para eliminación de registros que **no está expuesto como tool del MCP**. Esta funcionalidad está disponible solo vía línea de comandos para operaciones administrativas.

#### Script: `src/database/delete_service.py`

**Funcionalidad:**
- Elimina un registro de la base de conocimiento por `service_name`
- Valida la existencia del registro antes de eliminar
- Proporciona feedback claro sobre el resultado de la operación

**Uso:**

```bash
python src/database/delete_service.py <service_name>
```

**Ejemplos:**

```bash
# Eliminar un servicio específico
python src/database/delete_service.py user-service

# El script retorna:
# - ✓ "Registro eliminado con éxito" si el registro fue encontrado y removido
# - ✗ "Registro no encontrado" si el service_name no existe
# - ✗ "Error al eliminar registro" en caso de falla en la operación
```

**Características:**
- Validación de parámetros (service_name no puede estar vacío)
- Manejo de errores con logging detallado
- Códigos de salida apropiados (0 para éxito, 1 para falla)
- Mensajes claros de feedback para el usuario

**Nota:** Esta funcionalidad no está disponible como tool del MCP por motivos de seguridad y control de acceso. Usa solo para operaciones administrativas necesarias.

---

## 📚 Script de Inicialización de pgvector

El script `init-scripts/01-init-pgvector.sh` es usado automáticamente por PostgreSQL durante la inicialización del contenedor.

### Cómo funciona

**1. Volumen mapeado en docker-compose.yml**

El directorio local `init-scripts/` es mapeado a `/docker-entrypoint-initdb.d` dentro del contenedor a través de la configuración de volumen en docker-compose.yml.

**2. Comportamiento automático de PostgreSQL**

La imagen oficial de PostgreSQL (incluyendo pgvector/pgvector) ejecuta automáticamente todos los archivos presentes en `/docker-entrypoint-initdb.d` cuando:

- La base de datos es inicializada por primera vez (cuando el volumen de datos está vacío)
- Los archivos son ejecutados en orden alfabético (por eso el prefijo 01-)
- Acepta archivos .sql, .sh y otros ejecutables

**3. Qué hace el script**

El script `01-init-pgvector.sh`:

- Ejecuta `CREATE EXTENSION IF NOT EXISTS vector;` para crear la extensión pgvector
- Lista las extensiones instaladas para verificación
- Usa `set -e` para parar en caso de error

### Importante

- Los scripts en `init-scripts/` solo se ejecutan en la primera inicialización (cuando el volumen está vacío)
- Si el contenedor ya fue iniciado antes, el script no se ejecutará nuevamente
- Para reejecutar, es necesario remover el volumen: `docker-compose down -v`

---

## ⌨️ Comandos de Cursor (Slash Commands)

Este repositorio incluye comandos personalizados de Cursor en `.cursor/commands/`, que ayudan a **crear, actualizar y listar** la base de conocimiento en el MCP `mcp-just-seek-knowledge`.

### Comandos disponibles

- **`/criar_base_conhecimento`**: analiza todo el workspace abierto (todos los proyectos/directorios), lee documentación (incluyendo Swagger/OpenAPI) y **crea** un registro único para el workspace usando `mcp-just-seek-knowledge.ingest`.
- **`/atualizar_base_conhecimento`**: mismo análisis del comando anterior, pero **actualiza** (upsert) el registro del workspace usando `mcp-just-seek-knowledge.update`.
- **`/listar_base_conhecimento`**: lista los `service_name` existentes vía `mcp-just-seek-knowledge.list_catalog` y presenta un layout amigable con `count`, `service_name` y `metadata` (enriqueciendo vía `mcp-just-seek-knowledge.search`).

### Cómo usar

1. Asegúrate de que el MCP `mcp-just-seek-knowledge` esté configurado en Cursor (`~/.cursor/mcp.json` o `.cursor/mcp.json`).
2. Abre el(los) proyecto(s) en el workspace de Cursor.
3. En el chat de Cursor, ejecuta un comando escribiendo:
   - `/criar_base_conhecimento`
   - `/atualizar_base_conhecimento`
   - `/listar_base_conhecimento`
