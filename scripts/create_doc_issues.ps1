$gh   = "C:\Program Files\GitHub CLI\gh.exe"
$repo = "prbretas/agenteclasstrib"

$body016 = @"
## Objetivo
Criar arquivos de prompts separados por issue em docs/prompts/, registrando os prompts enviados ao Kiro e as respostas durante o desenvolvimento de cada issue.

## Tarefas
- [ ] Criar docs/prompts/ISSUE-001-setup-ambiente.md
- [ ] Criar docs/prompts/ISSUE-002-base-regulatoria.md
- [ ] Criar docs/prompts/ISSUE-003-pipeline-rag.md
- [ ] Criar docs/prompts/ISSUE-004-schemas.md
- [ ] Criar docs/prompts/ISSUE-005-no-parse-operacao.md
- [ ] Criar docs/prompts/ISSUE-006-no-retrieve-context.md
- [ ] Criar docs/prompts/ISSUE-007-no-classify-scenario.md
- [ ] Criar docs/prompts/ISSUE-008-no-determine-cclasstrib.md
- [ ] Criar docs/prompts/ISSUE-009-no-generate-justification.md
- [ ] Criar docs/prompts/ISSUE-010-no-human-review.md
- [ ] Criar docs/prompts/ISSUE-011-export-api-checkpointer.md
- [ ] Criar docs/prompts/ISSUE-012-montagem-grafo.md
- [ ] Criar docs/prompts/ISSUE-013-golden-set.md
- [ ] Criar docs/prompts/ISSUE-014-documentacao-final.md

## Criterio avaliado
Criterio 3 - Organizacao dos arquivos, documentacao e prompts (2,0 pts)
Requisito: 'Registrei os principais prompts utilizados em arquivo .md'

## Branch
feature/ISSUE-016-prompts-por-issue
"@

$body017 = @"
## Objetivo
Criar apresentacao de ate 2 slides com a ideia do projeto conforme exigido pelo professor.

## Conteudo obrigatorio dos slides
Slide 1:
- Problema escolhido
- Processo automatizado
- Proposta do agente

Slide 2:
- Entrada esperada (exemplo JSON)
- Saida esperada (exemplo JSON)
- Fluxo geral da solucao (diagrama do grafo)
- Ferramenta utilizada

## Formatos aceitos
- PDF versionado no repositorio em docs/apresentacao/
- PowerPoint / Google Slides exportado como PDF

## Criterio avaliado
Criterio 4 - Ideia do projeto e apresentacao (1,0 pt)

## Branch
feature/ISSUE-017-slides-apresentacao
"@

& $gh issue create --repo $repo --title "ISSUE-016: Arquivo de prompts por issue (docs/prompts/)" --label "docs,priority:high" --body $body016
Write-Host "ISSUE-016 criada"

& $gh issue create --repo $repo --title "ISSUE-017: Slides de apresentacao do projeto (2 slides)" --label "docs,priority:high" --body $body017
Write-Host "ISSUE-017 criada"
