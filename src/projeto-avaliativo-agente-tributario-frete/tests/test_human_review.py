"""Testes do nó human_review (ISSUE-010).

O interrupt() do LangGraph não pode ser chamado fora de um grafo em execução.
Os testes validam a lógica do nó usando mock do interrupt().
"""
from unittest.mock import patch
from src.schemas.models import Operacao, Classificacao, ResultadoCClassTrib
from src.graph.human_review import human_review


def _state_completo() -> dict:
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
        "aprovado_por_humano": None,
        "resultado_exportado": None,
        "erro": None,
    }


def test_interrupt_pausa_execucao():
    """R6.1 — interrupt() é chamado com o resumo da classificação."""
    with patch("src.graph.human_review.interrupt") as mock_interrupt:
        mock_interrupt.return_value = {"aprovado": True}
        result = human_review(_state_completo())

    # Verifica que interrupt() foi chamado com um dict contendo dados da classificação
    mock_interrupt.assert_called_once()
    chamada_args = mock_interrupt.call_args[0][0]
    assert "cclasstrib" in chamada_args
    assert "justificativa" in chamada_args
    assert "instrucoes" in chamada_args


def test_aprovacao_marca_aprovado():
    """R6.3 — resposta aprovado=True → aprovado_por_humano=True, sem erro."""
    with patch("src.graph.human_review.interrupt", return_value={"aprovado": True}):
        result = human_review(_state_completo())

    assert result["aprovado_por_humano"] is True
    assert result["erro"] is None


def test_rejeicao_permite_reclassificacao():
    """R6.2 — resposta aprovado=False → aprovado_por_humano=False, erro com comentário."""
    with patch("src.graph.human_review.interrupt",
               return_value={"aprovado": False, "comentario": "cClassTrib incorreto"}):
        result = human_review(_state_completo())

    assert result["aprovado_por_humano"] is False
    assert result["erro"] is not None
    assert "cClassTrib incorreto" in result["erro"]


def test_rejeicao_sem_comentario():
    """Rejeição sem comentário → erro genérico, sem quebrar."""
    with patch("src.graph.human_review.interrupt", return_value={"aprovado": False}):
        result = human_review(_state_completo())

    assert result["aprovado_por_humano"] is False
    assert result["erro"] is not None
