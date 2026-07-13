# app/mcp_client.py
# Conecta ao(s) servidor(es) MCP e devolve as ferramentas como tools LangChain.

import asyncio
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient


# Mapa de servidores MCP. Cada um diz como ser lançado.
# Aqui, lançamos nosso próprio servidor via stdio (mesmo Python do projeto).
SERVIDORES = {
    "empresa": {
        "command": sys.executable,          # o python atual
        "args": ["-m", "app.mcp_server"],     # roda app/mcp_server.py
        "transport": "stdio",
    }
}


async def _carregar_tools_async():
    client = MultiServerMCPClient(SERVIDORES)
    # get_tools faz a descoberta: pergunta ao servidor quais ferramentas existem.
    return await client.get_tools()


def carregar_tools_mcp():
    """Carrega as tools MCP de forma síncrona (chamado uma vez, no boot)."""
    try:
        return asyncio.run(_carregar_tools_async())
    except Exception as e:
        # Se o servidor MCP não subir, seguimos sem as tools externas.
        print(f"[MCP] não foi possível carregar tools: {e}")
        return []
