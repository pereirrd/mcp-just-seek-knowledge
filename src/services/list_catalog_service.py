"""Serviço para listar o catálogo de service_name existentes na base."""

import logging
from typing import Dict, Any, Optional

from ..database.repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class ListCatalogService:
    """Serviço para listar todos os serviços/projetos já cadastrados (service_name)."""

    def __init__(self, repository: Optional[KnowledgeRepository] = None):
        """
        Inicializa o serviço de listagem do catálogo.

        Args:
            repository: Repositório de dados (opcional, cria novo se não fornecido)
        """
        self.repository = repository or KnowledgeRepository()
        logger.info("ListCatalogService inicializado")

    def list_catalog(self) -> Dict[str, Any]:
        """
        Lista todos os service_name existentes na base.

        Returns:
            Dict com resultado da operação:
                - success: bool
                - services: List[str]
                - count: int
        """
        try:
            service_names = self.repository.list_service_names()
            return {
                "success": True,
                "services": service_names,
                "count": len(service_names),
            }
        except Exception as e:
            error_msg = f"Erro ao listar catálogo de serviços: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "error": str(e),
                "services": [],
                "count": 0,
            }

