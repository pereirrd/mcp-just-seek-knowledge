"""Entry point do servidor MCP."""

import sys
import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv

from .database.connection import initialize_database
from .mcp.mcp_server import MCPServer

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging a partir de arquivo INI
# Criar diretório log se não existir
log_dir = Path(__file__).parent.parent / "log"
log_dir.mkdir(exist_ok=True)

# Carregar configuração de logging do arquivo INI (formato nativo do Python)
config_file = Path(__file__).parent.parent / "logging.ini"
if config_file.exists():
    logging.config.fileConfig(config_file, disable_existing_loggers=False)
else:
    # Fallback se arquivo não existir
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

logger = logging.getLogger(__name__)


def main() -> None:
    """Função principal para inicializar e executar o servidor MCP."""
    try:
        logger.info("Inicializando servidor MCP...")
        
        # Inicializar banco de dados (criar schema se necessário)
        logger.info("Inicializando banco de dados...")
        initialize_database()
        
        # Criar e iniciar servidor MCP
        logger.info("Criando servidor MCP...")
        server = MCPServer()
        
        logger.info("Servidor MCP pronto. Iniciando loop principal...")
        server.run()
    
    except KeyboardInterrupt:
        logger.info("Servidor MCP interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal ao iniciar servidor MCP: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
