"""Repositório de dados usando PostgreSQL com pgVector."""

import logging
from typing import List, Optional, Dict, Any, Tuple
import psycopg
from psycopg.types.json import Jsonb

from .connection import create_connection, get_connection_string

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Repositório para gerenciar conhecimento Java API no PostgreSQL com pgVector."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Inicializa o repositório.
        
        Args:
            connection_string: String de conexão PostgreSQL (opcional, usa variáveis de ambiente se não fornecido)
        """
        self.connection_string = connection_string or get_connection_string()
        logger.debug("KnowledgeRepository inicializado")
    
    def _get_connection(self) -> psycopg.Connection:
        """
        Cria uma conexão com o banco de dados.
        
        Returns:
            psycopg.Connection: Conexão PostgreSQL
        """
        return psycopg.connect(self.connection_string)
    
    def insert(
        self,
        service_name: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Insere um documento no banco de dados.
        
        Args:
            service_name: Nome do serviço (único)
            content: Conteúdo do conhecimento
            embedding: Vetor de embedding
            metadata: Metadados adicionais (opcional)
            
        Returns:
            int: ID do registro inserido
            
        Raises:
            psycopg.IntegrityError: Se service_name já existe
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO java_api_knowledge (service_name, content, embedding, metadata)
                    VALUES (%s, %s, %s::vector, %s)
                    RETURNING id
                """, (
                    service_name,
                    content,
                    str(embedding),
                    Jsonb(metadata) if metadata else None
                ))
                record_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Documento inserido para service_name '{service_name}' com ID {record_id}")
                return record_id
        except psycopg.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro ao inserir documento: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def update(
        self,
        service_name: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Atualiza um documento existente por service_name.
        
        Args:
            service_name: Nome do serviço
            content: Novo conteúdo
            embedding: Novo vetor de embedding
            metadata: Metadados atualizados (opcional)
            
        Returns:
            bool: True se o documento foi atualizado, False se não existe
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE java_api_knowledge
                    SET content = %s, embedding = %s::vector, metadata = %s
                    WHERE service_name = %s
                """, (
                    content,
                    str(embedding),
                    Jsonb(metadata) if metadata else None,
                    service_name
                ))
                updated = cur.rowcount > 0
                conn.commit()
                if updated:
                    logger.info(f"Documento atualizado para service_name '{service_name}'")
                else:
                    logger.warning(f"Documento não encontrado para service_name '{service_name}'")
                return updated
        except psycopg.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro ao atualizar documento: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def upsert(
        self,
        service_name: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Insere ou atualiza um documento (upsert).
        
        Args:
            service_name: Nome do serviço
            content: Conteúdo do conhecimento
            embedding: Vetor de embedding
            metadata: Metadados (opcional)
            
        Returns:
            int: ID do registro
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO java_api_knowledge (service_name, content, embedding, metadata)
                    VALUES (%s, %s, %s::vector, %s)
                    ON CONFLICT (service_name) 
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, (
                    service_name,
                    content,
                    str(embedding),
                    Jsonb(metadata) if metadata else None
                ))
                record_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Documento upserted para service_name '{service_name}' com ID {record_id}")
                return record_id
        except psycopg.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro ao fazer upsert do documento: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_by_service_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca um documento por service_name.
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Dict com dados do documento ou None se não encontrado
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, service_name, content, embedding, metadata, created_at, updated_at
                    FROM java_api_knowledge
                    WHERE service_name = %s
                """, (service_name,))
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "service_name": row[1],
                        "content": row[2],
                        "embedding": row[3],
                        "metadata": row[4],
                        "created_at": row[5],
                        "updated_at": row[6]
                    }
                return None
        except psycopg.Error as e:
            logger.error(f"Erro ao buscar documento por service_name: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 10,
        threshold: Optional[float] = None,
        service_name_filter: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Busca documentos similares usando similaridade vetorial.
        
        Args:
            query_embedding: Vetor de embedding da query
            k: Número de resultados (padrão: 10)
            threshold: Threshold mínimo de similaridade (opcional)
            service_name_filter: Filtrar por service_name (opcional)
            
        Returns:
            Lista de tuplas (documento, score de similaridade)
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Construir query com filtros opcionais
                where_clauses = []
                params = [str(query_embedding), str(query_embedding), k]
                
                if service_name_filter:
                    where_clauses.append("service_name = %s")
                    params.insert(-1, service_name_filter)
                
                where_sql = " AND ".join(where_clauses) if where_clauses else ""
                if where_sql:
                    where_sql = "WHERE " + where_sql
                
                query = f"""
                    SELECT id, service_name, content, embedding, metadata, created_at, updated_at,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM java_api_knowledge
                    {where_sql}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """
                
                cur.execute(query, params)
                results = []
                for row in cur.fetchall():
                    similarity = float(row[7])
                    
                    # Aplicar threshold se especificado
                    if threshold is not None and similarity < threshold:
                        continue
                    
                    doc = {
                        "id": row[0],
                        "service_name": row[1],
                        "content": row[2],
                        "embedding": row[3],
                        "metadata": row[4],
                        "created_at": row[5],
                        "updated_at": row[6]
                    }
                    results.append((doc, similarity))
                
                logger.debug(f"Busca semântica retornou {len(results)} resultados")
                return results
        except psycopg.Error as e:
            logger.error(f"Erro ao buscar documentos similares: {e}")
            raise
        finally:
            if conn:
                conn.close()
