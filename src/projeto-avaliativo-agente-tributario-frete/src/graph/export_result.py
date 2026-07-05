"""
Nó export_result: exporta o resultado aprovado em JSON e persiste via SqliteSaver.
Requisito R7 — Exportação do resultado.
"""
import json
from datetime import datetime
from pathlib import Path
from src.schemas.models import AgentState

OUTPUTS_DIR = Path(__file__).parent.parent.parent / "data" / "outputs"


def export_result(state: AgentState) -> dict:
    """
    Nó 7 do grafo. Exporta resultado aprovado em JSON.

    R7.1: JSON contendo operacao, cenario, cClassTrib, aliquota, justificativa, fontes.
    R7.2: persistência de estado via SqliteSaver (configurado no grafo, não aqui).
    """
    if not state.get("aprovado_por_humano"):
        return {"erro": "export_result: resultado nao aprovado. Nao exportar."}

    operacao = state.get("operacao")
    classificacao = state.get("classificacao")
    resultado = state.get("resultado_cclasstrib")

    resultado_dict = {
        "timestamp": datetime.now().isoformat(),
        "operacao": operacao.model_dump() if operacao else None,
        "cenario": {
            "fase_transicao": classificacao.fase_transicao if classificacao else None,
            "obrigatoriedade_destaque": classificacao.obrigatoriedade_destaque if classificacao else None,
            "observacoes": classificacao.observacoes if classificacao else None,
        },
        "cclasstrib": resultado.cclasstrib if resultado else None,
        "aliquota_total": resultado.aliquota_total if resultado else None,
        "aliquota_cbs": resultado.aliquota_cbs if resultado else None,
        "aliquota_ibs": resultado.aliquota_ibs if resultado else None,
        "justificativa": state.get("justificativa"),
        "fontes_citadas": state.get("fontes_citadas", []),
        "aprovado_por_humano": True,
    }

    # Persiste o JSON em disco
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    nome = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    caminho = OUTPUTS_DIR / nome
    caminho.write_text(json.dumps(resultado_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"resultado_exportado": resultado_dict, "erro": None}
