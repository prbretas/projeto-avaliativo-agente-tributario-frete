# ISSUE-004 — Modelos de dados (State e schemas Pydantic)

**Branch:** `feature/ISSUE-004-schemas`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação dos schemas Pydantic

**Prompt enviado:**
> Execute a ISSUE-004: implementar Operacao, TrechoRecuperado, Classificacao, ResultadoCClassTrib, AgentState em src/schemas/models.py. Ser a fonte única de todos os modelos — tabela_cclasstrib.py deve importar daqui.

**Resposta resumida:**
- `src/schemas/models.py` criado com:
  - `Operacao`: validação de UF (normaliza maiúsculas, aceita EX para internacional), data ISO 8601, modal Literal
  - `TrechoRecuperado`: documento, trecho, score
  - `Classificacao`: fase_transicao Literal, obrigatoriedade_destaque, contexto_insuficiente (flag R2.2)
  - `ResultadoCClassTrib`: fonte única (tabela importa daqui)
  - `AgentState`: TypedDict com todos os campos + campo `erro`
  - `OperacaoRequest`, `ClassificacaoResponse`, `ReviewRequest`: schemas da API REST
- `tabela_cclasstrib.py` refatorado para importar `ResultadoCClassTrib` de `models.py`
- `tests/test_schemas.py`: 8 testes PASSED (validação válida, inválida, data, UF normalizada, state)
- Suite completa: 16 passed, 1 skipped
- PR #20 mergeado via squash
