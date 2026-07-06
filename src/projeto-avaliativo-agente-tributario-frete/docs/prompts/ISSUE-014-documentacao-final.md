# ISSUE-014 — Documentação final e demo

**Branch:** `feature/ISSUE-014-documentacao-final`
**Data:** 06-07/07/2026
**Ferramenta:** Kiro (Claude)

---

## [P01] — Análise dos critérios do professor

**Prompt enviado:**
> Aqui está o projeto avaliativo do professor. Confira se estamos no caminho de atingir todos os requisitos.

**Resposta resumida:**
- Kiro analisou o documento [M2S05] Mini-Projeto Avaliativo.docx e comparou com o estado atual do projeto
- Critérios analisados:
  - ✅ Critério 1: Versionamento com branches e commits semânticos — completo
  - ✅ Critério 2: Contribuição individual — completo
  - ⚠️ Critério 3: Documentação e prompts — faltam README completo e arquivos de prompts por issue
  - ⚠️ Critério 4: Slides de apresentação — não criados ainda
  - ✅ Critério 5: LangGraph — completo
  - ✅ Critério 6: Ferramenta integrada — completo (RAG, tabela, API, JSON)
  - ✅ Critério 7: Segurança — completo
  - ✅ Critério 8: Contexto, memória e validação — completo

---

## [P02] — Criação das issues de documentação

**Prompt enviado:**
> Crie as issues no GitHub para concluirmos o critério 3 e o critério 4. Aproveite e já busque os prompts desde o início do desenvolvimento. Salve os prompts em arquivos separados, para cada issue criada.

**Resposta resumida:**
- ISSUE-015 criada no GitHub: README.md completo conforme critérios do professor
- ISSUE-016 criada no GitHub: Arquivo de prompts por issue (docs/prompts/)
- ISSUE-017 criada no GitHub: Slides de apresentação (2 slides)
- Arquivos criados:
  - docs/prompts/ISSUE-001-setup-ambiente.md
  - docs/prompts/ISSUE-002-base-regulatoria.md
  - docs/prompts/ISSUE-003-pipeline-rag.md
  - docs/prompts/ISSUE-004-schemas.md
  - docs/prompts/ISSUE-005-no-parse-operacao.md
  - docs/prompts/ISSUE-006-no-retrieve-context.md
  - docs/prompts/ISSUE-007-no-classify-scenario.md
  - docs/prompts/ISSUE-008-no-determine-cclasstrib.md
  - docs/prompts/ISSUE-009-no-generate-justification.md
  - docs/prompts/ISSUE-010-no-human-review.md
  - docs/prompts/ISSUE-011-export-api-checkpointer.md
  - docs/prompts/ISSUE-012-montagem-grafo.md
  - docs/prompts/ISSUE-013-golden-set.md
  - docs/prompts/ISSUE-014-documentacao-final.md (este arquivo)

**Pendências para entrega:**
- [ ] README.md — adicionar exemplos de entrada/saída, decisões tomadas, limitações (ISSUE-015)
- [ ] 2 slides de apresentação (ISSUE-017) — a fazer manualmente
- [ ] Submissão no AVA até 20/07/2026 22h
