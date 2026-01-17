"""Schema SQL para a tabela de conhecimento de projetos de software."""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS software_design_knowledge (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_VECTOR_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
ON software_design_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""

CREATE_SERVICE_NAME_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_knowledge_service_name 
ON software_design_knowledge (service_name);
"""

CREATE_TRIGGER_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS update_software_design_knowledge_updated_at ON software_design_knowledge;
CREATE TRIGGER update_software_design_knowledge_updated_at
BEFORE UPDATE ON software_design_knowledge
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
"""

# Script completo para criar o schema
CREATE_SCHEMA_SQL = (
    CREATE_TABLE_SQL + "\n" +
    CREATE_VECTOR_INDEX_SQL + "\n" +
    CREATE_SERVICE_NAME_INDEX_SQL + "\n" +
    CREATE_TRIGGER_FUNCTION_SQL + "\n" +
    CREATE_TRIGGER_SQL
)
