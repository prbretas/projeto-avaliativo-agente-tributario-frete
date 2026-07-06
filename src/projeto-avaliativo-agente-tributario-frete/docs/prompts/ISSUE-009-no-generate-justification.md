# ISSUE-009 — Nó generate_justification

**Branch:** `feature/ISSUE-009-no-generate-justification`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do nó generate_justification

**Prompt enviado:**
> Implementar src/graph/generate_justification.py. LLM local llama3.2 via ChatOllama.
> - R5.1: justificativa em português citando trechos do RAG
> - R5.2: fontes_citadas obrigatório — erro se vazio
> - R5.3: retry automático único em caso de falha de formato JSON
> - structured_output via Pydantic (JustificativaOutput)
> - Testes com mocks do LLM — sem chamada real ao Ollama

**Resposta resumida:**
- `src/graph/generate_justification.py` criado com:
  - `JustificativaOutput(BaseModel)`: schema Pydantic com `justificativa: str` e `fontes_citadas: list[str]`
  - `_montar_prompt(state)`: monta prompt completo com dados da operação, classificação e trechos RAG (até 4, 300 chars cada)
  - `generate_justification(state)`: invoca `ChatOllama(model="llama3.2:latest", temperature=0.1)`
  - Parse do JSON com `re.search(r'\{.*\}', ...)` — extrai JSON da resposta do LLM
  - Loop `for tentativa in range(1, MAX_TENTATIVAS + 1)` com `MAX_TENTATIVAS = 2`
  - R5.2: verifica `if not output.fontes_citadas: raise ValueError("fontes_citadas vazia")`
- `tests/test_generate_justification.py`: 5 testes PASSED com mocks
  - test_justificativa_contem_fonte
  - test_retry_em_falha_de_formato
  - test_falha_total_retorna_erro
  - test_sem_fontes_retorna_erro
  - test_sem_classificacao_retorna_erro
- PR #26 mergeado via squash
