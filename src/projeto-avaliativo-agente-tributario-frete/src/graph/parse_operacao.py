"""
Nó parse_operacao: valida e normaliza os dados de entrada da operação de frete.
Requisito R1 — Entrada de dados da operação.
"""
from datetime import date
from src.schemas.models import AgentState, Operacao


DATA_MINIMA = date(2026, 1, 1)
DATA_MAXIMA = date(2033, 12, 31)


def parse_operacao(state: AgentState) -> dict:
    """
    Nó 1 do grafo. Valida e normaliza os dados da operação.

    Atualiza no state: operacao (Operacao validada) ou erro (str).

    Regras (R1):
    - R1.1: todos os campos obrigatórios devem estar presentes
    - R1.2: se campo faltante, retorna erro descritivo (não assume padrão)
    - R1.3: data anterior a 01/01/2026 → aviso de fora do escopo
    """
    entrada = state.get("operacao")

    # Se já é um objeto Operacao válido, apenas verificar data
    if isinstance(entrada, Operacao):
        operacao = entrada
    elif isinstance(entrada, dict):
        # Validar campos obrigatórios antes de criar Operacao
        campos_obrigatorios = ["modal", "origem_uf", "destino_uf", "regime_tributario", "data_emissao"]
        faltantes = [c for c in campos_obrigatorios if not entrada.get(c)]
        if faltantes:
            return {
                "erro": f"Campos obrigatórios ausentes: {', '.join(faltantes)}. "
                        f"Por favor, forneça: {', '.join(faltantes)}."
            }
        try:
            operacao = Operacao(**entrada)
        except Exception as e:
            return {"erro": f"Dados inválidos: {e}"}
    else:
        return {"erro": "Dados da operação não informados. Forneça modal, origem_uf, destino_uf, regime_tributario e data_emissao."}

    # R1.3: verificar data
    data = date.fromisoformat(operacao.data_emissao)
    avisos = []
    if data < DATA_MINIMA:
        avisos.append(
            f"AVISO: data_emissao {operacao.data_emissao} é anterior a 01/01/2026. "
            "Esta data está fora do escopo de cobertura da base regulatória (transição 2026–2033). "
            "A classificação pode não ser precisa."
        )

    result = {"operacao": operacao, "erro": None}
    if avisos:
        result["erro"] = " | ".join(avisos)
    return result
