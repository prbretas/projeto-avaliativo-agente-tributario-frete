"""Testes dos schemas Pydantic do agente."""
import pytest
from src.schemas.models import (
    Operacao, TrechoRecuperado, Classificacao,
    ResultadoCClassTrib, AgentState
)


def test_operacao_valida():
    op = Operacao(
        modal="rodoviario",
        origem_uf="SP",
        destino_uf="RJ",
        regime_tributario="lucro_real",
        data_emissao="2026-09-15",
        contratado_pessoa_fisica=False,
    )
    assert op.modal == "rodoviario"
    assert op.origem_uf == "SP"
    assert op.data_emissao == "2026-09-15"


def test_operacao_invalida_rejeitada():
    with pytest.raises(Exception):
        Operacao(
            modal="bicicleta",  # modal inválido
            origem_uf="SP",
            destino_uf="RJ",
            regime_tributario="lucro_real",
            data_emissao="2026-09-15",
        )


def test_operacao_data_invalida():
    with pytest.raises(Exception):
        Operacao(
            modal="rodoviario",
            origem_uf="SP",
            destino_uf="RJ",
            regime_tributario="lucro_real",
            data_emissao="15/09/2026",  # formato errado
        )


def test_operacao_uf_normalizada():
    op = Operacao(
        modal="rodoviario",
        origem_uf="sp",  # minúscula — deve normalizar para SP
        destino_uf="rj",
        regime_tributario="lucro_real",
        data_emissao="2026-09-15",
    )
    assert op.origem_uf == "SP"
    assert op.destino_uf == "RJ"


def test_trecho_recuperado():
    t = TrechoRecuperado(
        documento="lc_214_2025_frete",
        trecho="Art. 12 — A alíquota de IBS é de 0,1%",
        score=0.87,
    )
    assert t.score == 0.87


def test_classificacao_valida():
    c = Classificacao(
        fase_transicao="2026_teste",
        obrigatoriedade_destaque=True,
    )
    assert c.fase_transicao == "2026_teste"
    assert c.contexto_insuficiente is False


def test_resultado_nao_determinado():
    r = ResultadoCClassTrib(
        cclasstrib=None,
        determinado=False,
        observacao="Combinação não mapeada",
    )
    assert r.determinado is False


def test_agent_state_inicializavel():
    state: AgentState = {
        "operacao": None,
        "contexto_recuperado": [],
        "classificacao": None,
        "resultado_cclasstrib": None,
        "justificativa": None,
        "fontes_citadas": [],
        "aprovado_por_humano": None,
        "resultado_exportado": None,
        "erro": None,
    }
    assert state["operacao"] is None
    assert isinstance(state["fontes_citadas"], list)
