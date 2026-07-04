"""
Nó retrieve_context: consulta a base RAG (Chroma) e recupera trechos regulatórios.
Requisito R2 — Recuperação de contexto regulatório.
"""
from pathlib import Path
from src.schemas.models import AgentState, TrechoRecuperado, Operacao
from src.rag.ingestao import recuperar_contexto, CHROMA_DIR

SCORE_MINIMO = 0.3  # R2.2: abaixo disso = contexto insuficiente
K_RESULTADOS = 4


def _montar_query(operacao: Operacao) -> str:
    """Constrói a query de busca a partir dos dados da operação."""
    partes = [
        f"frete {operacao.modal}",
        f"regime {operacao.regime_tributario}",
        f"IBS CBS aliquota {operacao.data_emissao[:4]}",
    ]
    if operacao.contratado_pessoa_fisica:
        partes.append("TAC transportador autonomo pessoa fisica")
    if operacao.modal == "internacional":
        partes.append("transporte internacional imunidade aliquota zero")
    return " ".join(partes)


def retrieve_context(state: AgentState) -> dict:
    """
    Nó 2 do grafo. Consulta o Chroma e retorna trechos relevantes.

    Atualiza no state:
    - contexto_recuperado: list[TrechoRecuperado]
    - erro: str se contexto insuficiente (R2.2)
    """
    operacao = state.get("operacao")
    if not operacao:
        return {"erro": "retrieve_context: operacao não encontrada no state."}

    # Verificar se o índice Chroma existe
    chroma_path = Path(CHROMA_DIR)
    arquivos = [f for f in chroma_path.iterdir() if f.name != ".gitkeep"] if chroma_path.exists() else []
    if not arquivos:
        return {
            "contexto_recuperado": [],
            "erro": "contexto_insuficiente: índice Chroma não encontrado. Execute scripts/run_ingestao.py primeiro.",
        }

    query = _montar_query(operacao)
    resultados_raw = recuperar_contexto(query, k=K_RESULTADOS)

    if not resultados_raw:
        # R2.2: nenhum trecho com score >= SCORE_MINIMO
        return {
            "contexto_recuperado": [],
            "erro": f"contexto_insuficiente: nenhum trecho relevante encontrado para a query: '{query}'",
        }

    trechos = [
        TrechoRecuperado(
            documento=r["documento"],
            trecho=r["trecho"],
            score=r["score"],
        )
        for r in resultados_raw
    ]

    return {"contexto_recuperado": trechos, "erro": None}
