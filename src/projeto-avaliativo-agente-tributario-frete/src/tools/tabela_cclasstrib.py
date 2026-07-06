"""
Tabela determinística de classificação tributária para frete (CT-e).
Fonte: LC 214/2025 e Notas Técnicas do CT-e.
IMPORTANTE: Esta tabela NÃO é gerada por LLM. É um lookup determinístico.
"""
from src.schemas.models import ResultadoCClassTrib


# Chave: (fase_transicao, regime_tributario, contratado_pessoa_fisica, modal)
# fase_transicao: "2026_teste" | "2027_2032_convivencia" | "2033_definitivo" | "regime_especial"
# regime_tributario: "simples_nacional" | "lucro_presumido" | "lucro_real"
# contratado_pessoa_fisica: True = TAC, False = empresa transportadora
# modal: "rodoviario" | "aereo" | "aquaviario" | "internacional"

TABELA_CCLASSTRIB: dict[tuple[str, str, bool, str], ResultadoCClassTrib] = {
    # Regime regular 2026 - fase teste (rodoviário)
    ("2026_teste", "lucro_real", False, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="01",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Fase-teste 2026: aliquota somada 1% (0,9% CBS + 0,1% IBS). Art. 337 LC 214/2025."
    ),
    ("2026_teste", "lucro_presumido", False, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="01",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Fase-teste 2026: aliquota somada 1% (0,9% CBS + 0,1% IBS). Art. 337 LC 214/2025."
    ),
    # Simples Nacional 2026 - destaque facultativo
    ("2026_teste", "simples_nacional", False, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="02",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Simples Nacional 2026: destaque de IBS/CBS facultativo. Art. 4 LC 214/2025."
    ),
    # Simples Nacional 2027+ - destaque obrigatório
    ("2027_2032_convivencia", "simples_nacional", False, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="03",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Simples Nacional 2027+: destaque obrigatorio a partir de 01/01/2027."
    ),
    # Regime regular 2027+ (convivencia)
    ("2027_2032_convivencia", "lucro_real", False, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="01",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Periodo de convivencia 2027-2032: aliquotas progressivas conforme Anexo LC 214/2025."
    ),
    # Transporte internacional - imunidade
    ("2026_teste", "lucro_real", False, "internacional"): ResultadoCClassTrib(
        cclasstrib="04",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Transporte internacional: imunidade/aliquota zero com manutencao de credito. Art. 8 LC 214/2025."
    ),
    ("2027_2032_convivencia", "lucro_real", False, "internacional"): ResultadoCClassTrib(
        cclasstrib="04",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Transporte internacional: imunidade/aliquota zero. Art. 8 LC 214/2025."
    ),
    # TAC - transportador autônomo pessoa física (regime_especial — independe de fase/regime)
    ("regime_especial", "lucro_real", True, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="05",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="TAC (pessoa fisica): nao e contribuinte. Obrigacao recai sobre o contratante."
    ),
    ("regime_especial", "lucro_presumido", True, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="05",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="TAC (pessoa fisica): nao e contribuinte. Obrigacao recai sobre o contratante."
    ),
    ("regime_especial", "simples_nacional", True, "rodoviario"): ResultadoCClassTrib(
        cclasstrib="05",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="TAC (pessoa fisica): nao e contribuinte. Obrigacao recai sobre o contratante."
    ),
    # Transporte internacional (regime_especial — independe de fase)
    ("regime_especial", "lucro_real", False, "internacional"): ResultadoCClassTrib(
        cclasstrib="04",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Transporte internacional: imunidade/aliquota zero. Art. 8 LC 214/2025."
    ),
    ("regime_especial", "lucro_presumido", False, "internacional"): ResultadoCClassTrib(
        cclasstrib="04",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Transporte internacional: imunidade/aliquota zero. Art. 8 LC 214/2025."
    ),
    ("regime_especial", "simples_nacional", False, "internacional"): ResultadoCClassTrib(
        cclasstrib="04",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Transporte internacional: imunidade/aliquota zero. Art. 8 LC 214/2025."
    ),
    # Simples Nacional 2027-2032 convivência (outros modais)
    ("2027_2032_convivencia", "simples_nacional", False, "aereo"): ResultadoCClassTrib(
        cclasstrib="03",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Simples Nacional 2027+: destaque obrigatorio."
    ),
    ("2027_2032_convivencia", "simples_nacional", False, "aquaviario"): ResultadoCClassTrib(
        cclasstrib="03",
        aliquota_cbs=0.009, aliquota_ibs=0.001, aliquota_total=0.01,
        determinado=True,
        observacao="Simples Nacional 2027+: destaque obrigatorio."
    ),
    # Simples Nacional 2026 - outros modais
    ("2026_teste", "simples_nacional", False, "aereo"): ResultadoCClassTrib(
        cclasstrib="02",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Simples Nacional 2026: destaque facultativo."
    ),
    ("2026_teste", "simples_nacional", False, "aquaviario"): ResultadoCClassTrib(
        cclasstrib="02",
        aliquota_cbs=0.0, aliquota_ibs=0.0, aliquota_total=0.0,
        determinado=True,
        observacao="Simples Nacional 2026: destaque facultativo."
    ),
}


def consultar_cclasstrib(
    fase_transicao: str,
    regime_tributario: str,
    contratado_pessoa_fisica: bool,
    modal: str
) -> ResultadoCClassTrib:
    """
    Consulta a tabela determinística e retorna o ResultadoCClassTrib.
    Se não encontrar combinação exata, retorna determinado=False.
    """
    chave = (fase_transicao, regime_tributario, contratado_pessoa_fisica, modal)
    resultado = TABELA_CCLASSTRIB.get(chave)
    if resultado:
        return resultado
    return ResultadoCClassTrib(
        cclasstrib=None,
        aliquota_cbs=None,
        aliquota_ibs=None,
        aliquota_total=None,
        determinado=False,
        observacao=f"Combinacao nao mapeada: {chave}. Requer revisao manual."
    )
