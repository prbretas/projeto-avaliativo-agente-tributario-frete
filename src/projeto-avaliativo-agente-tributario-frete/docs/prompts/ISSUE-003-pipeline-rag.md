# ISSUE-003 — Pipeline de ingestão RAG (chunking + embeddings + índice)

**Branch:** `feature/ISSUE-003-pipeline-rag`
**Data:** 06/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Implementação do pipeline RAG

**Prompt enviado:**
> Execute a ISSUE-003: implementar pipeline de ingestão RAG.
> - src/rag/ingestao.py: carregar .txt, chunking 600/100 tokens, embeddings nomic-embed-text, indexar no Chroma
> - recuperar_contexto() com threshold SCORE_MINIMO para sinalizar contexto insuficiente (R2.2)
> - scripts/run_ingestao.py: script para indexar os documentos
> - tests/test_rag_pipeline.py: 2 testes (indexacao e retrieval)

**Resposta resumida:**
- `src/rag/ingestao.py` criado com:
  - `carregar_documentos()`: lê todos os `.txt` de `data/docs_regulatorios/`
  - `fazer_chunking()`: RecursiveCharacterTextSplitter com chunk_size=600, overlap=100
  - `indexar_chroma()`: OllamaEmbeddings + Chroma.from_documents com persistência
  - `carregar_vectorstore()`: carrega índice existente
  - `recuperar_contexto()`: top-k com SCORE_MINIMO=0.3 (retorna lista vazia se insuficiente)
  - `executar_ingestao()`: pipeline completo
- `scripts/run_ingestao.py` criado
- `tests/test_rag_pipeline.py`: `test_indexacao_gera_chunks` PASSED, `test_retrieval` SKIPPED (correto sem índice)
- PR #19 mergeado via squash

---

## [P02] — Correção de problema com arquivos

**Contexto:** Arquivos de ingestao.py e test_rag_pipeline.py não foram encontrados após stash pop — precisaram ser recriados manualmente pelo Kiro.

**Resposta resumida:**
- Kiro identificou que os arquivos haviam sido perdidos no processo de stash/unstash do git
- Recriou `ingestao.py` e `test_rag_pipeline.py` diretamente via `fs_write`
- Adicionou `recuperar_contexto()` mais completo com threshold configurável
