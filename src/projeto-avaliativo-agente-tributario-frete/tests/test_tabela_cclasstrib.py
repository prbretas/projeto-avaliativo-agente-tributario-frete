from src.tools.tabela_cclasstrib import TABELA_CCLASSTRIB, consultar_cclasstrib, ResultadoCClassTrib


def test_tabela_nao_vazia():
    assert len(TABELA_CCLASSTRIB) >= 8


def test_combinacao_conhecida_retorna_resultado():
    resultado = consultar_cclasstrib("2026_teste", "lucro_real", False, "rodoviario")
    assert resultado.determinado is True
    assert resultado.cclasstrib is not None
    assert resultado.aliquota_total == 0.01


def test_simples_nacional_2026_facultativo():
    resultado = consultar_cclasstrib("2026_teste", "simples_nacional", False, "rodoviario")
    assert resultado.determinado is True
    assert resultado.aliquota_total == 0.0


def test_transporte_internacional_imunidade():
    resultado = consultar_cclasstrib("2026_teste", "lucro_real", False, "internacional")
    assert resultado.determinado is True
    assert resultado.aliquota_total == 0.0


def test_tac_nao_contribuinte():
    # TAC usa fase "regime_especial" conforme classify_scenario
    resultado = consultar_cclasstrib("regime_especial", "lucro_real", True, "rodoviario")
    assert resultado.determinado is True
    assert resultado.cclasstrib == "05"


def test_combinacao_desconhecida_retorna_nao_determinado():
    resultado = consultar_cclasstrib("9999_futuro", "regime_invalido", False, "rodoviario")
    assert resultado.determinado is False
    assert resultado.cclasstrib is None
