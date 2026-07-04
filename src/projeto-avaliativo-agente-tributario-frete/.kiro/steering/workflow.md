---
inclusion: always
---

# Workflow: Git, Issues, Prompts e Testes

Esta é a regra operacional do projeto. O Kiro (e qualquer pessoa) deve seguir isto ao trabalhar
em qualquer issue de `tasks.md`.

## 1. Uma branch por issue (GitHub Flow)

- `main` deve estar sempre em estado funcional (deployável/executável).
- Para cada issue de `tasks.md`, criar uma branch a partir de `main` atualizada:
  `feature/ISSUE-XXX-slug-curto` (ex.: `feature/ISSUE-005-no-parse-operacao`).
- Commits seguem Conventional Commits, referenciando a issue:
  `feat(ISSUE-005): implementa validação de operacao`
  `test(ISSUE-005): adiciona testes de campo faltante`
- Ao concluir, abrir Pull Request de `feature/ISSUE-XXX-*` para `main`.
- PR só pode ser mesclado se todos os testes da issue estiverem passando.
- Preferir squash merge; apagar a branch após o merge.

## 2. Log de prompts obrigatório por issue

- **Antes do primeiro commit de uma issue** (ou seja, no momento em que a issue entra na coluna
  "Desenvolvimento" do Kanban), o(s) prompt(s) usados para gerar/guiar aquele trabalho DEVEM ser
  salvos em `docs/prompts/ISSUE-XXX-slug-curto.md`, seguindo o template de
  `docs/prompts/README.md`.
- Isso vale tanto para prompts enviados ao Kiro quanto a qualquer outro assistente de IA usado no
  desenvolvimento da issue.
- O arquivo de prompt da issue deve ser commitado junto com o primeiro commit de código daquela
  branch (mesmo commit ou commit imediatamente anterior).

## 3. Gate de testes antes do commit

- Nenhuma issue é considerada "pronta para revisão" sem casos de teste correspondentes em
  `/tests`, conforme listado em cada issue de `tasks.md`.
- O repositório usa um git hook local (`.githooks/pre-commit`) que roda `pytest` automaticamente
  e **bloqueia o commit** se algum teste falhar. Ativar uma vez por clone com:
  ```
  git config core.hooksPath .githooks
  ```
- Dentro do Kiro, ao concluir uma task de spec, pedir explicitamente para "rodar os testes da
  issue antes de finalizar" — não confiar apenas no hook local durante a sessão de
  desenvolvimento assistido.

## 4. Kanban

- Quadro definido em `docs/kanban.md` com as colunas: **Backlog → Refinamento → Desenvolvimento →
  Bloqueado → Teste de Aceitação → Concluído**.
- Toda issue nasce em Backlog.
- Mover para Desenvolvimento só depois de: (a) branch criada, (b) prompt inicial salvo em
  `docs/prompts/`.
- Mover para Bloqueado sempre que houver dependência não resolvida (ex.: ISSUE-007 depende de
  ISSUE-003 e ISSUE-004 estarem concluídas).
- Mover para Teste de Aceitação quando o PR estiver aberto e os testes automatizados passando.
- Mover para Concluído somente após o merge em `main`.

## 5. Ordem de dependência entre issues

`ISSUE-001` → `ISSUE-002`/`ISSUE-004` (paralelas) → `ISSUE-003` → `ISSUE-005`..`ISSUE-011`
(podem ser paralelas entre si, pois cada nó é isolado) → `ISSUE-012` (precisa de todas as
anteriores) → `ISSUE-013` → `ISSUE-014`.
