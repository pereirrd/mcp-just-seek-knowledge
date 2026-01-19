#!/usr/bin/env python3
"""
Script CLI para excluir um registro pelo service_name.

Uso:
    python src/database/delete_service.py <service_name>

Exemplo:
    python src/database/delete_service.py user-service
"""

import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos quando executado diretamente
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database.repository import KnowledgeRepository

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def delete_service(service_name: str) -> bool:
    """
    Exclui um registro pelo service_name.
    
    Args:
        service_name: Nome do serviço a ser excluído
        
    Returns:
        bool: True se excluído com sucesso, False caso contrário
    """
    try:
        repository = KnowledgeRepository()
        deleted = repository.delete(service_name)
        
        if deleted:
            print(f"✓ Registro excluído com sucesso: '{service_name}'")
            return True
        else:
            print(f"✗ Registro não encontrado: '{service_name}'")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao excluir registro: {e}", exc_info=True)
        print(f"✗ Erro ao excluir registro: {e}")
        return False


def main():
    """Função principal do script CLI."""
    if len(sys.argv) < 2:
        print("Uso: python src/database/delete_service.py <service_name>")
        print("\nExemplo:")
        print("  python src/database/delete_service.py user-service")
        sys.exit(1)
    
    service_name = sys.argv[1].strip()
    
    if not service_name:
        print("✗ Erro: service_name não pode ser vazio")
        sys.exit(1)
    
    print(f"Tentando excluir registro com service_name: '{service_name}'...")
    success = delete_service(service_name)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
