"""Entry point do servidor MCP."""

import sys
from pathlib import Path

# Adicionar diretório do projeto ao path para permitir imports absolutos quando executado diretamente
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import logging
import logging.config
from dotenv import load_dotenv

# Usar imports absolutos do pacote src para funcionar quando executado diretamente
from src.database.connection import initialize_database
from src.mcp.mcp_server import MCPServer

# Carregar variáveis de ambiente do arquivo .env no diretório raiz do projeto
env_file = parent_dir / ".env"
load_dotenv(env_file)

# Configurar logging a partir de arquivo INI
# Criar diretório log se não existir (deve ser criado antes do fileConfig)
log_dir = parent_dir / "log"
log_dir.mkdir(parents=True, exist_ok=True)

# Carregar configuração de logging do arquivo INI
config_file = parent_dir / "logging.ini"
if config_file.exists():
    import os
    original_cwd = os.getcwd()
    try:
        # Mudar temporariamente para o diretório do projeto para resolver caminhos relativos no INI
        os.chdir(parent_dir)
        logging.config.fileConfig(config_file, disable_existing_loggers=False)
    finally:
        os.chdir(original_cwd)
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
