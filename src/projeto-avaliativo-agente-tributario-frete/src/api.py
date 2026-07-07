"""
API REST do Agente de Classificação Tributária de Frete.
Requisito R7.2 — endpoint REST para integração externa.

Endpoints:
  POST /classificar              → dispara o grafo, retorna thread_id + status
  GET  /classificar/{thread_id}  → consulta estado atual de uma execução
  POST /classificar/{thread_id}/review → aprova ou rejeita (retoma o interrupt())
"""
import uuid
from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.sqlite import SqliteSaver
from src.schemas.models import OperacaoRequest, ClassificacaoResponse, ReviewRequest
from src.graph.grafo import criar_grafo

DB_PATH = "data/checkpoints.sqlite"
app = FastAPI(
    title="Agente Tributário de Frete",
    description="Classifica tributariamente operações de frete (IBS/CBS) conforme LC 214/2025",
    version="1.0.0",
)


def _get_checkpointer():
    return SqliteSaver.from_conn_string(DB_PATH)


def _extrair_resposta(thread_id: str, vals: dict, status: str) -> ClassificacaoResponse:
    """
    Extrai campos do AgentState para o schema de resposta.
    Funciona com objetos Pydantic (produção) e dicts (testes/mocks).
    """
    resultado = vals.get("resultado_cclasstrib")
    classificacao = vals.get("classificacao")

    def _campo(obj, attr):
        """Acessa atributo em objeto Pydantic ou chave em dict."""
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj.get(attr)
        return getattr(obj, attr, None)

    return ClassificacaoResponse(
        thread_id=thread_id,
        status=status,
        cclasstrib=_campo(resultado, "cclasstrib"),
        aliquota_total=_campo(resultado, "aliquota_total"),
        fase_transicao=_campo(classificacao, "fase_transicao"),
        justificativa=vals.get("justificativa"),
        fontes_citadas=vals.get("fontes_citadas") or [],
    )


@app.post("/classificar", response_model=ClassificacaoResponse, status_code=202)
def classificar(request: OperacaoRequest):
    """
    Dispara o grafo com os dados da operação.
    Retorna thread_id e status 'pendente_revisao' quando o grafo pausa no human_review.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    with _get_checkpointer() as checkpointer:
        grafo = criar_grafo(checkpointer)
        state_inicial = {
            "operacao": request.model_dump(),
            "contexto_recuperado": [],
            "classificacao": None,
            "resultado_cclasstrib": None,
            "justificativa": None,
            "fontes_citadas": [],
            "aprovado_por_humano": None,
            "resultado_exportado": None,
            "erro": None,
        }
        # Executa até o interrupt() no human_review
        for _ in grafo.stream(state_inicial, config=config):
            pass

        snapshot = grafo.get_state(config)
        vals = snapshot.values

    return _extrair_resposta(thread_id, vals, "pendente_revisao")


@app.get("/classificar/{thread_id}", response_model=ClassificacaoResponse)
def consultar(thread_id: str):
    """Consulta o estado atual de uma execução pelo thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    with _get_checkpointer() as checkpointer:
        grafo = criar_grafo(checkpointer)
        snapshot = grafo.get_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail=f"thread_id '{thread_id}' nao encontrado")

    vals = snapshot.values
    aprovado = vals.get("aprovado_por_humano")
    status = "aprovado" if aprovado is True else ("rejeitado" if aprovado is False else "pendente_revisao")

    return _extrair_resposta(thread_id, vals, status)


@app.post("/classificar/{thread_id}/review", response_model=ClassificacaoResponse)
def review(thread_id: str, request: ReviewRequest):
    """
    Retoma o grafo pausado no interrupt() com a decisão humana.
    aprovado=True → avanca para export_result
    aprovado=False → retorna para classify_scenario
    """
    from langgraph.types import Command

    config = {"configurable": {"thread_id": thread_id}}
    resposta = {"aprovado": request.aprovado}
    if request.comentario:
        resposta["comentario"] = request.comentario

    with _get_checkpointer() as checkpointer:
        grafo = criar_grafo(checkpointer)
        for _ in grafo.stream(Command(resume=resposta), config=config):
            pass

        snapshot = grafo.get_state(config)
        vals = snapshot.values

    status = "aprovado" if request.aprovado else "rejeitado"
    return _extrair_resposta(thread_id, vals, status)
