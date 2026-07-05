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
from src.graph.grafo import criar_grafo  # montado na ISSUE-012

DB_PATH = "data/checkpoints.sqlite"
app = FastAPI(
    title="Agente Tributário de Frete",
    description="Classifica tributariamente operações de frete (IBS/CBS) conforme LC 214/2025",
    version="1.0.0",
)


def _get_checkpointer():
    return SqliteSaver.from_conn_string(DB_PATH)


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

        # Lê o estado após a pausa
        snapshot = grafo.get_state(config)
        vals = snapshot.values

    return ClassificacaoResponse(
        thread_id=thread_id,
        status="pendente_revisao",
        cclasstrib=vals.get("resultado_cclasstrib", {}).get("cclasstrib") if vals.get("resultado_cclasstrib") else None,
        aliquota_total=vals.get("resultado_cclasstrib", {}).get("aliquota_total") if vals.get("resultado_cclasstrib") else None,
        fase_transicao=vals.get("classificacao", {}).get("fase_transicao") if vals.get("classificacao") else None,
        justificativa=vals.get("justificativa"),
        fontes_citadas=vals.get("fontes_citadas", []),
    )


@app.get("/classificar/{thread_id}", response_model=ClassificacaoResponse)
def consultar(thread_id: str):
    """Consulta o estado atual de uma execução pelo thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    with _get_checkpointer() as checkpointer:
        grafo = criar_grafo(checkpointer)
        snapshot = grafo.get_state(config)

    if not snapshot:
        raise HTTPException(status_code=404, detail=f"thread_id '{thread_id}' nao encontrado")

    vals = snapshot.values
    aprovado = vals.get("aprovado_por_humano")
    status = "aprovado" if aprovado is True else ("rejeitado" if aprovado is False else "pendente_revisao")

    return ClassificacaoResponse(
        thread_id=thread_id,
        status=status,
        cclasstrib=vals.get("resultado_cclasstrib", {}).get("cclasstrib") if vals.get("resultado_cclasstrib") else None,
        aliquota_total=vals.get("resultado_cclasstrib", {}).get("aliquota_total") if vals.get("resultado_cclasstrib") else None,
        fase_transicao=vals.get("classificacao", {}).get("fase_transicao") if vals.get("classificacao") else None,
        justificativa=vals.get("justificativa"),
        fontes_citadas=vals.get("fontes_citadas", []),
    )


@app.post("/classificar/{thread_id}/review", response_model=ClassificacaoResponse)
def review(thread_id: str, request: ReviewRequest):
    """
    Retoma o grafo pausado no interrupt() com a decisão humana.
    aprovado=True → avanca para export_result
    aprovado=False → retorna para classify_scenario
    """
    config = {"configurable": {"thread_id": thread_id}}
    from langgraph.types import Command

    with _get_checkpointer() as checkpointer:
        grafo = criar_grafo(checkpointer)
        resposta = {"aprovado": request.aprovado}
        if request.comentario:
            resposta["comentario"] = request.comentario

        for _ in grafo.stream(Command(resume=resposta), config=config):
            pass

        snapshot = grafo.get_state(config)
        vals = snapshot.values

    status = "aprovado" if request.aprovado else "rejeitado"
    return ClassificacaoResponse(
        thread_id=thread_id,
        status=status,
        cclasstrib=vals.get("resultado_cclasstrib", {}).get("cclasstrib") if vals.get("resultado_cclasstrib") else None,
        aliquota_total=vals.get("resultado_cclasstrib", {}).get("aliquota_total") if vals.get("resultado_cclasstrib") else None,
        fase_transicao=vals.get("classificacao", {}).get("fase_transicao") if vals.get("classificacao") else None,
        justificativa=vals.get("justificativa"),
        fontes_citadas=vals.get("fontes_citadas", []),
    )
