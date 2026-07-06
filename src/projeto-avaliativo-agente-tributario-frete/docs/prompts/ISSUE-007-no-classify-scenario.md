# ISSUE-007 — Nó classify_scenario

**Branch:** `feature/ISSUE-007-no-classify-scenario`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do nó classify_scenario com 5 regras R3

**Prompt enviado (subagente):**
> Execute a ISSUE-007. Implementar src/graph/classify_scenario.py com as 5 regras do R3 em ordem de prioridade:
> 1. TAC (pessoa física) — R3.5 — regime_especial, não contribuinte
> 2. Transporte internacional — R3.4 — imunidade/alíquota zero
> 3. Simples Nacional + 2026 — R3.2 — destaque facultativo
> 4. Simples Nacional + 2027+ — R3.3 — destaque obrigatório
> 5. Regime regular — R3.1 — fase conforme data

**Resposta resumida:**
- `src/graph/classify_scenario.py` criado com:
  - `_determinar_fase(data_emissao)`: mapeia ano para "2026_teste", "2027_2032_convivencia", "2033_definitivo", "regime_especial"
  - `classify_scenario(state)`: aplica as 5 regras em ordem de prioridade
  - **Decisão de design:** TAC e internacional sempre retornam `fase_transicao="regime_especial"` independente da data — decisão importante que impactou a tabela na ISSUE-013
  - Flag `contexto_insuficiente` propagada do `contexto_recuperado` vazio
- `tests/test_classify_scenario.py`: 5 testes PASSED (um por regra)
  - test_fase_teste_2026
  - test_simples_nacional_2026_facultativo
  - test_simples_nacional_2027_obrigatorio
  - test_transporte_internacional_imunidade
  - test_tac_pessoa_fisica_nao_contribuinte
- PR #23 mergeado via squash
