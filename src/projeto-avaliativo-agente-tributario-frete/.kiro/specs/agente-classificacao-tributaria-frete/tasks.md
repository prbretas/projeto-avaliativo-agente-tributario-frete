# Tasks: Agente de Classificação Tributária de Frete (RAG + LangGraph)

Cada task abaixo é uma **Issue**. Convenções obrigatórias (ver `.kiro/steering/workflow.md`):

- Branch: `feature/ISSUE-XXX-slug-curto`, criada a partir de `main` atualizada.
- Antes do primeiro commit da issue: salvar o prompt usado em
  `docs/prompts/ISSUE-XXX-slug-curto.md` (ver `docs/prompts/README.md`).
- Nenhum commit sem teste correspondente passando localmente (`pytest`).
- Coluna inicial no Kanban (`docs/kanban.md`): **Backlog**.

---

## ISSUE-001 — Setup do ambiente e estrutura do projeto

**Requisitos:** R1 (pré-condição) · **Branch:** `feature/ISSUE-001-setup-ambiente`

- [ ] Criar venv, instalar `langgraph`, `langchain`, `langchain-ollama`, `chromadb`, `pydantic`, `pytest`
- [ ] Instalar Ollama + baixar `llama3.1:8b` e `nomic-embed-text`
- [ ] Criar estrutura de pastas conforme `.kiro/steering/structure.md`
- [ ] Configurar `.githooks/pre-commit` (`git config core.hooksPath .githooks`)

**Casos de teste:**
- `test_environment.py::test_ollama_responde` — chamada simples ao modelo local retorna texto não vazio.

---

## ISSUE-002 — Base de conhecimento regulatória (RAG - fonte de dados)

**Requisitos:** R2 · **Branch:** `feature/ISSUE-002-base-regulatoria`

- [ ] Reunir trechos da LC 214/2025 relevantes a transporte de cargas
- [ ] Reunir resumos das Notas Técnicas do CT-e (NT 2025.001) e cronograma 2026–2033
- [ ] Montar `TABELA_CCLASSTRIB` inicial (mínimo 8 combinações cobrindo os cenários do requisito 3)

**Casos de teste:**
- `test_tabela_cclasstrib.py::test_tabela_nao_vazia`
- `test_tabela_cclasstrib.py::test_combinacao_conhecida_retorna_resultado`

---

## ISSUE-003 — Pipeline de ingestão RAG (chunking + embeddings + índice)

**Requisitos:** R2 · **Branch:** `feature/ISSUE-003-pipeline-rag`

- [ ] Implementar chunking dos documentos de `/data/docs_regulatorios`
- [ ] Gerar embeddings com `nomic-embed-text`
- [ ] Indexar no Chroma (`/data/chroma_db`)

**Casos de teste:**
- `test_rag_pipeline.py::test_indexacao_gera_chunks`
- `test_rag_pipeline.py::test_retrieval_traz_trecho_relevante`

---

## ISSUE-004 — Modelos de dados (State e schemas Pydantic)

**Requisitos:** design.md seção 2 · **Branch:** `feature/ISSUE-004-schemas`

- [ ] Implementar `Operacao`, `TrechoRecuperado`, `Classificacao`, `ResultadoCClassTrib`, `AgentState`

**Casos de teste:**
- `test_schemas.py::test_operacao_valida`
- `test_schemas.py::test_operacao_invalida_rejeitada`

---

## ISSUE-005 — Nó `parse_operacao`

**Requisitos:** R1 · **Branch:** `feature/ISSUE-005-no-parse-operacao`

- [ ] Implementar validação e normalização dos dados de entrada
- [ ] Tratar campo obrigatório ausente (requisito 1.2)
- [ ] Tratar data anterior a 01/01/2026 (requisito 1.3)

**Casos de teste:**
- `test_parse_operacao.py::test_dados_completos`
- `test_parse_operacao.py::test_campo_faltante_solicita_dado`
- `test_parse_operacao.py::test_data_fora_do_escopo_avisa`

---

## ISSUE-006 — Nó `retrieve_context`

**Requisitos:** R2 · **Branch:** `feature/ISSUE-006-no-retrieve-context`

- [ ] Consultar Chroma a partir dos dados da operação
- [ ] Sinalizar `contexto_insuficiente` quando score abaixo do mínimo (requisito 2.2)

**Casos de teste:**
- `test_retrieve_context.py::test_retorna_trechos_relevantes`
- `test_retrieve_context.py::test_contexto_insuficiente_sinalizado`

---

## ISSUE-007 — Nó `classify_scenario`

**Requisitos:** R3 · **Branch:** `feature/ISSUE-007-no-classify-scenario`

- [ ] Implementar as 5 regras de classificação (fase-teste 2026, Simples Nacional 2026 vs 2027+, transporte internacional, TAC pessoa física)

**Casos de teste (um por regra do requisito 3):**
- `test_classify_scenario.py::test_fase_teste_2026`
- `test_classify_scenario.py::test_simples_nacional_2026_facultativo`
- `test_classify_scenario.py::test_simples_nacional_2027_obrigatorio`
- `test_classify_scenario.py::test_transporte_internacional_imunidade`
- `test_classify_scenario.py::test_tac_pessoa_fisica_nao_contribuinte`

---

## ISSUE-008 — Nó `determine_cclasstrib`

**Requisitos:** R4 · **Branch:** `feature/ISSUE-008-no-determine-cclasstrib`

- [ ] Consultar `TABELA_CCLASSTRIB`
- [ ] Retornar `determinado=False` quando não houver correspondência (requisito 4.2)

**Casos de teste:**
- `test_determine_cclasstrib.py::test_combinacao_conhecida`
- `test_determine_cclasstrib.py::test_combinacao_desconhecida_marca_revisao_manual`

---

## ISSUE-009 — Nó `generate_justification`

**Requisitos:** R5 · **Branch:** `feature/ISSUE-009-no-generate-justification`

- [ ] Prompt com `structured_output` (Pydantic) citando `fontes_citadas`
- [ ] Retry único em caso de falha de formato (requisito 5.3)

**Casos de teste:**
- `test_generate_justification.py::test_justificativa_contem_fonte`
- `test_generate_justification.py::test_retry_em_falha_de_formato`

---

## ISSUE-010 — Nó `human_review` (human-in-the-loop)

**Requisitos:** R6 · **Branch:** `feature/ISSUE-010-no-human-review`

- [ ] Implementar `interrupt()` do LangGraph
- [ ] Fluxo de rejeição volta para `classify_scenario`

**Casos de teste:**
- `test_human_review.py::test_interrupt_pausa_execucao`
- `test_human_review.py::test_rejeicao_permite_reclassificacao`

---

## ISSUE-011 — Nó `export_result` + checkpointer SQLite

**Requisitos:** R7 · **Branch:** `feature/ISSUE-011-export-e-checkpointer`

- [ ] Exportar JSON/CSV do resultado final
- [ ] Configurar `SqliteSaver`

**Casos de teste:**
- `test_export_result.py::test_json_contem_campos_obrigatorios`
- `test_export_result.py::test_checkpoint_persistido`

---

## ISSUE-012 — Montagem do grafo completo (edges condicionais)

**Requisitos:** todos · **Branch:** `feature/ISSUE-012-montagem-grafo`

- [ ] Conectar todos os nós com `StateGraph`
- [ ] Implementar edges condicionais (regime, modal, fase)

**Casos de teste:**
- `test_graph_e2e.py::test_fluxo_completo_happy_path`
- `test_graph_e2e.py::test_fluxo_com_rejeicao_humana`

---

## ISSUE-013 — Golden set e suíte de avaliação

**Requisitos:** R8 · **Branch:** `feature/ISSUE-013-golden-set`

- [ ] Criar 15–20 cenários em `/data/golden_set` com resultado esperado
- [ ] Script de avaliação (`scripts/run_golden_set.py`) medindo taxa de acerto

**Casos de teste:**
- `test_golden_set.py::test_taxa_de_acerto_minima_80_porcento`

---

## ISSUE-014 — Documentação final e demo

**Requisitos:** entrega da avaliação M2.1 · **Branch:** `feature/ISSUE-014-documentacao-final`

- [ ] `README.md` com propósito, arquitetura, como rodar localmente
- [ ] Gravação de demo (se exigido pelo AVA)
- [ ] Revisão final e submissão até 20/07/2026 15h

**Casos de teste:** N/A (documentação) — checklist manual de revisão.
