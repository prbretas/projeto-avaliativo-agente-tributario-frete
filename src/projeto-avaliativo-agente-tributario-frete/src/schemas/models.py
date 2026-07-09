"""
Modelos de dados do AgenteClassTrib.
Todos os schemas Pydantic e o AgentState do LangGraph são definidos aqui.
"""
from typing import TypedDict, Literal, Optional, Annotated
from pydantic import BaseModel, field_validator
from datetime import date


# ---------------------------------------------------------------------------
# Modelos de entrada
# ---------------------------------------------------------------------------

class Operacao(BaseModel):
    """Dados de uma operação de frete a ser classificada tributariamente."""
    modal: Literal["rodoviario", "aereo", "aquaviario", "internacional"]
    origem_uf: str
    destino_uf: str
    regime_tributario: Literal["simples_nacional", "lucro_presumido", "lucro_real"]
    data_emissao: str  # ISO 8601: "2026-09-15"
    contratado_pessoa_fisica: bool = False  # True = TAC

    @field_validator("data_emissao")
    @classmethod
    def validar_data(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(f"data_emissao deve ser ISO 8601 (YYYY-MM-DD), recebeu: {v}")
        return v

    @field_validator("origem_uf", "destino_uf")
    @classmethod
    def validar_uf(cls, v: str) -> str:
        v = v.upper().strip()
        ufs_validas = {
            "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
            "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO",
            "EX"  # EX = exterior (transporte internacional)
        }
        if v not in ufs_validas:
            raise ValueError(f"UF inválida: {v}")
        return v


# ---------------------------------------------------------------------------
# Modelos intermediários
# ---------------------------------------------------------------------------

class TrechoRecuperado(BaseModel):
    """Trecho de documento regulatório recuperado pelo RAG."""
    documento: str   # ex: "lc_214_2025_frete"
    trecho: str      # conteúdo do chunk
    score: float     # score de similaridade (0.0–1.0)


class Classificacao(BaseModel):
    """Resultado da classificação do cenário tributário."""
    fase_transicao: Literal[
        "2026_teste",
        "2027_2032_convivencia",
        "2033_definitivo",
        "regime_especial"
    ]
    obrigatoriedade_destaque: bool
    observacoes: Optional[str] = None
    contexto_insuficiente: bool = False  # True = RAG não encontrou contexto relevante


class ResultadoCClassTrib(BaseModel):
    """Resultado da determinação do cClassTrib via tabela determinística."""
    cclasstrib: Optional[str]
    aliquota_cbs: Optional[float] = None
    aliquota_ibs: Optional[float] = None
    aliquota_total: Optional[float] = None
    determinado: bool  # False = requer revisão manual
    observacao: Optional[str] = None


# ---------------------------------------------------------------------------
# Estado do grafo LangGraph
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    """Estado compartilhado entre todos os nós do grafo LangGraph."""
    operacao: Optional[Operacao]
    contexto_recuperado: list[TrechoRecuperado]
    classificacao: Optional[Classificacao]
    resultado_cclasstrib: Optional[ResultadoCClassTrib]
    justificativa: Optional[str]
    fontes_citadas: list[str]
    aprovado_por_humano: Optional[bool]
    resultado_exportado: Optional[dict]
    erro: Optional[str]   # mensagem de erro se algum nó falhar


# ---------------------------------------------------------------------------
# Schemas da API REST
# ---------------------------------------------------------------------------

class OperacaoRequest(BaseModel):
    """Schema de entrada do endpoint POST /classificar."""
    modal: Literal["rodoviario", "aereo", "aquaviario", "internacional"]
    origem_uf: str
    destino_uf: str
    regime_tributario: Literal["simples_nacional", "lucro_presumido", "lucro_real"]
    data_emissao: str
    contratado_pessoa_fisica: bool = False


class ClassificacaoResponse(BaseModel):
    """Schema de resposta do endpoint POST /classificar."""
    thread_id: str
    status: Literal["pendente_revisao", "aprovado", "rejeitado", "erro"]
    cclasstrib: Optional[str] = None
    aliquota_total: Optional[float] = None
    fase_transicao: Optional[str] = None
    justificativa: Optional[str] = None
    fontes_citadas: list[str] = []


class ReviewRequest(BaseModel):
    """Schema de entrada do endpoint POST /classificar/{thread_id}/review."""
    aprovado: bool
    comentario: Optional[str] = None
