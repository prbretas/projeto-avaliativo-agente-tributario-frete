# ISSUE-013 — Golden set e suíte de avaliação

**Branch:** `feature/ISSUE-013-golden-set`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Criação do golden set e script de avaliação

**Prompt enviado:**
> Implementar ISSUE-013:
> - 15 cenários em data/golden_set/cenarios.json com resultado esperado
> - Cobrir: rodoviário Lucro Real 2026/2027, Simples Nacional 2026/2027/2030, internacional, TAC, aéreo, aquaviário, 2033 definitivo
> - scripts/run_golden_set.py: executa os nós determinísticos (sem LLM) e mede taxa de acerto
> - tests/test_golden_set.py: valida taxa >= 80% (R8.2)

**Resposta resumida:**
- `data/golden_set/cenarios.json` criado com 15 cenários (GS-001 a GS-015)
- `scripts/run_golden_set.py` criado com saída formatada mostrando acerto por cenário
- `tests/test_golden_set.py` criado com `test_taxa_de_acerto_minima_80_porcento`

---

## [P02] — Problema detectado: taxa cClassTrib = 60%

**Contexto:** Primeira execução do golden set retornou fase 100% mas cClassTrib apenas 60%.

**Diagnóstico:**
- `classify_scenario` retorna `fase_transicao="regime_especial"` para TAC e internacional
- Mas a `TABELA_CCLASSTRIB` usava `"2026_teste"` como chave para TAC e `"2026_teste"/"2027..."` para internacional
- Resultado: 6 combinações com `regime_especial` não encontradas → `determinado=False`

**Prompt enviado:**
> Expandir TABELA_CCLASSTRIB com entradas usando chave "regime_especial" para TAC (todos os regimes) e internacional (todos os regimes). Adicionar também modais alternativos (aereo, aquaviario) para Simples Nacional.

**Resposta resumida:**
- `tabela_cclasstrib.py` expandido de 9 para 19 entradas:
  - TAC: `("regime_especial", "lucro_real", True, "rodoviario")` → "05"
  - TAC: `("regime_especial", "lucro_presumido", True, "rodoviario")` → "05"
  - TAC: `("regime_especial", "simples_nacional", True, "rodoviario")` → "05"
  - Internacional: `("regime_especial", "lucro_real", False, "internacional")` → "04"
  - Internacional: `("regime_especial", "lucro_presumido", False, "internacional")` → "04"
  - Internacional: `("regime_especial", "simples_nacional", False, "internacional")` → "04"
  - Simples Nacional aereo/aquaviario 2026 e 2027+
- Resultado final: fase 15/15 (100%) e cClassTrib 15/15 (100%) — APROVADO
- Testes afetados corrigidos: `test_tac_nao_contribuinte` em test_tabela_cclasstrib.py e test_determine_cclasstrib.py
- Suite completa: 50 passed, 1 skipped
- PR #30 mergeado via squash
