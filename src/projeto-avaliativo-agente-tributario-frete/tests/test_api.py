"""
Testes da API REST (ISSUE-011).
Usa TestClient do FastAPI com mocks do grafo — sem execução real do LangGraph.
"""
import pytest
from unittest.mock import patch, MagicMock


def _mock_snapshot(vals: dict):
    snap = MagicMock()
    snap.values = vals
    return snap


def _vals_pendente():
    return {
        "resultado_cclasstrib": {"cclasstrib": "01", "aliquota_total": 0.01},
        "classificacao": {"fase_transicao": "2026_teste"},
        "justificativa": "Operação classificada conforme LC 214/2025.",
        "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
        "aprovado_por_humano": None,
    }


@pytest.fixture
def client():
    """Cria TestClient com grafo mockado."""
    # Precisamos do grafo para importar a api — mock antes do import
    with patch("src.graph.grafo.criar_grafo") as _:
        from fastapi.testclient import TestClient
        from src.api import app
        return TestClient(app)


def test_post_classificar_retorna_thread_id(client):
    """POST /classificar retorna thread_id e status pendente_revisao."""
    mock_grafo = MagicMock()
    mock_grafo.stream.return_value = iter([{}])
    mock_grafo.get_state.return_value = _mock_snapshot(_vals_pendente())

    with patch("src.api.criar_grafo", return_value=mock_grafo), \
         patch("src.api._get_checkpointer") as mock_cp:
        mock_cp.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_cp.return_value.__exit__ = MagicMock(return_value=False)

        resp = client.post("/classificar", json={
            "modal": "rodoviario",
            "origem_uf": "SP",
            "destino_uf": "RJ",
            "regime_tributario": "lucro_real",
            "data_emissao": "2026-09-15",
            "contratado_pessoa_fisica": False,
        })

    assert resp.status_code == 202
    data = resp.json()
    assert "thread_id" in data
    assert data["status"] == "pendente_revisao"


def test_review_endpoint_aprova_resultado(client):
    """POST /classificar/{thread_id}/review com aprovado=True retorna status aprovado."""
    mock_grafo = MagicMock()
    mock_grafo.stream.return_value = iter([{}])
    vals_aprovado = {**_vals_pendente(), "aprovado_por_humano": True}
    mock_grafo.get_state.return_value = _mock_snapshot(vals_aprovado)

    with patch("src.api.criar_grafo", return_value=mock_grafo), \
         patch("src.api._get_checkpointer") as mock_cp:
        mock_cp.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_cp.return_value.__exit__ = MagicMock(return_value=False)

        resp = client.post("/classificar/thread-123/review", json={"aprovado": True})

    assert resp.status_code == 200
    assert resp.json()["status"] == "aprovado"
