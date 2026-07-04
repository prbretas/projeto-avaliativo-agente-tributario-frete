"""
Nó generate_justification: gera justificativa em linguagem natural com LLM local.
Requisito R5 — Justificativa citável.

Regras:
- R5.1: justificativa em português citando trechos do RAG
- R5.2: NUNCA apresentar justificativa sem ao menos uma citação rastreável
- R5.3: retry automático único se a geração falhar ou retornar formato inválido
"""
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from src.schemas.models import AgentState

LLM_MODEL = "llama3.2:latest"
MAX_TENTATIVAS = 2


class JustificativaOutput(BaseModel):
    """Schema Pydantic para structured_output do LLM."""
    justificativa: str
    fontes_citadas: list[str]


def _montar_prompt(state: AgentState) -> str:
    operacao = state["operacao"]
    classificacao = state["classificacao"]
    resultado = state["resultado_cclasstrib"]
    trechos = state.get("contexto_recuperado", [])

    contexto_str = "\n".join(
        f"[{t.documento}]: {t.trecho[:300]}"
        for t in trechos[:4]
    ) if trechos else "(sem trechos recuperados)"

    return f"""Você é um especialista tributário brasileiro. Com base nos trechos regulatórios abaixo,
gere uma justificativa em português para a classificação tributária da operação de frete.

OPERAÇÃO:
- Modal: {operacao.modal}
- Origem/Destino: {operacao.origem_uf} → {operacao.destino_uf}
- Regime tributário: {operacao.regime_tributario}
- Data de emissão: {operacao.data_emissao}
- Transportador autônomo (TAC): {operacao.contratado_pessoa_fisica}

CLASSIFICAÇÃO DETERMINADA:
- Fase de transição: {classificacao.fase_transicao}
- Destaque obrigatório: {classificacao.obrigatoriedade_destaque}
- cClassTrib sugerido: {resultado.cclasstrib if resultado else 'não determinado'}
- Alíquota estimada: {resultado.aliquota_total if resultado else 'N/A'}

TRECHOS REGULATÓRIOS RECUPERADOS:
{contexto_str}

INSTRUÇÕES:
1. Explique por que esta operação se enquadra nesta classificação (2-4 parágrafos)
2. Cite os documentos e artigos usados no campo fontes_citadas
3. Use linguagem técnica mas acessível
4. OBRIGATÓRIO: inclua ao menos uma citação de fonte no campo fontes_citadas

Responda APENAS com um JSON no formato:
{{"justificativa": "...", "fontes_citadas": ["documento - trecho/artigo", ...]}}"""


def generate_justification(state: AgentState) -> dict:
    """
    Nó 5 do grafo. Gera justificativa com LLM local (structured_output via Pydantic).
    Tenta até MAX_TENTATIVAS vezes em caso de falha de formato (R5.3).
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

            # Extrair JSON da resposta
            import json
            import re
            match = re.search(r'\{.*\}', conteudo, re.DOTALL)
            if not match:
                raise ValueError("Resposta não contém JSON válido")

            dados = json.loads(match.group())
            output = JustificativaOutput(**dados)

            # R5.2: verificar que há ao menos uma fonte
            if not output.fontes_citadas:
                raise ValueError("fontes_citadas está vazia — R5.2 violado")

            return {
                "justificativa": output.justificativa,
                "fontes_citadas": output.fontes_citadas,
                "erro": None,
            }

        except Exception as e:
            ultimo_erro = str(e)
            if tentativa < MAX_TENTATIVAS:
                continue  # R5.3: tenta mais uma vez

    # R5.3: após MAX_TENTATIVAS, sinaliza erro
    return {
        "justificativa": None,
        "fontes_citadas": [],
        "erro": f"generate_justification: falhou após {MAX_TENTATIVAS} tentativas. Último erro: {ultimo_erro}",
    }
