"""Testes do nó generate_justification (ISSUE-009).

Usa mocks do LLM — sem chamadas reais ao Ollama.
"""
import json
from unittest.mock import patch, MagicMock
from src.schemas.models import Operacao, Classificacao, ResultadoCClassTrib, TrechoRecuperado
from src.graph.generate_justification import generate_justification


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
        "contexto_recuperado": [
            TrechoRecuperado(
                documento="lc_214_2025_frete",
                trecho="Art. 337 — Alíquota de teste 2026: 1% (0,9% CBS + 0,1% IBS)",
                score=0.88,
            )
        ],
        "justificativa": None,
        "fontes_citadas": [],
        "aprovado_por_humano": None,
        "resultado_exportado": None,
        "erro": None,
    }


def _mock_llm_response(texto: str):
    """Cria um mock de resposta do ChatOllama."""
    mock_resp = MagicMock()
    mock_resp.content = texto
    return mock_resp


def test_justificativa_contem_fonte():
    """R5.1 e R5.2 — LLM retorna JSON válido com fontes_citadas não-vazio."""
    payload = json.dumps({
        "justificativa": "A operação se enquadra na fase-teste 2026 conforme Art. 337 da LC 214/2025.",
        "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
    })
    with patch("src.graph.generate_justification.ChatOllama") as MockLLM:
        MockLLM.return_value.invoke.return_value = _mock_llm_response(payload)
        result = generate_justification(_state_completo())

    assert result["erro"] is None
    assert result["justificativa"] is not None
    assert len(result["fontes_citadas"]) >= 1
    assert "lc_214_2025_frete" in result["fontes_citadas"][0]


def test_retry_em_falha_de_formato():
    """R5.3 — primeira tentativa retorna JSON inválido, segunda retorna válido."""
    payload_valido = json.dumps({
        "justificativa": "Operação classificada conforme LC 214/2025.",
        "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
    })
    respostas = [
        _mock_llm_response("resposta inválida sem JSON"),
        _mock_llm_response(payload_valido),
    ]
    with patch("src.graph.generate_justification.ChatOllama") as MockLLM:
        MockLLM.return_value.invoke.side_effect = respostas
        result = generate_justification(_state_completo())

    assert result["erro"] is None
    assert result["justificativa"] is not None


def test_falha_total_retorna_erro():
    """R5.3 — ambas as tentativas falham → campo erro preenchido, justificativa fallback."""
    with patch("src.graph.generate_justification.ChatOllama") as MockLLM:
        MockLLM.return_value.invoke.return_value = _mock_llm_response("sem JSON aqui")
        result = generate_justification(_state_completo())

    assert result["erro"] is not None
    assert "falhou apos" in result["erro"]
    # Justificativa agora tem valor fallback (nao bloqueia o fluxo)
    assert result["justificativa"] is not None


def test_sem_fontes_usa_fallback_do_contexto():
    """R5.2 — fontes vazias → usa documentos do contexto RAG como fallback."""
    payload = json.dumps({
        "justificativa": "Justificativa sem fontes.",
        "fontes_citadas": [],
    })
    with patch("src.graph.generate_justification.ChatOllama") as MockLLM:
        MockLLM.return_value.invoke.return_value = _mock_llm_response(payload)
        result = generate_justification(_state_completo())

    # Com contexto RAG disponivel, usa documento como fallback
    assert result["erro"] is None
    assert len(result["fontes_citadas"]) >= 1


def test_sem_classificacao_retorna_erro():
    """State incompleto retorna erro imediato."""
    state = _state_completo()
    state["classificacao"] = None
    result = generate_justification(state)
    assert result.get("erro") is not None
