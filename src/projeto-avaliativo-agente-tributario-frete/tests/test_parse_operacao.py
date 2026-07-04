"""Testes do nó parse_operacao (ISSUE-005)."""
import pytest
from src.schemas.models import Operacao, AgentState
from src.graph.parse_operacao import parse_operacao


def _state_base(**kwargs) -> dict:
    """Helper: monta um state mínimo para testes."""
    return {
        "operacao": {
            "modal": "rodoviario",
            "origem_uf": "SP",
            "destino_uf": "RJ",
            "regime_tributario": "lucro_real",
            "data_emissao": "2026-09-15",
            "contratado_pessoa_fisica": False,
            **kwargs,
        },
        "contexto_recuperado": [],
        "classificacao": None,
        "resultado_cclasstrib": None,
        "justificativa": None,
        "fontes_citadas": [],
        "aprovado_por_humano": None,
        "resultado_exportado": None,
        "erro": None,
    }


def test_dados_completos():
    """R1.1 — dados válidos → operacao populada, sem erro."""
    result = parse_operacao(_state_base())
    assert result["operacao"] is not None
    assert isinstance(result["operacao"], Operacao)
    assert result["erro"] is None


def test_campo_faltante_solicita_dado():
    """R1.2 — campo obrigatório ausente → erro descritivo."""
    state = _state_base()
    del state["operacao"]["modal"]
    result = parse_operacao(state)
    assert result.get("erro") is not None
    assert "modal" in result["erro"]


def test_data_fora_do_escopo_avisa():
    """R1.3 — data anterior a 01/01/2026 → aviso no campo erro."""
    result = parse_operacao(_state_base(data_emissao="2025-12-31"))
    assert result.get("erro") is not None
    assert "2026" in result["erro"]


def test_operacao_tac():
    """TAC (contratado_pessoa_fisica=True) deve ser aceito."""
    result = parse_operacao(_state_base(contratado_pessoa_fisica=True))
    assert result["operacao"].contratado_pessoa_fisica is True
    assert result["erro"] is None


def test_operacao_internacional():
    """Modal internacional com UF EX deve ser aceito."""
    result = parse_operacao(_state_base(modal="internacional", destino_uf="EX"))
    assert result["operacao"].modal == "internacional"
    assert result["erro"] is None


def test_sem_dados_retorna_erro():
    """State sem operacao → erro informativo."""
    state = {
        "operacao": None,
        "contexto_recuperado": [], "classificacao": None,
        "resultado_cclasstrib": None, "justificativa": None,
        "fontes_citadas": [], "aprovado_por_humano": None,
        "resultado_exportado": None, "erro": None,
    }
    result = parse_operacao(state)
    assert result.get("erro") is not None
