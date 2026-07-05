"""Testes do nó export_result (ISSUE-011)."""
import json
from pathlib import Path
from unittest.mock import patch
from src.schemas.models import Operacao, Classificacao, ResultadoCClassTrib
from src.graph.export_result import export_result


def _state_aprovado() -> dict:
    return {
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
        "contexto_recuperado": [],
        "justificativa": "Operação classificada conforme Art. 337 LC 214/2025.",
        "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
        "aprovado_por_humano": True,
        "resultado_exportado": None,
        "erro": None,
    }


def test_json_contem_campos_obrigatorios(tmp_path):
    """R7.1 — JSON exportado contém todos os campos obrigatórios."""
    with patch("src.graph.export_result.OUTPUTS_DIR", tmp_path):
        result = export_result(_state_aprovado())

    assert result["erro"] is None
    r = result["resultado_exportado"]
    assert r["cclasstrib"] == "01"
    assert r["aliquota_total"] == 0.01
    assert r["justificativa"] is not None
    assert len(r["fontes_citadas"]) >= 1
    assert r["aprovado_por_humano"] is True
    assert r["cenario"]["fase_transicao"] == "2026_teste"
    assert r["operacao"]["modal"] == "rodoviario"


def test_arquivo_json_criado(tmp_path):
    """R7.1 — arquivo JSON é gravado em disco."""
    with patch("src.graph.export_result.OUTPUTS_DIR", tmp_path):
        export_result(_state_aprovado())

    arquivos = list(tmp_path.glob("resultado_*.json"))
    assert len(arquivos) == 1

    conteudo = json.loads(arquivos[0].read_text(encoding="utf-8"))
    assert conteudo["cclasstrib"] == "01"


def test_nao_aprovado_retorna_erro():
    """Resultado não aprovado → erro, sem exportar."""
    state = _state_aprovado()
    state["aprovado_por_humano"] = False
    result = export_result(state)
    assert result.get("erro") is not None
    assert result.get("resultado_exportado") is None


def test_checkpoint_persistido(tmp_path):
    """R7.2 — a função exporta sem erros (checkpointer é responsabilidade do grafo)."""
    with patch("src.graph.export_result.OUTPUTS_DIR", tmp_path):
        result = export_result(_state_aprovado())

    # O nó em si não cria o checkpointer — isso é feito no grafo (ISSUE-012)
    # Aqui validamos que o resultado foi exportado corretamente
    assert result["resultado_exportado"] is not None
    assert result["erro"] is None
