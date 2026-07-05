"""
Montagem do grafo LangGraph completo.
Stub para ISSUE-011 — implementação completa na ISSUE-012.
"""
from langgraph.graph import StateGraph
from src.schemas.models import AgentState


def criar_grafo(checkpointer=None):
    """
    Cria e compila o StateGraph do agente.
    Stub: retorna grafo vazio com o State correto.
    Implementação completa na ISSUE-012.
    """
    builder = StateGraph(AgentState)
    # Nós e edges serão adicionados na ISSUE-012
    # Por ora, o stub permite que a API importe sem erro
    return builder.compile(checkpointer=checkpointer)
