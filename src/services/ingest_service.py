"""Serviço de ingest para adicionar conhecimento na base de dados."""

import logging
from typing import Dict, Any, Optional

from ..database.repository import KnowledgeRepository
from ..embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class IngestService:
    """Serviço para ingerir conhecimento na base de dados."""
    
    def __init__(
        self,
        repository: Optional[KnowledgeRepository] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Inicializa o serviço de ingest.
        
        Args:
            repository: Repositório de dados (opcional, cria novo se não fornecido)
            embedding_service: Serviço de embeddings (opcional, cria novo se não fornecido)
        """
        self.repository = repository or KnowledgeRepository()
        self.embedding_service = embedding_service or EmbeddingService()
        logger.info("IngestService inicializado")
    
    def ingest(
        self,
        service_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingera conhecimento na base de dados.
        
        Args:
            service_name: Nome do serviço (obrigatório, único)
            content: Conteúdo do conhecimento
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Dict com resultado da operação:
                - success: bool
                - message: str
                - id: int (ID do registro inserido, se sucesso)
                
        Raises:
            ValueError: Se service_name ou content estiverem vazios
            psycopg.IntegrityError: Se service_name já existir
        """
        # Validação de dados de entrada
        if not service_name or not service_name.strip():
            error_msg = "service_name não pode estar vazio"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not content or not content.strip():
            error_msg = "content não pode estar vazio"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            logger.info(f"Iniciando ingest para service_name: '{service_name}'")
            
            # Criar embedding do conteúdo
            logger.debug(f"Criando embedding para conteúdo de {len(content)} caracteres")
            embedding = self.embedding_service.create_embedding(content)
            logger.debug(f"Embedding criado com dimensão {len(embedding)}")
            
            # Inserir no banco de dados
            record_id = self.repository.insert(
                service_name=service_name.strip(),
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
            logger.info(f"Ingest concluído com sucesso para service_name: '{service_name}' (ID: {record_id})")
            
            return {
                "success": True,
                "message": f"Conhecimento ingerido com sucesso para service_name: '{service_name}'",
                "id": record_id,
                "service_name": service_name
            }
        
        except Exception as e:
            error_msg = f"Erro ao ingerir conhecimento: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "error": str(e)
            }
