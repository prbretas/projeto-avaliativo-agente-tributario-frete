# ISSUE-005 — Nó parse_operacao

**Branch:** `feature/ISSUE-005-no-parse-operacao`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do nó parse_operacao

**Prompt enviado (subagente):**
> Execute a ISSUE-005. Implementar src/graph/parse_operacao.py com as regras R1:
> - R1.1: aceitar todos os campos obrigatórios e criar objeto Operacao validado
> - R1.2: detectar campos faltantes e retornar erro descritivo (não assumir padrão)
> - R1.3: data anterior a 01/01/2026 → aviso de fora do escopo no campo erro
> - Aceitar entrada como dict ou objeto Operacao já instanciado

**Resposta resumida:**
- `src/graph/parse_operacao.py` criado com:
  - `parse_operacao(state)`: função pura que retorna dict com chaves `operacao` e `erro`
  - Trata entrada como dict (valida campos obrigatórios antes de criar Operacao) ou Operacao já instanciada
  - Campos faltantes: retorna `{"erro": "Campos obrigatórios ausentes: modal, ..."}` sem prosseguir
  - Data anterior a 2026: popula `erro` com aviso mas **não bloqueia** o fluxo (operacao ainda é retornada)
  - `DATA_MINIMA = date(2026, 1, 1)` e `DATA_MAXIMA = date(2033, 12, 31)`
- `tests/test_parse_operacao.py`: 6 testes PASSED
  - test_dados_completos, test_campo_faltante_solicita_dado, test_data_fora_do_escopo_avisa
  - test_operacao_tac, test_operacao_internacional, test_sem_dados_retorna_erro
- Suite completa: 20 passed
- PR #21 mergeado via squash
