$gh   = "C:\Program Files\GitHub CLI\gh.exe"
$repo = "prbretas/agenteclasstrib"

$issues = @(
  @{
    title  = "ISSUE-001: Setup do ambiente e estrutura do projeto"
    labels = "chore,setup,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-001-setup-ambiente``

## Descricao
Preparar o ambiente de desenvolvimento completo.

## Tarefas
- [ ] Criar venv + instalar: langgraph, langchain, langchain-ollama, chromadb, pydantic, fastapi, uvicorn, pytest
- [ ] Instalar Ollama + baixar llama3.1:8b e nomic-embed-text
- [ ] Criar estrutura de pastas: /src/graph, /src/rag, /src/tools, /src/schemas, /data/docs_regulatorios, /data/golden_set, /tests
- [ ] Criar requirements.txt
- [ ] Configurar .githooks/pre-commit

## Casos de teste
- test_environment.py::test_ollama_responde

## Prioridade e dependencias
**Prioridade:** CRITICA
**Depende de:** nenhuma (issue inicial, precede todas as demais)
"@
  },
  @{
    title  = "ISSUE-002: Base de conhecimento regulatoria (RAG - fonte de dados)"
    labels = "story,rag,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-002-base-regulatoria``

## Descricao
Reunir e organizar os documentos regulatorios que alimentarao o RAG.

## Tarefas
- [ ] Reunir trechos da LC 214/2025 relevantes a transporte de cargas
- [ ] Reunir resumos das Notas Tecnicas do CT-e (NT 2025.001) e cronograma 2026-2033
- [ ] Montar TABELA_CCLASSTRIB inicial (minimo 8 combinacoes cobrindo os cenarios do requisito R3)

## Casos de teste
- test_tabela_cclasstrib.py::test_tabela_nao_vazia
- test_tabela_cclasstrib.py::test_combinacao_conhecida_retorna_resultado

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #1 (ISSUE-001)
**Pode rodar em paralelo com:** ISSUE-004
"@
  },
  @{
    title  = "ISSUE-003: Pipeline de ingestao RAG (chunking + embeddings + indice)"
    labels = "story,rag,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-003-pipeline-rag``

## Descricao
Implementar o pipeline que processa os documentos regulatorios e cria o indice vetorial no Chroma.

## Tarefas
- [ ] Implementar chunking dos documentos de /data/docs_regulatorios (500-800 tokens, overlap 100)
- [ ] Gerar embeddings com nomic-embed-text via Ollama
- [ ] Indexar no Chroma (/data/chroma_db)

## Casos de teste
- test_rag_pipeline.py::test_indexacao_gera_chunks
- test_rag_pipeline.py::test_retrieval_traz_trecho_relevante

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #1 (ISSUE-001), #2 (ISSUE-002)
**Bloqueia:** ISSUE-006
"@
  },
  @{
    title  = "ISSUE-004: Modelos de dados (State e schemas Pydantic)"
    labels = "story,data-model,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-004-schemas``

## Descricao
Definir e implementar todos os modelos de dados usados no grafo LangGraph.

## Tarefas
- [ ] Implementar Operacao, TrechoRecuperado, Classificacao, ResultadoCClassTrib, AgentState
- [ ] Validar que todos os campos obrigatorios sao exigidos pelo Pydantic
- [ ] Garantir compatibilidade com o StateGraph do LangGraph

## Casos de teste
- test_schemas.py::test_operacao_valida
- test_schemas.py::test_operacao_invalida_rejeitada

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #1 (ISSUE-001)
**Pode rodar em paralelo com:** ISSUE-002
**Bloqueia:** ISSUE-005, ISSUE-006, ISSUE-007, ISSUE-008, ISSUE-009, ISSUE-010, ISSUE-011
"@
  },
  @{
    title  = "ISSUE-005: No parse_operacao"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-005-no-parse-operacao``

## Descricao
Implementar o primeiro no do grafo: recebe o input bruto do usuario, valida e normaliza os dados da operacao de frete.

## Tarefas
- [ ] Implementar validacao e normalizacao dos dados de entrada
- [ ] Tratar campo obrigatorio ausente (R1.2): solicitar dado faltante
- [ ] Tratar data anterior a 01/01/2026 (R1.3): emitir aviso de fora do escopo

## Casos de teste
- test_parse_operacao.py::test_dados_completos
- test_parse_operacao.py::test_campo_faltante_solicita_dado
- test_parse_operacao.py::test_data_fora_do_escopo_avisa

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #1 (ISSUE-001), #4 (ISSUE-004)
"@
  },
  @{
    title  = "ISSUE-006: No retrieve_context"
    labels = "story,rag,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-006-no-retrieve-context``

## Descricao
Implementar o no de recuperacao de contexto regulatorio via RAG (consulta ao Chroma).

## Tarefas
- [ ] Consultar Chroma a partir dos dados da operacao
- [ ] Aplicar score minimo configuravel
- [ ] Sinalizar contexto_insuficiente quando score abaixo do minimo (R2.2)

## Casos de teste
- test_retrieve_context.py::test_retorna_trechos_relevantes
- test_retrieve_context.py::test_contexto_insuficiente_sinalizado

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #3 (ISSUE-003), #4 (ISSUE-004)
"@
  },
  @{
    title  = "ISSUE-007: No classify_scenario"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-007-no-classify-scenario``

## Descricao
Implementar o no de classificacao do cenario tributario com as 5 regras de negocio do R3.

## Tarefas
- [ ] Regra 1: fase-teste 2026 (aliquota 1%)
- [ ] Regra 2: Simples Nacional 2026 - destaque facultativo
- [ ] Regra 3: Simples Nacional 2027+ - destaque obrigatorio
- [ ] Regra 4: transporte internacional - imunidade/aliquota zero
- [ ] Regra 5: TAC pessoa fisica - nao contribuinte, obrigacao no contratante

## Casos de teste
- test_classify_scenario.py::test_fase_teste_2026
- test_classify_scenario.py::test_simples_nacional_2026_facultativo
- test_classify_scenario.py::test_simples_nacional_2027_obrigatorio
- test_classify_scenario.py::test_transporte_internacional_imunidade
- test_classify_scenario.py::test_tac_pessoa_fisica_nao_contribuinte

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #4 (ISSUE-004), #6 (ISSUE-006)
**Bloqueia:** ISSUE-008
"@
  },
  @{
    title  = "ISSUE-008: No determine_cclasstrib"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-008-no-determine-cclasstrib``

## Descricao
Implementar o no de determinacao do codigo cClassTrib usando tabela deterministica (nao LLM).

## Tarefas
- [ ] Consultar TABELA_CCLASSTRIB (lookup deterministico em Python)
- [ ] Retornar determinado=False quando nao houver correspondencia (R4.2)
- [ ] Apresentar aliquota estimada junto ao codigo (R4.3)

## Casos de teste
- test_determine_cclasstrib.py::test_combinacao_conhecida
- test_determine_cclasstrib.py::test_combinacao_desconhecida_marca_revisao_manual

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #2 (ISSUE-002), #7 (ISSUE-007)
**Bloqueia:** ISSUE-009
"@
  },
  @{
    title  = "ISSUE-009: No generate_justification"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-009-no-generate-justification``

## Descricao
Implementar o no de geracao de justificativa em linguagem natural com LLM local e structured_output.

## Tarefas
- [ ] Prompt com structured_output (Pydantic) citando fontes_citadas
- [ ] Garantir que toda resposta contenha ao menos uma citacao de fonte (R5.2)
- [ ] Retry automatico unico em caso de falha de formato (R5.3)

## Casos de teste
- test_generate_justification.py::test_justificativa_contem_fonte
- test_generate_justification.py::test_retry_em_falha_de_formato

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #8 (ISSUE-008)
**Bloqueia:** ISSUE-010
"@
  },
  @{
    title  = "ISSUE-010: No human_review (human-in-the-loop)"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-010-no-human-review``

## Descricao
Implementar o ponto de validacao humana usando interrupt() do LangGraph.

## Tarefas
- [ ] Implementar interrupt() do LangGraph para pausar o grafo
- [ ] Fluxo de rejeicao: retorna para classify_scenario
- [ ] Fluxo de aprovacao: avanca para export_result

## Casos de teste
- test_human_review.py::test_interrupt_pausa_execucao
- test_human_review.py::test_rejeicao_permite_reclassificacao

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #9 (ISSUE-009)
**Bloqueia:** ISSUE-011
"@
  },
  @{
    title  = "ISSUE-011: No export_result + API REST + checkpointer SQLite"
    labels = "story,api,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-011-export-api-checkpointer``

## Descricao
Implementar exportacao do resultado em JSON e API REST com FastAPI para integracao externa.

## Endpoints
- POST /classificar - dispara o agente
- GET /classificar/{thread_id}/review - consulta resultado pendente
- POST /classificar/{thread_id}/review - aprova ou rejeita

## Tarefas
- [ ] Exportar resultado em JSON ao aprovar
- [ ] Implementar API REST com FastAPI (3 endpoints acima)
- [ ] Configurar SqliteSaver para persistencia de estado por thread_id

## Casos de teste
- test_export_result.py::test_json_contem_campos_obrigatorios
- test_export_result.py::test_checkpoint_persistido
- test_api.py::test_post_classificar_retorna_thread_id
- test_api.py::test_review_endpoint_aprova_resultado

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #10 (ISSUE-010)
**Bloqueia:** ISSUE-012
"@
  },
  @{
    title  = "ISSUE-012: Montagem do grafo completo (edges condicionais)"
    labels = "story,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-012-montagem-grafo``

## Descricao
Conectar todos os nos do grafo com StateGraph e implementar as edges condicionais.

## Tarefas
- [ ] Conectar todos os nos com StateGraph
- [ ] Implementar edges condicionais por regime tributario, modal e fase da transicao
- [ ] Validar fluxo completo end-to-end (happy path e rejeicao humana)

## Casos de teste
- test_graph_e2e.py::test_fluxo_completo_happy_path
- test_graph_e2e.py::test_fluxo_com_rejeicao_humana

## Prioridade e dependencias
**Prioridade:** CRITICA
**Depende de:** #5, #6, #7, #8, #9, #10, #11 (todos os nos implementados)
**Bloqueia:** ISSUE-013
"@
  },
  @{
    title  = "ISSUE-013: Golden set e suite de avaliacao"
    labels = "test,ai,priority:high"
    body   = @"
**Branch:** ``feature/ISSUE-013-golden-set``

## Descricao
Criar o golden set de cenarios representativos e validar a taxa de acerto do agente (meta: >= 80%).

## Tarefas
- [ ] Criar 15-20 cenarios em /data/golden_set com resultado esperado (JSON)
- [ ] Cobrir: rodoviario interestadual, Simples Nacional 2026, Simples Nacional 2027, transporte internacional, TAC pessoa fisica, Lucro Real 2026 vs 2027
- [ ] Implementar script scripts/run_golden_set.py medindo taxa de acerto
- [ ] Atingir >= 80% de acerto na classificacao de cenario e cClassTrib (R8.2)

## Casos de teste
- test_golden_set.py::test_taxa_de_acerto_minima_80_porcento

## Prioridade e dependencias
**Prioridade:** ALTA
**Depende de:** #12 (ISSUE-012 - grafo completo montado)
**Bloqueia:** ISSUE-014
"@
  },
  @{
    title  = "ISSUE-014: Documentacao final e demo"
    labels = "docs,priority:medium"
    body   = @"
**Branch:** ``feature/ISSUE-014-documentacao-final``

## Descricao
Finalizar a documentacao do projeto e preparar para entrega da avaliacao M2.1.

## Tarefas
- [ ] Atualizar README.md com arquitetura final, diagrama do grafo e instrucoes de execucao
- [ ] Documentar endpoints da API REST
- [ ] Documentar fontes regulatorias usadas na base RAG (com links/versoes)
- [ ] Gravar demonstracao do fluxo completo (se exigido pelo AVA)
- [ ] Revisao final e submissao no AVA ate 20/07/2026 15h

## Casos de teste
N/A - checklist manual de revisao.

## Prioridade e dependencias
**Prioridade:** MEDIA
**Depende de:** #13 (ISSUE-013)
**Prazo:** 20/07/2026 15h
"@
  }
)

foreach ($issue in $issues) {
  $result = & $gh issue create --repo $repo --title $issue.title --label $issue.labels --body $issue.body 2>&1
  Write-Host $result
}

Write-Host "Todas as issues criadas!"
