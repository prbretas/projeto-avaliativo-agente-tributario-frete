"""
Nó determine_cclasstrib: determina o código cClassTrib via tabela determinística.
Requisito R4 — Sugestão de código cClassTrib e alíquota.
IMPORTANTE: A decisão do código tributário vem de uma tabela/lookup, NUNCA do LLM.
"""
from src.schemas.models import AgentState, ResultadoCClassTrib
from src.tools.tabela_cclasstrib import consultar_cclasstrib


def determine_cclasstrib(state: AgentState) -> dict:
    """
    Nó 4 do grafo. Consulta a tabela determinística e retorna o cClassTrib.

    Atualiza no state:
    - resultado_cclasstrib: ResultadoCClassTrib
    - erro: str se determinado=False (R4.2)
    """
    classificacao = state.get("classificacao")
    operacao = state.get("operacao")

    if not classificacao or not operacao:
        return {
            "erro": "determine_cclasstrib: classificacao ou operacao ausente no state."
        }

    resultado = consultar_cclasstrib(
        fase_transicao=classificacao.fase_transicao,
        regime_tributario=operacao.regime_tributario,
        contratado_pessoa_fisica=operacao.contratado_pessoa_fisica,
        modal=operacao.modal,
    )

    # R4.2: se não determinado, sinaliza revisão manual
    erro = None
    if not resultado.determinado:
        erro = (
            f"classificacao_nao_determinada: combinação "
            f"({classificacao.fase_transicao}, {operacao.regime_tributario}, "
            f"TAC={operacao.contratado_pessoa_fisica}, modal={operacao.modal}) "
            "não encontrada na tabela. Requer revisão manual."
        )

    return {"resultado_cclasstrib": resultado, "erro": erro}
