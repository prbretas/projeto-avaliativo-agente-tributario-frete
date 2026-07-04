"""
Nó human_review: pausa o grafo para validação humana via interrupt() do LangGraph.
Requisito R6 — Validação humana (human-in-the-loop).

Fluxo:
- R6.1: ao chegar neste nó, o grafo pausa com interrupt() aguardando input humano
- R6.2: se rejeitado, retorna para classify_scenario (edge condicional no grafo)
- R6.3: se aprovado, marca aprovado_por_humano=True e avança para export_result
"""
from langgraph.types import interrupt
from src.schemas.models import AgentState


def human_review(state: AgentState) -> dict:
    """
    Nó 6 do grafo. Pausa a execução e aguarda aprovação humana.

    Usa interrupt() do LangGraph — a execução para completamente aqui
    e só retoma quando o usuário fornecer um valor via Command(resume=...).

    Valor esperado no resume:
    - {"aprovado": True}  → avança para export_result
    - {"aprovado": False, "comentario": "..."} → retorna para classify_scenario
    """
    classificacao = state.get("classificacao")
    resultado = state.get("resultado_cclasstrib")
    justificativa = state.get("justificativa")
    fontes = state.get("fontes_citadas", [])

    # Monta o resumo para exibição ao usuário
    resumo = {
        "fase_transicao": classificacao.fase_transicao if classificacao else None,
        "obrigatoriedade_destaque": classificacao.obrigatoriedade_destaque if classificacao else None,
        "cclasstrib": resultado.cclasstrib if resultado else None,
        "aliquota_total": resultado.aliquota_total if resultado else None,
        "justificativa": justificativa,
        "fontes_citadas": fontes,
        "instrucoes": (
            "Revise a classificação acima. "
            "Responda com {'aprovado': True} para confirmar "
            "ou {'aprovado': False, 'comentario': 'motivo'} para rejeitar."
        ),
    }

    # R6.1: interrupt() pausa o grafo — retoma com Command(resume={"aprovado": bool})
    resposta_humana = interrupt(resumo)

    aprovado = resposta_humana.get("aprovado", False)
    comentario = resposta_humana.get("comentario", None)

    return {
        "aprovado_por_humano": aprovado,
        "erro": None if aprovado else f"Classificacao rejeitada pelo usuário. Comentário: {comentario or 'sem comentário'}",
    }
