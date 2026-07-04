# SCTEC — Agente Tributário de Frete

> Projeto avaliativo M2.1 — Curso SCTEC / SENAI  
> Agente de Classificação Tributária de Frete com RAG + LangGraph

---

## Sobre o projeto

Agente de IA local que analisa dados de uma operação de transporte de cargas e sugere a
classificação tributária aplicável (IBS/CBS, cClassTrib, alíquota estimada) conforme a Reforma
Tributária brasileira (EC 132/2023 e LC 214/2025).

**Problema que resolve:** desde 03/08/2026, documentos fiscais de frete (CT-e) sem o correto
preenchimento dos campos IBS/CBS são rejeitados automaticamente pela SEFAZ. Este agente apoia a
decisão de classificação com embasamento regulatório real.

**Avaliação:** M2.1 (30% do módulo) · **Entrega:** 20/07/2026 15h · **Modalidade:** Individual

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Orquestração do agente | LangGraph (StateGraph + `interrupt()`) |
| LLM local | Ollama — `llama3.1:8b` ou `mistral` |
| Embeddings | `nomic-embed-text` via Ollama |
| Vector store | Chroma (local, persistente) |
| Persistência de estado | SQLite (`SqliteSaver`) |
| Validação de schema | Pydantic |
| Testes | pytest + golden set |
| API | FastAPI (endpoint REST para integração externa) |

> Sem APIs pagas. Funciona 100% offline.

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11+
- [Ollama](https://ollama.ai) instalado e rodando
- Git

### Setup

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd SCTEC-agente-tributario-frete/src/projeto-avaliativo-agente-tributario-frete

# 2. Crie e ative o venv
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Baixe os modelos no Ollama
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# 5. Configure o git hook de testes
git config core.hooksPath .githooks

# 6. Execute o agente
python src/main.py
```

### Rodar os testes

```bash
pytest tests/
```

### Executar o golden set de avaliação

```bash
python scripts/run_golden_set.py
```

---

## Estrutura do projeto

```
src/
  /graph          # StateGraph, nós e edges do LangGraph
  /rag            # ingestão, chunking, indexação e retrieval
  /tools          # lookup determinístico de cClassTrib/alíquota
  /schemas        # modelos Pydantic (State, outputs estruturados)
data/
  /docs_regulatorios   # LC 214/2025, Notas Técnicas (fonte do RAG)
  /golden_set          # cenários de teste com resultado esperado
  /chroma_db           # índice vetorial local (gerado na ingestão)
tests/                 # suíte pytest
docs/
  /prompts             # log de prompts por issue (rastreabilidade IA)
  kanban.md            # quadro Kanban do projeto
.kiro/
  /specs               # requirements, design e tasks (spec Kiro)
  /steering            # contexto permanente para o agente IA
  /hooks               # automações do Kiro
.githooks/
  pre-commit           # bloqueia commit se pytest falhar
```

---

## Fluxo do agente

```
parse_operacao → retrieve_context → classify_scenario
    → determine_cclasstrib → generate_justification
    → [human_review] → export_result → API REST
```

O nó `human_review` pausa a execução via `interrupt()` do LangGraph e aguarda aprovação ou
rejeição. Se rejeitado, o fluxo retorna para `classify_scenario`. O resultado aprovado é
disponibilizado via endpoint REST para integração com qualquer sistema externo.

---

## Workflow de desenvolvimento

Ver `.kiro/steering/workflow.md` para as regras completas. Resumo:

- Uma branch por issue: `feature/ISSUE-XXX-slug`
- Salvar prompt em `docs/prompts/` antes do primeiro commit
- PR só mergeia com todos os testes passando
- Kanban em `docs/kanban.md`

---

## Fontes regulatórias

- LC 214/2025 (IBS/CBS)
- Nota Técnica CT-e NT 2025.001
- EC 132/2023 (Reforma Tributária)
- Cronograma de transição 2026–2033 (SEFAZ)

---

## Autor

Philippe Bretas — Curso SCTEC / SENAI · Módulo M2.1
