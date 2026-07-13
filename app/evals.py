# app/evals.py
# Harness de avaliação: roda casos golden contra o agente e calcula uma nota.

from dataclasses import dataclass
from typing import Callable


@dataclass
class EvalCase:
    nome: str
    entrada: str
    # cada checagem: (descrição, função que recebe a resposta e devolve bool)
    checagens: list


# --- Helpers de checagem (componíveis e legíveis) ---
def contains(substr: str) -> Callable[[str], bool]:
    """A resposta DEVE conter o trecho (case-insensitive)."""
    return lambda resp: substr.lower() in resp.lower()


def not_contains(substr: str) -> Callable[[str], bool]:
    """A resposta NÃO deve conter o trecho (ex.: alucinação conhecida)."""
    return lambda resp: substr.lower() not in resp.lower()


# --- Dataset golden: os cenários mais críticos do SEU agente ---
# Estes são exemplos sobre o domínio de docs/politicas.md; troque pelos seus.
CASOS = [
    EvalCase(
        nome="reembolso_prazo",
        entrada="Qual o prazo para solicitar reembolso?",
        checagens=[
            ("menciona 30 dias", contains("30 dias")),
            ("não inventa garantia vitalícia", not_contains("vitalícia")),
        ],
    ),
    EvalCase(
        nome="fora_de_escopo",
        entrada="Qual a capital da França?",
        checagens=[
            ("admite não ter a informação na base", contains("não")),
        ],
    ),
]
