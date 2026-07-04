"""Testes do nó retrieve_context (ISSUE-006)."""
import pytest
from unittest.mock import patch, Mock
from src.schemas.models import Operacao, TrechoRecuperado
from src.graph.retrieve_context import retrieve_context


def _mock_path_entry(name: str) -> Mock:
    """Cria um mock de entrada de diretório com atributo .name."""
    entry = Mock()
    entry.name = name
    return entry


def _state_com_operacao(**kwargs) -> dict:
    op = Operacao(
        modal="rodoviario", origem_uf="SP", destino_uf="RJ",
        regime_tributario="lucro_real", data_emissao="2026-09-15",
        contratado_pessoa_fisica=False, **kwargs
    )
    return {
        "operacao": op, "contexto_recuperado": [], "classificacao": None,
        "resultado_cclasstrib": None, "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }


def test_retorna_trechos_relevantes():
    """R2.1 — com mock do RAG, deve retornar TrechoRecuperado populados."""
    mock_resultados = [
        {"documento": "lc_214_2025_frete", "trecho": "Art. 12 aliquota IBS CBS frete", "score": 0.85},
        {"documento": "notas_tecnicas_cte_2026", "trecho": "cClassTrib 01 regime regular 2026", "score": 0.72},
    ]
    with patch("src.graph.retrieve_context.recuperar_contexto", return_value=mock_resultados), \
         patch("src.graph.retrieve_context.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.iterdir.return_value = [_mock_path_entry("chroma.sqlite3")]

        result = retrieve_context(_state_com_operacao())

    assert result["erro"] is None
    assert len(result["contexto_recuperado"]) == 2
    assert isinstance(result["contexto_recuperado"][0], TrechoRecuperado)
    assert result["contexto_recuperado"][0].score == 0.85


def test_contexto_insuficiente_sinalizado():
    """R2.2 — RAG retorna lista vazia → erro contexto_insuficiente."""
    with patch("src.graph.retrieve_context.recuperar_contexto", return_value=[]), \
         patch("src.graph.retrieve_context.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.iterdir.return_value = [_mock_path_entry("chroma.sqlite3")]

        result = retrieve_context(_state_com_operacao())

    assert "contexto_insuficiente" in result.get("erro", "")
    assert result["contexto_recuperado"] == []


def test_sem_operacao_retorna_erro():
    """State sem operacao → erro."""
    state = {
        "operacao": None, "contexto_recuperado": [], "classificacao": None,
        "resultado_cclasstrib": None, "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }
    result = retrieve_context(state)
    assert result.get("erro") is not None
