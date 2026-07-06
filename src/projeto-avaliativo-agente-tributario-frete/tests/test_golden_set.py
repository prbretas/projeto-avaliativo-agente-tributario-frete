"""Teste do golden set — valida taxa de acerto mínima de 80% (R8.2)."""
import json
import sys
from pathlib import Path

# Garante que src está no path
sys.path.insert(0, str(Path(__file__).parent.parent))

GOLDEN_SET = Path(__file__).parent.parent / "data" / "golden_set" / "cenarios.json"


def _avaliar(cenario: dict) -> dict:
    from src.graph.parse_operacao import parse_operacao
    from src.graph.classify_scenario import classify_scenario
    from src.graph.determine_cclasstrib import determine_cclasstrib

    state = {
        "operacao": cenario["operacao"], "contexto_recuperado": [],
        "classificacao": None, "resultado_cclasstrib": None,
        "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }
    state.update(parse_operacao(state))
    if state.get("erro") and not state.get("operacao"):
        return {"acerto_fase": False, "acerto_cclasstrib": False}

    state.update(classify_scenario(state))
    state.update(determine_cclasstrib(state))

    esperado = cenario["esperado"]
    classificacao = state.get("classificacao")
    resultado = state.get("resultado_cclasstrib")

    acerto_fase = classificacao and classificacao.fase_transicao == esperado.get("fase_transicao")
    esperado_det = esperado.get("determinado", True)
    if not esperado_det:
        acerto_cc = resultado and not resultado.determinado
    else:
        acerto_cc = resultado and resultado.cclasstrib == esperado.get("cclasstrib")

    return {"acerto_fase": bool(acerto_fase), "acerto_cclasstrib": bool(acerto_cc)}


def test_taxa_de_acerto_minima_80_porcento():
    """R8.2 — taxa de acerto >= 80% em fase_transicao e cclasstrib."""
    cenarios = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    assert len(cenarios) >= 15, f"Golden set deve ter >= 15 cenários, tem {len(cenarios)}"

    resultados = [_avaliar(c) for c in cenarios]
    total = len(resultados)
    acertos_fase = sum(1 for r in resultados if r["acerto_fase"])
    acertos_cc = sum(1 for r in resultados if r["acerto_cclasstrib"])

    taxa_fase = acertos_fase / total * 100
    taxa_cc = acertos_cc / total * 100

    assert taxa_fase >= 80.0, f"Taxa fase_transicao {taxa_fase:.0f}% < 80%"
    assert taxa_cc >= 80.0, f"Taxa cclasstrib {taxa_cc:.0f}% < 80%"
