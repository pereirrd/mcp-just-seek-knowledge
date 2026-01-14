"""Serviço de embeddings usando OpenAI."""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Serviço para criar embeddings usando OpenAI."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Inicializa o serviço de embeddings.
        
        Args:
            model: Nome do modelo de embedding (padrão: text-embedding-3-small)
            api_key: Chave API OpenAI (opcional, usa variável de ambiente se não fornecido)
        """
        self.model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada. Configure via variável de ambiente ou parâmetro.")
        
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=api_key
        )
        logger.info(f"EmbeddingService inicializado com modelo {self.model}")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Cria um embedding para um texto.
        
        Args:
            text: Texto para criar embedding
            
        Returns:
            List[float]: Vetor de embedding
            
        Raises:
            Exception: Se houver erro ao criar embedding
        """
        try:
            logger.debug(f"Criando embedding para texto de {len(text)} caracteres")
            embedding = self.embeddings.embed_query(text)
            logger.debug(f"Embedding criado com dimensão {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Erro ao criar embedding: {e}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Cria embeddings para múltiplos textos em batch (otimização).
        
        Args:
            texts: Lista de textos para criar embeddings
            
        Returns:
            List[List[float]]: Lista de vetores de embedding
            
        Raises:
            Exception: Se houver erro ao criar embeddings
        """
        try:
            logger.debug(f"Criando embeddings em batch para {len(texts)} textos")
            embeddings = self.embeddings.embed_documents(texts)
            logger.debug(f"Embeddings criados: {len(embeddings)} vetores com dimensão {len(embeddings[0]) if embeddings else 0}")
            return embeddings
        except Exception as e:
            logger.error(f"Erro ao criar embeddings em batch: {e}")
            raise
