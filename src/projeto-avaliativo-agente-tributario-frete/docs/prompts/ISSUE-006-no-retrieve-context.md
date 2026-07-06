# ISSUE-006 — Nó retrieve_context

**Branch:** `feature/ISSUE-006-no-retrieve-context`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do nó retrieve_context

**Prompt enviado (subagente):**
> Execute a ISSUE-006. Implementar src/graph/retrieve_context.py:
> - Verificar se o índice Chroma existe antes de consultar
> - Montar query semântica a partir dos campos de Operacao (modal, regime, ano, TAC, internacional)
> - Consultar Chroma via recuperar_contexto() com SCORE_MINIMO
> - Retornar TrechoRecuperado[] ou sinalizar contexto_insuficiente (R2.2)
> - Testes com mocks (sem dependência do Chroma indexado)

**Resposta resumida:**
- `src/graph/retrieve_context.py` criado com:
  - `_montar_query(operacao)`: constrói query a partir do modal, regime, ano, flags TAC/internacional
  - `retrieve_context(state)`: verifica existência do índice Chroma, consulta RAG, retorna TrechoRecuperado[]
  - Contexto insuficiente (lista vazia do RAG): popula campo `erro` com "contexto_insuficiente: ..."
  - Mock do Path.iterdir() necessário para simular presença do índice nos testes
- `tests/test_retrieve_context.py`: 3 testes PASSED com mocks
  - test_retorna_trechos_relevantes, test_contexto_insuficiente_sinalizado, test_sem_operacao_retorna_erro
- PR #22 mergeado via squash
