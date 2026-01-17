"""Servidor MCP (Model Context Protocol) para integração com Cursor."""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..services.ingest_service import IngestService
from ..services.update_service import UpdateService
from ..services.search_service import SearchService

# Logger será configurado no entry point (mcp_server.py)
logger = logging.getLogger(__name__)

# Caminho para diretório de prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"


class MCPServer:
    """Servidor MCP que implementa protocolo JSON-RPC 2.0 via stdio."""
    
    def __init__(self):
        """Inicializa o servidor MCP e seus serviços."""
        self.ingest_service = IngestService()
        self.update_service = UpdateService()
        self.search_service = SearchService()
        logger.info("MCPServer inicializado")
    
    def _send_response(self, response: Dict[str, Any]) -> None:
        """
        Envia resposta JSON no stdout.
        
        Args:
            response: Dicionário com resposta JSON-RPC
        """
        json_str = json.dumps(response, ensure_ascii=False)
        print(json_str, flush=True)
        logger.debug(f"Resposta enviada: {json_str[:100]}...")
    
    def _error_response(self, request_id: Optional[Any], code: int, message: str, data: Optional[Any] = None) -> None:
        """
        Envia resposta de erro JSON-RPC.
        
        Args:
            request_id: ID da requisição
            code: Código de erro JSON-RPC
            message: Mensagem de erro
            data: Dados adicionais do erro (opcional)
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        if data is not None:
            response["error"]["data"] = data
        self._send_response(response)
    
    def handle_initialize(self, request_id: Optional[Any]) -> None:
        """
        Handshake inicial do protocolo MCP.
        
        Args:
            request_id: ID da requisição
        """
        logger.info("Handshake inicial do MCP")
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mcp-just-seek-knowledge",
                    "version": "1.0.0"
                }
            }
        }
        self._send_response(response)
    
    def _load_tool_definition(self, tool_name: str) -> Dict[str, Any]:
        """
        Carrega definição de uma tool a partir de arquivo JSON.
        
        Args:
            tool_name: Nome da tool (ex: 'ingest', 'update', 'search')
            
        Returns:
            Dict com definição da tool
            
        Raises:
            FileNotFoundError: Se arquivo não existir
            json.JSONDecodeError: Se arquivo JSON for inválido
        """
        tool_file = PROMPTS_DIR / f"{tool_name}.json"
        if not tool_file.exists():
            raise FileNotFoundError(f"Arquivo de definição da tool '{tool_name}' não encontrado: {tool_file}")
        
        with open(tool_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def handle_tools_list(self, request_id: Optional[Any]) -> None:
        """
        Lista todas as ferramentas disponíveis.
        
        Args:
            request_id: ID da requisição
        """
        logger.info("Listando ferramentas disponíveis")
        
        # Lista de tools disponíveis
        tool_names = ["ingest", "update", "search"]
        
        # Carregar definições das tools dos arquivos JSON
        tools = []
        for tool_name in tool_names:
            try:
                tool_def = self._load_tool_definition(tool_name)
                tools.append(tool_def)
                logger.debug(f"Tool '{tool_name}' carregada de {PROMPTS_DIR / f'{tool_name}.json'}")
            except Exception as e:
                logger.error(f"Erro ao carregar definição da tool '{tool_name}': {e}", exc_info=True)
                # Continuar mesmo se uma tool falhar
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        self._send_response(response)
    
    def handle_tool_call(self, request_id: Optional[Any], params: Dict[str, Any]) -> None:
        """
        Processa chamada de ferramenta.
        
        Args:
            request_id: ID da requisição
            params: Parâmetros da requisição contendo 'name' e 'arguments'
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Chamada de ferramenta: {tool_name} com argumentos: {list(arguments.keys())}")
        
        try:
            if tool_name == "ingest":
                result = self._handle_ingest(arguments)
            elif tool_name == "update":
                result = self._handle_update(arguments)
            elif tool_name == "search":
                result = self._handle_search(arguments)
            else:
                self._error_response(request_id, -32601, f"Ferramenta não encontrada: {tool_name}")
                return
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }
            self._send_response(response)
        
        except Exception as e:
            logger.error(f"Erro ao processar ferramenta {tool_name}: {e}", exc_info=True)
            self._error_response(request_id, -32603, f"Erro interno: {str(e)}")
    
    def _handle_ingest(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handler para tool ingest.
        
        Args:
            arguments: Argumentos da tool
            
        Returns:
            Resultado da ingestão
        """
        service_name = arguments.get("service_name")
        content = arguments.get("content")
        metadata = arguments.get("metadata")
        
        if not service_name:
            raise ValueError("service_name é obrigatório")
        if not content:
            raise ValueError("content é obrigatório")
        
        return self.ingest_service.ingest(
            service_name=service_name,
            content=content,
            metadata=metadata
        )
    
    def _handle_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handler para tool update.
        
        Args:
            arguments: Argumentos da tool
            
        Returns:
            Resultado da atualização
        """
        service_name = arguments.get("service_name")
        content = arguments.get("content")
        metadata = arguments.get("metadata")
        
        if not service_name:
            raise ValueError("service_name é obrigatório")
        if not content:
            raise ValueError("content é obrigatório")
        
        return self.update_service.update(
            service_name=service_name,
            content=content,
            metadata=metadata
        )
    
    def _handle_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handler para tool search.
        
        Args:
            arguments: Argumentos da tool
            
        Returns:
            Resultado da busca
        """
        query = arguments.get("query")
        k = arguments.get("k", 10)
        service_name = arguments.get("service_name")
        threshold = arguments.get("threshold")
        
        if not query:
            raise ValueError("query é obrigatória")
        
        return self.search_service.search(
            query=query,
            k=k,
            threshold=threshold,
            service_name=service_name
        )
    
    def run(self) -> None:
        """Loop principal do servidor MCP lendo do stdin."""
        logger.info("Servidor MCP iniciado. Aguardando requisições...")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    logger.debug(f"Requisição recebida: {request.get('method')}")
                    
                    method = request.get("method")
                    request_id = request.get("id")
                    params = request.get("params", {})
                    
                    # Notificações (sem id) não requerem resposta
                    if method and request_id is not None:
                        if method == "initialize":
                            self.handle_initialize(request_id)
                        elif method == "tools/list":
                            self.handle_tools_list(request_id)
                        elif method == "tools/call":
                            self.handle_tool_call(request_id, params)
                        else:
                            self._error_response(request_id, -32601, f"Método não encontrado: {method}")
                    elif method:
                        # Notificação sem id - apenas logar, não enviar resposta
                        logger.debug(f"Notificação recebida (sem id): {method}")
                    else:
                        # Requisição sem method - enviar erro
                        self._error_response(request_id, -32600, "Invalid Request: missing method")
                
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    # Para erros de parse, o id deve ser null conforme JSON-RPC 2.0
                    self._error_response(None, -32700, "Parse error", str(e))
                except Exception as e:
                    logger.error(f"Erro ao processar requisição: {e}", exc_info=True)
                    request_id = request.get("id") if 'request' in locals() else None
                    self._error_response(request_id, -32603, "Internal error", str(e))
        
        except KeyboardInterrupt:
            logger.info("Servidor MCP interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro fatal no servidor: {e}", exc_info=True)
