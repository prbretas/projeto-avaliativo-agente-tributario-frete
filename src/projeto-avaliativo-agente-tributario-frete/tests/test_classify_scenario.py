"""Testes do nó classify_scenario (ISSUE-007)."""
from src.schemas.models import Operacao
from src.graph.classify_scenario import classify_scenario


def _state(operacao_kwargs: dict, contexto: list = None) -> dict:
    op = Operacao(**{
        "modal": "rodoviario", "origem_uf": "SP", "destino_uf": "RJ",
        "regime_tributario": "lucro_real", "data_emissao": "2026-09-15",
        "contratado_pessoa_fisica": False,
        **operacao_kwargs
    })
    return {
        "operacao": op,
        "contexto_recuperado": contexto or [],
        "classificacao": None, "resultado_cclasstrib": None,
        "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }


def test_fase_teste_2026():
    """R3.1 — Lucro Real em 2026 = fase_teste, destaque obrigatório."""
    result = classify_scenario(_state({"data_emissao": "2026-06-15", "regime_tributario": "lucro_real"}))
    c = result["classificacao"]
    assert c.fase_transicao == "2026_teste"
    assert c.obrigatoriedade_destaque is True


def test_simples_nacional_2026_facultativo():
    """R3.2 — Simples Nacional em 2026 = facultativo."""
    result = classify_scenario(_state({"data_emissao": "2026-06-15", "regime_tributario": "simples_nacional"}))
    c = result["classificacao"]
    assert c.fase_transicao == "2026_teste"
    assert c.obrigatoriedade_destaque is False


def test_simples_nacional_2027_obrigatorio():
    """R3.3 — Simples Nacional em 2027 = obrigatório."""
    result = classify_scenario(_state({"data_emissao": "2027-01-15", "regime_tributario": "simples_nacional"}))
    c = result["classificacao"]
    assert c.fase_transicao == "2027_2032_convivencia"
    assert c.obrigatoriedade_destaque is True


def test_transporte_internacional_imunidade():
    """R3.4 — Modal internacional = regime_especial, imunidade."""
    result = classify_scenario(_state({"modal": "internacional", "destino_uf": "EX"}))
    c = result["classificacao"]
    assert c.fase_transicao == "regime_especial"
    assert "imunidade" in (c.observacoes or "").lower()


def test_tac_pessoa_fisica_nao_contribuinte():
    """R3.5 — TAC = regime_especial, não contribuinte."""
    result = classify_scenario(_state({"contratado_pessoa_fisica": True}))
    c = result["classificacao"]
    assert c.fase_transicao == "regime_especial"
    assert c.obrigatoriedade_destaque is False
    assert "TAC" in (c.observacoes or "")
