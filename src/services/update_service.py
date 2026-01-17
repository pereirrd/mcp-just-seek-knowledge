"""Serviço de update para atualizar conhecimento na base de dados."""

import logging
from typing import Dict, Any, Optional

from ..database.repository import KnowledgeRepository
from ..embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class UpdateService:
    """Serviço para atualizar conhecimento na base de dados (comportamento upsert)."""
    
    def __init__(
        self,
        repository: Optional[KnowledgeRepository] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Inicializa o serviço de update.
        
        Args:
            repository: Repositório de dados (opcional, cria novo se não fornecido)
            embedding_service: Serviço de embeddings (opcional, cria novo se não fornecido)
        """
        self.repository = repository or KnowledgeRepository()
        self.embedding_service = embedding_service or EmbeddingService()
        logger.info("UpdateService inicializado")
    
    def update(
        self,
        service_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Atualiza conhecimento na base de dados (comportamento upsert).
        
        Se service_name não existe, cria novo registro.
        Se service_name existe, atualiza o registro existente.
        
        Args:
            service_name: Nome do serviço (obrigatório)
            content: Novo conteúdo do conhecimento
            metadata: Metadados atualizados (opcional)
            
        Returns:
            Dict com resultado da operação:
                - success: bool
                - message: str
                - id: int (ID do registro)
                - created: bool (True se criado, False se atualizado)
                
        Raises:
            ValueError: Se service_name ou content estiverem vazios
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
            service_name_clean = service_name.strip()
            logger.info(f"Iniciando update para service_name: '{service_name_clean}'")
            
            # Verificar se service_name existe
            existing_doc = self.repository.get_by_service_name(service_name_clean)
            is_new = existing_doc is None
            
            if is_new:
                logger.debug(f"Service_name '{service_name_clean}' não existe. Criando novo registro.")
            else:
                logger.debug(f"Service_name '{service_name_clean}' existe. Atualizando registro (ID: {existing_doc['id']}).")
            
            # Criar novo embedding do conteúdo atualizado
            logger.debug(f"Criando embedding para conteúdo de {len(content)} caracteres")
            embedding = self.embedding_service.create_embedding(content)
            logger.debug(f"Embedding criado com dimensão {len(embedding)}")
            
            # Fazer upsert (insert ou update)
            record_id = self.repository.upsert(
                service_name=service_name_clean,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
            action = "criado" if is_new else "atualizado"
            logger.info(f"Update concluído com sucesso para service_name: '{service_name_clean}' - registro {action} (ID: {record_id})")
            
            return {
                "success": True,
                "message": f"Conhecimento {action} com sucesso para service_name: '{service_name_clean}'",
                "id": record_id,
                "service_name": service_name_clean,
                "created": is_new
            }
        
        except Exception as e:
            error_msg = f"Erro ao atualizar conhecimento: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "error": str(e)
            }
