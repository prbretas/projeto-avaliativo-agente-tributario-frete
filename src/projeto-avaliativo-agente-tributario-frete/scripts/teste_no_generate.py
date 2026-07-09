"""Teste direto do nó generate_justification."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas.models import (
    Operacao, Classificacao, ResultadoCClassTrib, TrechoRecuperado, AgentState
)
from src.graph.generate_justification import generate_justification

state = {
    "operacao": Operacao(
        modal="rodoviario", origem_uf="SP", destino_uf="RJ",
        regime_tributario="lucro_real", data_emissao="2026-09-15",
    ),
    "classificacao": Classificacao(
        fase_transicao="2026_teste", obrigatoriedade_destaque=True,
    ),
    "resultado_cclasstrib": ResultadoCClassTrib(
        cclasstrib="01", aliquota_total=0.01, determinado=True,
    ),
    "contexto_recuperado": [
        TrechoRecuperado(
            documento="lc_214_2025_frete",
            trecho="Art. 337 — Em 2026 a aliquota somada de IBS e CBS sera de 1%.",
            score=0.88,
        )
    ],
    "justificativa": None,
    "fontes_citadas": [],
    "aprovado_por_humano": None,
    "resultado_exportado": None,
    "erro": None,
}

print("Executando nó generate_justification...")
result = generate_justification(state)
print(f"\nerro: {result.get('erro')}")
print(f"justificativa: {result.get('justificativa', '')[:200]}")
print(f"fontes_citadas: {result.get('fontes_citadas')}")
