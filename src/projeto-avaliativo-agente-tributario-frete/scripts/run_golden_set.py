"""
Script de avaliação do golden set — Agente de Classificação Tributária de Frete.
Executa: python scripts/run_golden_set.py

Meta: taxa de acerto >= 80% em fase_transicao e cclasstrib (R8.2).
"""
import sys
import json
from pathlib import Path

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.parse_operacao import parse_operacao
from src.graph.classify_scenario import classify_scenario
from src.graph.determine_cclasstrib import determine_cclasstrib

GOLDEN_SET = Path(__file__).parent.parent / "data" / "golden_set" / "cenarios.json"


def avaliar_cenario(cenario: dict) -> dict:
    """Executa os nós determinísticos (sem LLM) e compara com o esperado."""
    op_dict = cenario["operacao"]
    esperado = cenario["esperado"]

    # parse
    state = {
        "operacao": op_dict, "contexto_recuperado": [], "classificacao": None,
        "resultado_cclasstrib": None, "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }
    state.update(parse_operacao(state))

    if state.get("erro") and not state.get("operacao"):
        return {"id": cenario["id"], "acerto_fase": False, "acerto_cclasstrib": False, "erro": state["erro"]}

    # classify
    state.update(classify_scenario(state))
    classificacao = state.get("classificacao")

    # determine
    state.update(determine_cclasstrib(state))
    resultado = state.get("resultado_cclasstrib")

    acerto_fase = (
        classificacao is not None and
        classificacao.fase_transicao == esperado.get("fase_transicao")
    )

    # cClassTrib: se esperado.determinado == False, aceita determinado=False como correto
    esperado_determinado = esperado.get("determinado", True)
    if not esperado_determinado:
        acerto_cc = resultado is not None and not resultado.determinado
    else:
        acerto_cc = (
            resultado is not None and
            resultado.cclasstrib == esperado.get("cclasstrib")
        )

    return {
        "id": cenario["id"],
        "descricao": cenario["descricao"],
        "fase_esperada": esperado.get("fase_transicao"),
        "fase_obtida": classificacao.fase_transicao if classificacao else None,
        "cclasstrib_esperado": esperado.get("cclasstrib"),
        "cclasstrib_obtido": resultado.cclasstrib if resultado else None,
        "acerto_fase": acerto_fase,
        "acerto_cclasstrib": acerto_cc,
        "erro": state.get("erro"),
    }


def main():
    cenarios = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    print(f"\n{'='*60}")
    print(f"GOLDEN SET — {len(cenarios)} cenários")
    print(f"{'='*60}\n")

    resultados = [avaliar_cenario(c) for c in cenarios]

    acertos_fase = sum(1 for r in resultados if r["acerto_fase"])
    acertos_cc = sum(1 for r in resultados if r["acerto_cclasstrib"])
    total = len(resultados)

    for r in resultados:
        status_fase = "✓" if r["acerto_fase"] else "✗"
        status_cc = "✓" if r["acerto_cclasstrib"] else "✗"
        print(f"[{r['id']}] {r['descricao'][:55]:<55}")
        print(f"       fase: {status_fase} ({r['fase_obtida']})  cclasstrib: {status_cc} ({r['cclasstrib_obtido']})")
        if r.get("erro") and "AVISO" not in (r["erro"] or ""):
            print(f"       ⚠ {r['erro'][:80]}")
        print()

    taxa_fase = acertos_fase / total * 100
    taxa_cc = acertos_cc / total * 100

    print(f"{'='*60}")
    print(f"Taxa de acerto — fase_transicao : {acertos_fase}/{total} ({taxa_fase:.0f}%)")
    print(f"Taxa de acerto — cClassTrib     : {acertos_cc}/{total} ({taxa_cc:.0f}%)")
    print(f"{'='*60}")

    meta = 80.0
    aprovado = taxa_fase >= meta and taxa_cc >= meta
    print(f"\nResultado: {'✓ APROVADO' if aprovado else '✗ REPROVADO'} (meta: >= {meta:.0f}%)\n")

    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(main())
