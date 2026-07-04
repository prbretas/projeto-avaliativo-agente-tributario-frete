"""
Nó classify_scenario: classifica o cenário tributário da operação de frete.
Requisito R3 — Classificação do cenário tributário (5 regras).
"""
from datetime import date
from src.schemas.models import AgentState, Classificacao, TrechoRecuperado


def _determinar_fase(data_emissao: str) -> str:
    """Determina a fase de transição tributária baseado na data."""
    d = date.fromisoformat(data_emissao)
    if d.year == 2026:
        return "2026_teste"
    elif 2027 <= d.year <= 2032:
        return "2027_2032_convivencia"
    elif d.year >= 2033:
        return "2033_definitivo"
    else:
        return "regime_especial"  # antes de 2026


def classify_scenario(state: AgentState) -> dict:
    """
    Nó 3 do grafo. Classifica o cenário tributário aplicando as 5 regras do R3.

    Prioridade das regras:
    1. TAC (pessoa física) — R3.5 — regime_especial, não contribuinte
    2. Transporte internacional — R3.4 — imunidade/alíquota zero
    3. Simples Nacional + 2026 — R3.2 — destaque facultativo
    4. Simples Nacional + 2027+ — R3.3 — destaque obrigatório
    5. Regime regular — R3.1 — fase conforme data
    """
    operacao = state.get("operacao")
    if not operacao:
        return {"erro": "classify_scenario: operacao não encontrada no state."}

    contexto = state.get("contexto_recuperado", [])
    contexto_insuficiente = len(contexto) == 0

    # Regra R3.5 — TAC pessoa física
    if operacao.contratado_pessoa_fisica:
        return {
            "classificacao": Classificacao(
                fase_transicao="regime_especial",
                obrigatoriedade_destaque=False,
                observacoes="TAC (transportador autônomo pessoa física): não é contribuinte. "
                            "A obrigação de retenção/recolhimento recai sobre o contratante.",
                contexto_insuficiente=contexto_insuficiente,
            )
        }

    # Regra R3.4 — Transporte internacional
    if operacao.modal == "internacional":
        return {
            "classificacao": Classificacao(
                fase_transicao="regime_especial",
                obrigatoriedade_destaque=True,
                observacoes="Transporte internacional: imunidade/alíquota zero com manutenção "
                            "de crédito sobre insumos. Art. 8º LC 214/2025.",
                contexto_insuficiente=contexto_insuficiente,
            )
        }

    fase = _determinar_fase(operacao.data_emissao)

    # Regra R3.2 — Simples Nacional 2026 (facultativo)
    if operacao.regime_tributario == "simples_nacional" and fase == "2026_teste":
        return {
            "classificacao": Classificacao(
                fase_transicao=fase,
                obrigatoriedade_destaque=False,
                observacoes="Simples Nacional 2026: destaque de IBS/CBS é facultativo. "
                            "Art. 4º LC 214/2025.",
                contexto_insuficiente=contexto_insuficiente,
            )
        }

    # Regra R3.3 — Simples Nacional 2027+ (obrigatório)
    if operacao.regime_tributario == "simples_nacional" and fase in ("2027_2032_convivencia", "2033_definitivo"):
        return {
            "classificacao": Classificacao(
                fase_transicao=fase,
                obrigatoriedade_destaque=True,
                observacoes="Simples Nacional 2027+: destaque de IBS/CBS obrigatório a partir "
                            "de 01/01/2027.",
                contexto_insuficiente=contexto_insuficiente,
            )
        }

    # Regra R3.1 — Regime regular (lucro presumido / lucro real)
    obrigatorio = fase in ("2026_teste", "2027_2032_convivencia", "2033_definitivo")
    return {
        "classificacao": Classificacao(
            fase_transicao=fase,
            obrigatoriedade_destaque=obrigatorio,
            observacoes=f"Regime regular ({operacao.regime_tributario}): destaque IBS/CBS "
                        f"{'obrigatório' if obrigatorio else 'não aplicável'} na fase {fase}.",
            contexto_insuficiente=contexto_insuficiente,
        )
    }
