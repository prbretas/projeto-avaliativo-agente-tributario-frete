"""Testes do nó determine_cclasstrib (ISSUE-008)."""
from src.schemas.models import Operacao, Classificacao
from src.graph.determine_cclasstrib import determine_cclasstrib


def _state(fase: str, regime: str, modal: str = "rodoviario", tac: bool = False) -> dict:
    op = Operacao(
        modal=modal,
        origem_uf="SP",
        destino_uf="RJ" if modal != "internacional" else "EX",
        regime_tributario=regime,
        data_emissao="2026-06-15",
        contratado_pessoa_fisica=tac,
    )
    cl = Classificacao(
        fase_transicao=fase,
        obrigatoriedade_destaque=True,
    )
    return {
        "operacao": op,
        "classificacao": cl,
        "contexto_recuperado": [],
        "resultado_cclasstrib": None,
        "justificativa": None,
        "fontes_citadas": [],
        "aprovado_por_humano": None,
        "resultado_exportado": None,
        "erro": None,
    }


def test_combinacao_conhecida():
    """R4.1 — combinação mapeada retorna resultado determinado."""
    result = determine_cclasstrib(_state("2026_teste", "lucro_real"))
    r = result["resultado_cclasstrib"]
    assert r.determinado is True
    assert r.cclasstrib is not None
    assert r.aliquota_total == 0.01
    assert result["erro"] is None


def test_combinacao_desconhecida_marca_revisao_manual():
    """R4.2 — combinação válida mas não mapeada retorna determinado=False e sinaliza revisão manual."""
    # "2033_definitivo" + "lucro_presumido" não está na tabela
    result = determine_cclasstrib(_state("2033_definitivo", "lucro_presumido"))
    r = result["resultado_cclasstrib"]
    assert r.determinado is False
    assert r.cclasstrib is None
    assert "revisão manual" in (result.get("erro") or "")


def test_simples_nacional_2026():
    """Simples Nacional 2026 retorna aliquota 0.0 (facultativo)."""
    result = determine_cclasstrib(_state("2026_teste", "simples_nacional"))
    r = result["resultado_cclasstrib"]
    assert r.determinado is True
    assert r.aliquota_total == 0.0


def test_tac_nao_contribuinte():
    """TAC (pessoa física) retorna cClassTrib '05' e aliquota 0.0."""
    result = determine_cclasstrib(_state("2026_teste", "lucro_real", tac=True))
    r = result["resultado_cclasstrib"]
    assert r.determinado is True
    assert r.cclasstrib == "05"
    assert r.aliquota_total == 0.0


def test_transporte_internacional():
    """Internacional retorna imunidade (aliquota 0.0)."""
    result = determine_cclasstrib(_state("2026_teste", "lucro_real", modal="internacional"))
    r = result["resultado_cclasstrib"]
    assert r.determinado is True
    assert r.aliquota_total == 0.0


def test_sem_classificacao_retorna_erro():
    """State sem classificacao retorna erro."""
    state = {
        "operacao": Operacao(
            modal="rodoviario", origem_uf="SP", destino_uf="RJ",
            regime_tributario="lucro_real", data_emissao="2026-06-15",
        ),
        "classificacao": None,
        "contexto_recuperado": [], "resultado_cclasstrib": None,
        "justificativa": None, "fontes_citadas": [],
        "aprovado_por_humano": None, "resultado_exportado": None, "erro": None,
    }
    result = determine_cclasstrib(state)
    assert result.get("erro") is not None
