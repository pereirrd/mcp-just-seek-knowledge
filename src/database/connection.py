"""Gerenciamento de conexão com PostgreSQL."""

import os
import logging
from typing import Optional
import psycopg
from dotenv import load_dotenv

from .schema import CREATE_SCHEMA_SQL

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)


def get_connection_string() -> str:
    """
    Obtém a string de conexão PostgreSQL das variáveis de ambiente.
    
    Returns:
        str: String de conexão PostgreSQL
    """
    pgvector_url = os.getenv("PGVECTOR_URL")
    if not pgvector_url:
        # Construir a partir de variáveis individuais se PGVECTOR_URL não estiver definida
        postgres_db = os.getenv("POSTGRES_DB", "java_api_knowledge")
        postgres_user = os.getenv("POSTGRES_USER", "postgres")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        
        pgvector_url = (
            f"postgresql://{postgres_user}:{postgres_password}@"
            f"{postgres_host}:{postgres_port}/{postgres_db}"
        )
    
    return pgvector_url


def create_connection() -> psycopg.Connection:
    """
    Cria uma conexão com PostgreSQL.
    
    Returns:
        psycopg.Connection: Conexão PostgreSQL
        
    Raises:
        psycopg.Error: Se houver erro na conexão
    """
    connection_string = get_connection_string()
    logger.debug(f"Conectando ao PostgreSQL: {connection_string.split('@')[1] if '@' in connection_string else '***'}")
    
    try:
        conn = psycopg.connect(connection_string)
        logger.info("Conexão com PostgreSQL estabelecida com sucesso")
        return conn
    except psycopg.Error as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise


def schema_exists(conn: psycopg.Connection) -> bool:
    """
    Verifica se a tabela java_api_knowledge existe.
    
    Args:
        conn: Conexão PostgreSQL
        
    Returns:
        bool: True se a tabela existe, False caso contrário
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'java_api_knowledge'
                );
            """)
            exists = cur.fetchone()[0]
            logger.debug(f"Tabela java_api_knowledge existe: {exists}")
            return exists
    except psycopg.Error as e:
        logger.error(f"Erro ao verificar se schema existe: {e}")
        raise


def create_schema(conn: Optional[psycopg.Connection] = None) -> None:
    """
    Cria o schema do banco de dados (tabela, índices e triggers).
    
    Args:
        conn: Conexão PostgreSQL (opcional, cria nova se não fornecido)
        
    Raises:
        psycopg.Error: Se houver erro ao criar schema
    """
    should_close = False
    if conn is None:
        conn = create_connection()
        should_close = True
    
    try:
        logger.info("Criando schema do banco de dados...")
        
        with conn.cursor() as cur:
            # Executar script completo de criação
            cur.execute(CREATE_SCHEMA_SQL)
            conn.commit()
        
        logger.info("Schema criado com sucesso")
    except psycopg.Error as e:
        logger.error(f"Erro ao criar schema: {e}")
        conn.rollback()
        raise
    finally:
        if should_close:
            conn.close()


def initialize_database() -> None:
    """
    Inicializa o banco de dados: cria conexão, verifica se schema existe
    e cria se necessário.
    
    Raises:
        psycopg.Error: Se houver erro na inicialização
    """
    conn = None
    try:
        conn = create_connection()
        
        if not schema_exists(conn):
            logger.info("Schema não existe. Criando...")
            create_schema(conn)
        else:
            logger.info("Schema já existe")
    except psycopg.Error as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()
