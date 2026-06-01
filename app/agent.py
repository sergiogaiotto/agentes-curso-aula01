# app/agent.py
# Define o agente ReAct mínimo com uma ferramenta de exemplo.

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# Carrega as variáveis do .env para o ambiente do processo
load_dotenv()


# --- Ferramenta de exemplo -------------------------------------------------
# O decorator @tool transforma a função em uma ferramenta que o agente pode chamar.
# A docstring é importante: o modelo a lê para decidir QUANDO usar a ferramenta.
@tool
def calculator(expression: str) -> str:
    """Avalia uma expressão aritmética simples (ex.: '3 * (4 + 2)').
    Use esta ferramenta sempre que precisar de um cálculo exato em vez de estimar."""
    try:
        # eval restrito: sem acesso a builtins, apenas aritmética.
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as exc:
        return f"Erro ao calcular: {exc}"


# --- Prompt de sistema -----------------------------------------------------
# Define o papel e as regras do agente. Claro, direto, sem excesso.
SYSTEM_PROMPT = (
    "Você é um assistente objetivo e confiável. "
    "Quando a pergunta envolver um cálculo exato, use a ferramenta calculator "
    "em vez de estimar de cabeça. Responda em português, de forma concisa."
)


# --- Construção do agente --------------------------------------------------
def build_agent():
    """Monta e retorna o agente ReAct. Chamado uma vez na inicialização da API."""
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,  # determinístico: bom para tarefas com ferramentas
    )

    # create_agent já implementa o laço ReAct sobre o runtime do LangGraph.
    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


# Instância única reutilizada pela API (evita reconstruir a cada requisição).
agent = build_agent()
