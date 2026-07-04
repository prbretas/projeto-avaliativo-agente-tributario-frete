# Convenção de log de prompts

Todo prompt usado para gerar/guiar trabalho de uma issue deve ser salvo aqui, **antes** do
primeiro commit de código daquela issue (ver `.kiro/steering/workflow.md`).

## Nome do arquivo

```
docs/prompts/ISSUE-XXX-slug-curto.md
```

Para trabalho de planejamento anterior à criação das issues (ex.: definição do escopo do
projeto), usar `ISSUE-000-<assunto>.md`.

## Template de cada entrada

```markdown
## [PXX] AAAA-MM-DD

**Prompt enviado:**
> (cole o prompt exatamente como foi enviado)

**Ferramenta/modelo:** Kiro / Claude / etc.

**Resultado gerado (resumo):**
- (1–3 linhas resumindo o que foi produzido/decidido)

**Arquivos afetados:**
- caminho/do/arquivo.py
```

## Regra

- Um arquivo por issue. Se a issue precisar de várias interações, todas vão no mesmo arquivo,
  em ordem cronológica (P01, P02, P03...).
- Nunca editar retroativamente um prompt já registrado — se precisar corrigir o rumo, isso vira
  um novo prompt (Pxx seguinte) no mesmo arquivo.
