# app/agent.py
# Ferramentas e modelo. A base simulada deu lugar ao RAG real.

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from app.rag import get_vector_store
from app.tools_externas import lookup_cep

from app.mcp_client import carregar_tools_mcp

load_dotenv()


# --- Ferramenta 1: calculadora (mantida) ---
@tool
def calculator(expression: str) -> str:
    """Avalia uma expressão aritmética simples (ex.: '3 * (4 + 2)').
    Use para cálculos exatos em vez de estimar."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"Erro ao calcular: {exc}"


# --- Ferramenta 2: recuperação REAL (RAG) no lugar da base simulada ---
# O retriever é criado sob demanda (lazy): assim o serviço sobe no Render
# sem precisar conectar ao banco no momento do import/deploy.
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_vector_store().as_retriever(search_kwargs={"k": 4})
    return _retriever


@tool
def knowledge_search(query: str) -> str:
    """Busca informações sobre políticas e conhecimento do domínio na base
    de conhecimento da empresa. Use para qualquer pergunta sobre regras,
    procedimentos ou informações institucionais."""
    try:
        docs = _get_retriever().invoke(query)
    except Exception as exc:
        return f"Erro ao consultar a base de conhecimento: {exc}"
    if not docs:
        return "Nenhuma informação encontrada na base de conhecimento."
    return "\n\n".join(doc.page_content for doc in docs)


# --- Conjunto de ferramentas e modelo ---
TOOLS = [calculator, knowledge_search, lookup_cep]

SYSTEM_PROMPT = (
    "Você é um assistente objetivo e confiável. "
    "Use 'calculator' para cálculos exatos, 'knowledge_search' para perguntas "
    "sobre políticas e informações da empresa, e 'lookup_cep' para consultar "
    "endereços a partir de um CEP. Responda com base nos resultados das ferramentas; "
    "se a busca de conhecimento não encontrar, diga que não sabe; se uma ferramenta "
    "falhar, explique. Responda em português, de forma concisa."
    # Restrição explícita que ataca a falha de 'fora de escopo':
    "Se a informação NÃO estiver na base, diga claramente que NÃO TEM "
    "essa informação — nunca invente. Responda conciso, em português."
)


def build_model():
    """Cria o modelo já com as ferramentas vinculadas (tool calling)."""
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    return model.bind_tools(TOOLS)


# Ferramentas que NÓS escrevemos (Aulas 1-4).
TOOLS = [calculator, knowledge_search, lookup_cep]

# Ferramentas que VÊM de servidores MCP (Aula 9), sem adaptador sob medida.
_mcp_tools = carregar_tools_mcp()
TOOLS = TOOLS + _mcp_tools

# A partir daqui, o agente trata todas igual — locais e externas.
