# ISSUE-008 — Nó determine_cclasstrib

**Branch:** `feature/ISSUE-008-no-determine-cclasstrib`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do nó determine_cclasstrib

**Prompt enviado:**
> Implementar src/graph/determine_cclasstrib.py. O nó deve consultar a TABELA_CCLASSTRIB determinística (nunca LLM) e retornar o cClassTrib. Se combinação não mapeada: determinado=False + sinalizar revisão manual (R4.2).

**Resposta resumida:**
- `src/graph/determine_cclasstrib.py` criado com:
  - Importa `consultar_cclasstrib` de `src.tools.tabela_cclasstrib`
  - Constrói chave `(fase_transicao, regime_tributario, contratado_pessoa_fisica, modal)` a partir do state
  - Retorna `{"resultado_cclasstrib": resultado, "erro": None}` se determinado
  - Retorna `{"resultado_cclasstrib": resultado, "erro": "classificacao_nao_determinada: ..."}` se não mapeado
- `tests/test_determine_cclasstrib.py`: 6 testes PASSED
  - test_combinacao_conhecida, test_combinacao_desconhecida_marca_revisao_manual
  - test_simples_nacional_2026, test_tac_nao_contribuinte, test_transporte_internacional
  - test_sem_classificacao_retorna_erro

---

## [P02] — Correção do teste TAC

**Contexto:** Após expansão da tabela na ISSUE-013, o teste `test_tac_nao_contribuinte` usava a chave antiga `("2026_teste", ...)` mas TAC passou a ser `("regime_especial", ...)`.

**Prompt enviado:**
> Corrigir test_tac_nao_contribuinte para usar a chave "regime_especial" conforme o classify_scenario retorna.

**Resposta resumida:**
- Teste corrigido: `consultar_cclasstrib("regime_especial", "lucro_real", True, "rodoviario")`
- PR #25 mergeado via squash
