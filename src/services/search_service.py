"""Serviço de search para buscar conhecimento na base de dados."""

import logging
from typing import List, Dict, Any, Optional

from ..database.repository import KnowledgeRepository
from ..embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SearchService:
    """Serviço para buscar conhecimento na base de dados usando busca semântica."""
    
    def __init__(
        self,
        repository: Optional[KnowledgeRepository] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Inicializa o serviço de search.
        
        Args:
            repository: Repositório de dados (opcional, cria novo se não fornecido)
            embedding_service: Serviço de embeddings (opcional, cria novo se não fornecido)
        """
        self.repository = repository or KnowledgeRepository()
        self.embedding_service = embedding_service or EmbeddingService()
        logger.info("SearchService inicializado")
    
    def search(
        self,
        query: str,
        k: int = 10,
        threshold: Optional[float] = None,
        service_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca conhecimento usando busca semântica.
        
        Args:
            query: Texto de busca
            k: Número de resultados (padrão: 10)
            threshold: Threshold mínimo de similaridade (opcional, 0.0 a 1.0)
            service_name: Filtrar por service_name específico (opcional)
            
        Returns:
            Dict com resultado da busca:
                - success: bool
                - results: List[Dict] com documentos encontrados
                - count: int (número de resultados)
                - query: str (query original)
                
        Raises:
            ValueError: Se query estiver vazia ou parâmetros inválidos
        """
        # Validação de dados de entrada
        if not query or not query.strip():
            error_msg = "query não pode estar vazia"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if k < 1:
            error_msg = f"k deve ser maior que 0 (recebido: {k})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if threshold is not None and (threshold < 0.0 or threshold > 1.0):
            error_msg = f"threshold deve estar entre 0.0 e 1.0 (recebido: {threshold})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            query_clean = query.strip()
            logger.info(f"Iniciando busca semântica: query='{query_clean[:50]}...', k={k}, threshold={threshold}, service_name={service_name}")
            
            # Criar embedding da query
            logger.debug(f"Criando embedding para query de {len(query_clean)} caracteres")
            query_embedding = self.embedding_service.create_embedding(query_clean)
            logger.debug(f"Embedding da query criado com dimensão {len(query_embedding)}")
            
            # Buscar documentos similares no banco
            results = self.repository.similarity_search(
                query_embedding=query_embedding,
                k=k,
                threshold=threshold,
                service_name_filter=service_name
            )
            
            # Formatar resultados
            formatted_results = []
            for doc, similarity_score in results:
                formatted_result = {
                    "id": doc["id"],
                    "service_name": doc["service_name"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "similarity": round(similarity_score, 4),
                    "created_at": doc["created_at"].isoformat() if doc["created_at"] else None,
                    "updated_at": doc["updated_at"].isoformat() if doc["updated_at"] else None
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Busca concluída: {len(formatted_results)} resultados encontrados")
            
            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "query": query_clean
            }
        
        except Exception as e:
            error_msg = f"Erro ao buscar conhecimento: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "error": str(e),
                "results": [],
                "count": 0,
                "query": query.strip() if query else ""
            }
