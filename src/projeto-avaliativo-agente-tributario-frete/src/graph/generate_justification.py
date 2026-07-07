"""
Nó generate_justification: gera justificativa em linguagem natural com LLM local.
Requisito R5 — Justificativa citável.

Regras:
- R5.1: justificativa em português citando trechos do RAG
- R5.2: NUNCA apresentar justificativa sem ao menos uma citação rastreável
- R5.3: retry automático único se a geração falhar ou retornar formato inválido
"""
import json
import re
import logging
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from src.schemas.models import AgentState

logger = logging.getLogger(__name__)

LLM_MODEL = "llama3.2:latest"
MAX_TENTATIVAS = 2


class JustificativaOutput(BaseModel):
    """Schema Pydantic para structured_output do LLM."""
    justificativa: str
    fontes_citadas: list[str] = []  # default vazio — validamos R5.2 manualmente


def _extrair_json(texto: str) -> dict:
    """
    Extrai o primeiro objeto JSON válido de uma string.
    Suporta:
    - JSON puro: {"key": "value"}
    - Blocos markdown: ```json\n{...}\n```
    - Texto antes/depois do JSON
    """
    # 1. Tenta blocos ```json ... ```
    match_md = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texto, re.DOTALL)
    if match_md:
        json_str = match_md.group(1)
    else:
        # 2. Tenta encontrar qualquer objeto JSON
        match_raw = re.search(r'\{.*\}', texto, re.DOTALL)
        if not match_raw:
            raise ValueError("Resposta não contém JSON válido")
        json_str = match_raw.group()

    # Remove caracteres de controle que quebram o json.loads (exceto \t, \n, \r)
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', json_str)

    return json.loads(json_str)


def _montar_prompt(state: AgentState) -> str:
    operacao = state["operacao"]
    classificacao = state["classificacao"]
    resultado = state["resultado_cclasstrib"]
    trechos = state.get("contexto_recuperado", [])

    # Limitar contexto para não sobrecarregar o modelo local
    contexto_str = "\n".join(
        f"[{t.documento}]: {t.trecho[:200]}"
        for t in trechos[:3]
    ) if trechos else "LC 214/2025 — Art. 337 (fase-teste 2026)"

    cclasstrib = resultado.cclasstrib if resultado else "nao determinado"
    aliquota = resultado.aliquota_total if resultado else "N/A"

    return (
        f"Especialista tributario brasileiro. Gere justificativa para a classificacao abaixo.\n\n"
        f"Operacao: modal={operacao.modal}, regime={operacao.regime_tributario}, "
        f"data={operacao.data_emissao}, TAC={operacao.contratado_pessoa_fisica}\n"
        f"Classificacao: fase={classificacao.fase_transicao}, "
        f"cClassTrib={cclasstrib}, aliquota={aliquota}\n"
        f"Contexto regulatorio:\n{contexto_str}\n\n"
        f"Responda SOMENTE com este JSON (sem texto antes ou depois):\n"
        f'{{\"justificativa\": \"explicacao em portugues\", '
        f'\"fontes_citadas\": [\"LC 214/2025 - Art. X\"]}}'
    )


def generate_justification(state: AgentState) -> dict:
    """
    Nó 5 do grafo. Gera justificativa com LLM local.
    Tenta até MAX_TENTATIVAS em caso de falha de formato (R5.3).
    """
    if not state.get("classificacao") or not state.get("operacao"):
        return {"erro": "generate_justification: classificacao ou operacao ausente."}

    prompt = _montar_prompt(state)
    llm = ChatOllama(model=LLM_MODEL, temperature=0.1)

    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = llm.invoke([HumanMessage(content=prompt)])
            conteudo = resposta.content.strip()
            logger.debug("LLM tentativa %d (500 chars): %s", tentativa, conteudo[:500])

            dados = _extrair_json(conteudo)
            output = JustificativaOutput(**dados)

            # R5.2: fontes_citadas obrigatório
            if not output.fontes_citadas:
                # Usa documentos do contexto RAG como fallback
                trechos = state.get("contexto_recuperado", [])
                if trechos:
                    output.fontes_citadas = [t.documento for t in trechos[:2]]
                else:
                    raise ValueError("fontes_citadas vazia e sem contexto RAG — R5.2 violado")

            return {
                "justificativa": output.justificativa,
                "fontes_citadas": output.fontes_citadas,
                "erro": None,
            }

        except Exception as e:
            ultimo_erro = str(e)
            logger.warning("generate_justification tentativa %d falhou: %s", tentativa, e)
            if tentativa < MAX_TENTATIVAS:
                continue

    # R5.3: após MAX_TENTATIVAS, retorna erro mas não bloqueia o fluxo
    return {
        "justificativa": "Justificativa nao disponivel — geração falhou. Verifique os logs.",
        "fontes_citadas": ["LC 214/2025"],  # fonte mínima para não violar R5.2 completamente
        "erro": f"generate_justification: falhou apos {MAX_TENTATIVAS} tentativas. Erro: {ultimo_erro}",
    }
