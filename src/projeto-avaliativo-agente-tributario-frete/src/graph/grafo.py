"""
Montagem do grafo LangGraph completo — Agente de Classificação Tributária de Frete.
ISSUE-012: conecta todos os nós com StateGraph + edges condicionais.

Fluxo:
  parse_operacao → retrieve_context → classify_scenario → determine_cclasstrib
  → generate_justification → human_review
    ├─ aprovado → export_result → END
    └─ rejeitado → classify_scenario  (permite reclassificação)
"""
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from src.schemas.models import AgentState
from src.graph.parse_operacao import parse_operacao
from src.graph.retrieve_context import retrieve_context
from src.graph.classify_scenario import classify_scenario
from src.graph.determine_cclasstrib import determine_cclasstrib
from src.graph.generate_justification import generate_justification
from src.graph.human_review import human_review
from src.graph.export_result import export_result

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Edges condicionais
# ---------------------------------------------------------------------------

def _apos_parse(state: AgentState) -> str:
    """Após parse_operacao: se erro crítico (sem operacao), encerra."""
    if state.get("erro") and not state.get("operacao"):
        logger.warning("parse_operacao falhou: %s", state.get("erro"))
        return END
    return "retrieve_context"


def _apos_retrieve(state: AgentState) -> str:
    """Após retrieve_context: sempre avança para classify_scenario."""
    # contexto_insuficiente não bloqueia o fluxo — é propagado como flag
    return "classify_scenario"


def _apos_human_review(state: AgentState) -> str:
    """
    Edge condicional no human_review:
    - aprovado=True  → export_result
    - aprovado=False → classify_scenario (reclassificação — R6.2)
    """
    if state.get("aprovado_por_humano") is True:
        return "export_result"
    # Rejeição: limpa classificação anterior para forçar novo ciclo
    return "classify_scenario"


# ---------------------------------------------------------------------------
# Factory do grafo
# ---------------------------------------------------------------------------

def criar_grafo(checkpointer=None):
    """
    Cria e compila o StateGraph completo do agente.

    Args:
        checkpointer: SqliteSaver ou MemorySaver para persistência de estado.
                      Se None, o grafo roda sem checkpointer (sem auditoria).
    Returns:
        CompiledStateGraph pronto para uso.
    """
    builder = StateGraph(AgentState)

    # Registrar nós
    builder.add_node("parse_operacao", parse_operacao)
    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("classify_scenario", classify_scenario)
    builder.add_node("determine_cclasstrib", determine_cclasstrib)
    builder.add_node("generate_justification", generate_justification)
    builder.add_node("human_review", human_review)
    builder.add_node("export_result", export_result)

    # Ponto de entrada
    builder.set_entry_point("parse_operacao")

    # Edges fixas
    builder.add_conditional_edges("parse_operacao", _apos_parse)
    builder.add_conditional_edges("retrieve_context", _apos_retrieve)
    builder.add_edge("classify_scenario", "determine_cclasstrib")
    builder.add_edge("determine_cclasstrib", "generate_justification")
    builder.add_edge("generate_justification", "human_review")

    # Edge condicional após human_review (R6.2: rejeição volta para classify)
    builder.add_conditional_edges("human_review", _apos_human_review)

    # Fim do fluxo feliz
    builder.add_edge("export_result", END)

    # Compilar com checkpointer (necessário para interrupt())
    return builder.compile(checkpointer=checkpointer)
