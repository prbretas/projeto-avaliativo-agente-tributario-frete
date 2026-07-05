---
inclusion: always
---

# Workflow: Git, Issues, Prompts e Testes

Esta é a regra operacional do projeto. O Kiro (e qualquer pessoa) deve seguir isto ao trabalhar
em qualquer issue de `tasks.md`.

---

## 1. Ciclo obrigatório por issue — BRANCH → COMMIT → PUSH → PR → MERGE

**Este fluxo é OBRIGATÓRIO para cada issue. Nenhuma etapa pode ser pulada.**

```
git checkout main
git pull origin main
git checkout -b feature/ISSUE-XXX-slug-curto   ← branch nova a partir do main atualizado
# ... implementação + testes ...
git add <arquivos>
git commit -m "feat(ISSUE-XXX): descrição"
git push -u origin feature/ISSUE-XXX-slug-curto
gh pr create --base main --head feature/ISSUE-XXX-slug-curto ...
gh pr merge <numero> --squash --delete-branch
git checkout main
git pull origin main                             ← sincroniza o main local antes da próxima issue
```

### Regras críticas

- `main` deve estar sempre em estado funcional (testado, sem erros).
- Cada issue tem **exatamente uma branch**. Nunca commitar diretamente na `main`.
- A branch deve ser criada a partir do `main` já atualizado (`git pull` antes do `checkout -b`).
- Nunca começar uma nova issue sem antes mergear e deletar a branch da issue anterior.
- Após o merge, sempre fazer `git checkout main && git pull origin main` antes de criar a branch da próxima issue.
- Squash merge (`--squash`): mantém o histórico da main limpo.
- **Não deletar branches após o merge** — o desenvolvedor remove quando quiser.

---

## 2. Nomenclatura de branches

```
feature/ISSUE-XXX-slug-curto
```

Exemplos:
- `feature/ISSUE-005-no-parse-operacao`
- `feature/ISSUE-008-no-determine-cclasstrib`
- `feature/ISSUE-012-montagem-grafo`

---

## 3. Conventional Commits

Referenciando sempre o número da issue:

```
feat(ISSUE-XXX): implementa funcionalidade
test(ISSUE-XXX): adiciona testes
fix(ISSUE-XXX): corrige comportamento
chore(ISSUE-XXX): ajusta configuração
docs(ISSUE-XXX): atualiza documentação
```

---

## 4. Gate de testes antes do commit

- Nenhuma issue é "pronta para revisão" sem os casos de teste correspondentes em `/tests`.
- Rodar `pytest tests/ -v` com `.venv\Scripts\python.exe -m pytest` antes de qualquer commit.
- O `.githooks/pre-commit` bloqueia commits com testes falhando. Ativar uma vez por clone:
  ```
  git config core.hooksPath .githooks
  ```

---

## 5. Log de prompts obrigatório por issue

- Antes do primeiro commit de uma issue, salvar o prompt usado em:
  `docs/prompts/ISSUE-XXX-slug-curto.md`
- Seguir o template em `docs/prompts/README.md`.
- Commitar junto com o primeiro commit de código da branch.

---

## 6. Kanban

- Colunas: **Backlog → Refinamento → Desenvolvimento → Bloqueado → Teste de Aceitação → Concluído**
- Toda issue nasce em Backlog.
- Mover para Desenvolvimento só depois de: branch criada + prompt salvo.
- Mover para Bloqueado quando houver dependência não resolvida.
- Mover para Teste de Aceitação quando PR aberto e testes passando.
- Mover para Concluído somente após merge em `main`.

---

## 7. Ordem de dependência entre issues

```
ISSUE-001
  ↓
ISSUE-002 ──┐
            ├→ ISSUE-003
ISSUE-004 ──┘
  ↓
ISSUE-005, ISSUE-006, ISSUE-007, ISSUE-008, ISSUE-009, ISSUE-010, ISSUE-011
(podem rodar em paralelo — cada nó é isolado)
  ↓
ISSUE-012 (precisa de todas as anteriores)
  ↓
ISSUE-013
  ↓
ISSUE-014
```
