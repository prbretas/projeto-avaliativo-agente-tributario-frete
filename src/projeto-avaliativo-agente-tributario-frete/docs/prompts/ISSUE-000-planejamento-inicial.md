# ISSUE-000 — Planejamento inicial do projeto

Prompts trocados antes da criação formal das issues em `tasks.md`, durante a fase de definição de
escopo, arquitetura e specs do Kiro para a avaliação M2.1.

**Ferramenta/modelo:** Claude (Claude.ai), sessão de planejamento — 04/07/2026.

---

## [P01]

**Prompt enviado:**
> Avaliação M2.1 (30% do módulo): Mini-Projeto em squads (ou individual)... Criar um agente
> funcional usando LangGraph que automatize um processo real como PR Reviewer, pipeline
> inteligente, documentação viva (usando RAG) ou outro... EU PENSEI EM AGENTE PARA QUE EU POSSA
> EXECUTAR ALGO RELACIONADO A REFORMA TRIBUTÁRIA. ME DE IDEIAS DO QUE PODERIA CRIAR... QUERO QUE
> JA DEIXE UM ARQUIVO .MD CRIADO COM AS POSSIVEIS TASKS, ISSUES...

**Resultado gerado (resumo):**
- Pesquisa sobre boas práticas LangGraph 2026 e sobre o impacto da Reforma Tributária (IBS/CBS) no
  transporte de cargas.
- Proposta de 4 tipos de agente possíveis + roadmap de 3 semanas.
- Arquivo `roadmap-agente-tributario-frete.md` com épicos/tasks/issues iniciais.

**Arquivos afetados:**
- `roadmap-agente-tributario-frete.md` (versão inicial do planejamento, fora da estrutura `.kiro`)

---

## [P02]

**Prompt enviado:**
> (respostas às perguntas de esclarecimento) "NAO ENTENDI, TODAS AS ALTERNATIVAS IRAO CUMPRIR O
> REQUISITO?" / Individual / Só quero usar modelo local/gratuito (Ollama)

**Resultado gerado (resumo):**
- Explicação comparativa das 4 opções de agente.
- Recomendação: unir "classificação tributária" + "RAG regulatório" em um único agente.

---

## [P03]

**Prompt enviado:**
> Sim, essa é a direção

**Resultado gerado (resumo):**
- Confirmação do escopo: Agente de Classificação Tributária de Frete com RAG (LC 214/2025 +
  Notas Técnicas), LangGraph, Ollama local.

---

## [P04]

**Prompt enviado:**
> GOSTARIA QUE CRIASSE O REQUIREMENTS.MD, PRODUCT.MD, STEERING.MD, PARA QUE EU POSSA PASSAR PARA
> O KIRO E DESENVOLVER

**Resultado gerado (resumo):**
- Pesquisa sobre a convenção real de specs/steering do Kiro.
- Geração de `.kiro/steering/product.md`, `.kiro/steering/steering.md` (versão inicial) e
  `.kiro/specs/agente-classificacao-tributaria-frete/requirements.md` (formato EARS).

**Arquivos afetados:**
- `.kiro/steering/product.md`
- `.kiro/steering/steering.md` (posteriormente corrigido, ver P05)
- `.kiro/specs/agente-classificacao-tributaria-frete/requirements.md`

---

## [P05]

**Prompt enviado:**
> ah entao, nao precisa gerar steering.md, já que é uma pasta!

**Resultado gerado (resumo):**
- Correção: `steering.md` removido e substituído por `.kiro/steering/tech.md` e
  `.kiro/steering/structure.md`, seguindo a convenção real de múltiplos arquivos dentro da pasta
  `.kiro/steering/`.

**Arquivos afetados:**
- `.kiro/steering/tech.md` (novo)
- `.kiro/steering/structure.md` (novo)
- `.kiro/steering/steering.md` (removido)

---

## [P06]

**Prompt enviado:**
> pode gerarpara mim, o que puder adiantar melhor
> (seguido de, após pergunta de esclarecimento):
> 1- quero apenas o estudo inicial do projeto para que eu possa passar para o kiro. Inclusive
> seria interessante incluir desde já... pasta docs/prompts e salve todos os prompts...
> 2- quero que crie a regra ja para que os prompts sejam criados de acordo com as issues.
> 3 - Ao inciar uma issue deverá salvar os prompts
> 4 - criar uma branch para cada tarefa issue.
> 5 - criar o quadro kanban, com as colunas: backlog, refinamento, desenvolvimento, bloqueado,
> teste de aceitação, concluido.
> 6 - criar casos de testes para testar se o codigo esta funcionando antes de subir o commit.
> 7 - seguir workflow do github.

**Resultado gerado (resumo):**
- `design.md` e `tasks.md` (este último já quebrado em issues numeradas, com branch, critérios de
  aceite e casos de teste por issue).
- `.kiro/steering/workflow.md` com a regra de branch por issue, log de prompt obrigatório e gate
  de testes.
- `.kiro/hooks/salvar-prompt-ao-iniciar-issue.kiro.hook` (hook do Kiro).
- `.githooks/pre-commit` (git hook real que roda pytest e bloqueia commit em caso de falha).
- `docs/prompts/README.md` e este próprio arquivo (`ISSUE-000`).
- `docs/kanban.md` com as 6 colunas solicitadas.

**Arquivos afetados:**
- `.kiro/specs/agente-classificacao-tributaria-frete/design.md`
- `.kiro/specs/agente-classificacao-tributaria-frete/tasks.md`
- `.kiro/steering/workflow.md`
- `.kiro/hooks/salvar-prompt-ao-iniciar-issue.kiro.hook`
- `.githooks/pre-commit`
- `docs/prompts/README.md`
- `docs/prompts/ISSUE-000-planejamento-inicial.md`
- `docs/kanban.md`

---

## [P07]

**Prompt enviado:**
> VAMOS VALIDAR POSTTERIORMENTE, POR ENQUANTO EU QUERO O BASICO PARA INCIAR. VOCE SALVOU OS
> NOSSOS PROMPTS AQUI DENTRO JA DESTE ZIP? SE NAO SALVOU, PODE SALVAR.
> (contexto: userPreferences informado — dev TOTVS, módulo TMS Gestão de Frete Embarcador,
> conhece HTML/CSS/JS, Java, AdvPL, SQL/MSSQL, React Native, Bulma, Bootstrap, Hibernate,
> Spring Boot, Postman, APIs, Docker; aprendendo Python e Progress 4GL; curso de IA no SENAI)

**Resultado gerado (resumo):**
- Confirmação de que P01–P06 já estavam salvos no zip anterior.
- Este próprio registro (P07) adicionado a `ISSUE-000-planejamento-inicial.md`.
- Validação da tabela `TABELA_CCLASSTRIB` (ISSUE-002) adiada a pedido do usuário — fica pendente
  para quando ele tiver fonte oficial/contador para conferir.

**Arquivos afetados:**
- `docs/prompts/ISSUE-000-planejamento-inicial.md` (este arquivo)
