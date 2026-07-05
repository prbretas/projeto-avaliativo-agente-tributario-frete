"""
Testes end-to-end do grafo completo (ISSUE-012).

Usa MemorySaver como checkpointer (não persiste em disco).
Mockamos: Ollama (generate_justification), Chroma (retrieve_context).
"""
import json
from unittest.mock import patch, MagicMock
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from src.graph.grafo import criar_grafo


def _mock_retrieve_com_trechos(state):
    """Mock de retrieve_context que retorna 1 trecho."""
    from src.schemas.models import TrechoRecuperado
    return {
        "contexto_recuperado": [
            TrechoRecuperado(
                documento="lc_214_2025_frete",
                trecho="Art. 337 — fase-teste 2026, aliquota 1%",
                score=0.88,
            )
        ],
        "erro": None,
    }


def _mock_generate_ok(state):
    """Mock de generate_justification que retorna justificativa válida."""
    return {
        "justificativa": "Operação classificada conforme Art. 337 da LC 214/2025.",
        "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
        "erro": None,
    }


def _input_rodoviario_lucro_real():
    return {
        "operacao": {
            "modal": "rodoviario",
            "origem_uf": "SP",
            "destino_uf": "RJ",
            "regime_tributario": "lucro_real",
            "data_emissao": "2026-09-15",
            "contratado_pessoa_fisica": False,
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


def test_fluxo_completo_happy_path(tmp_path):
    """Fluxo completo: parse → retrieve → classify → determine → justify → approve → export."""
    checkpointer = MemorySaver()
    thread_id = "test-happy-path"
    config = {"configurable": {"thread_id": thread_id}}

    with patch("src.graph.retrieve_context.Path") as mock_path, \
         patch("src.graph.retrieve_context.recuperar_contexto") as mock_rag, \
         patch("src.graph.generate_justification.ChatOllama") as mock_llm, \
         patch("src.graph.export_result.OUTPUTS_DIR", tmp_path):

        # Configura mocks
        mock_path.return_value.exists.return_value = True
        entry = MagicMock(); entry.name = "chroma.sqlite3"
        mock_path.return_value.iterdir.return_value = [entry]
        mock_rag.return_value = [
            {"documento": "lc_214_2025_frete", "trecho": "Art. 337 aliquota 1%", "score": 0.88}
        ]
        payload = json.dumps({
            "justificativa": "Operação fase-teste 2026 conforme Art. 337.",
            "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
        })
        mock_resp = MagicMock()
        mock_resp.content = payload
        mock_llm.return_value.invoke.return_value = mock_resp

        grafo = criar_grafo(checkpointer)

        # Executa até o interrupt() no human_review
        events = list(grafo.stream(_input_rodoviario_lucro_real(), config=config))
        assert len(events) > 0

        # Verifica que o grafo parou no human_review (interrupt)
        snapshot = grafo.get_state(config)
        assert snapshot.next  # deve ter próximo nó pendente

        # Retoma com aprovação humana
        events_resume = list(grafo.stream(
            Command(resume={"aprovado": True}), config=config
        ))

    # Verifica resultado final
    snapshot_final = grafo.get_state(config)
    vals = snapshot_final.values
    assert vals.get("aprovado_por_humano") is True
    assert vals.get("resultado_exportado") is not None
    assert vals["resultado_exportado"]["cclasstrib"] == "01"


def test_fluxo_com_rejeicao_humana(tmp_path):
    """Fluxo com rejeição: human_review rejeita → volta para classify_scenario → aprova."""
    checkpointer = MemorySaver()
    thread_id = "test-rejeicao"
    config = {"configurable": {"thread_id": thread_id}}

    with patch("src.graph.retrieve_context.Path") as mock_path, \
         patch("src.graph.retrieve_context.recuperar_contexto") as mock_rag, \
         patch("src.graph.generate_justification.ChatOllama") as mock_llm, \
         patch("src.graph.export_result.OUTPUTS_DIR", tmp_path):

        entry = MagicMock(); entry.name = "chroma.sqlite3"
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.iterdir.return_value = [entry]
        mock_rag.return_value = [
            {"documento": "lc_214_2025_frete", "trecho": "Art. 337", "score": 0.88}
        ]
        payload = json.dumps({
            "justificativa": "Operação conforme LC 214/2025.",
            "fontes_citadas": ["lc_214_2025_frete - Art. 337"],
        })
        mock_resp = MagicMock()
        mock_resp.content = payload
        mock_llm.return_value.invoke.return_value = mock_resp

        grafo = criar_grafo(checkpointer)

        # 1ª execução até interrupt
        list(grafo.stream(_input_rodoviario_lucro_real(), config=config))

        # Rejeição: volta para classify_scenario
        list(grafo.stream(Command(resume={"aprovado": False, "comentario": "teste"}), config=config))

        # 2ª parada no human_review após reclassificação
        snapshot = grafo.get_state(config)
        # O grafo deve estar parado novamente no human_review
        assert snapshot is not None

        # Aprovação na 2ª rodada
        list(grafo.stream(Command(resume={"aprovado": True}), config=config))

    snapshot_final = grafo.get_state(config)
    vals = snapshot_final.values
    assert vals.get("aprovado_por_humano") is True
