# AgenteClassTrib

> Projeto Avaliativo M2.1 — Curso SCTEC / SENAI · Módulo: IA para DEVs  
> Agente de IA local que classifica tributariamente operações de frete conforme a Reforma Tributária brasileira (IBS/CBS — LC 214/2025).

---

## Problema

A partir de 03/08/2026, documentos fiscais de frete (CT-e) precisam ter os campos de IBS e CBS corretamente preenchidos para não serem rejeitados pela SEFAZ. O campo `cClassTrib` é obrigatório para empresas do regime regular, e opcional (com regras específicas) para o Simples Nacional. Classificar errado gera rejeição automática e retrabalho operacional.

Este agente resolve esse problema: dado os dados de uma operação de frete, classifica o cenário tributário aplicável, sugere o `cClassTrib` e a alíquota correta, justifica com base na legislação real (LC 214/2025), e aguarda aprovação humana antes de exportar o resultado.

---

## Objetivo do agente

Automatizar a classificação tributária de uma operação de frete, entregando:
- o código `cClassTrib` correto
- a alíquota estimada (IBS + CBS)
- uma justificativa em linguagem natural citando a base legal
- validação humana antes de aceitar o resultado (human-in-the-loop)
- exportação em JSON via API REST

---

## Fluxo com LangGraph

```
Entrada (dados da operação)
         ↓
  parse_operacao          → valida e normaliza os campos (modal, regime, data, UFs)
         ↓
  retrieve_context        → busca trechos da LC 214/2025 no índice vetorial (RAG/Chroma)
         ↓
  classify_scenario       → aplica as 5 regras do R3 e determina a fase de transição
         ↓
  determine_cclasstrib    → consulta tabela determinística → retorna cClassTrib e alíquota
         ↓
  generate_justification  → LLM local (llama3.2) gera justificativa citando fontes do RAG
         ↓
  [human_review]          → PAUSA — aguarda aprovação via API (interrupt() do LangGraph)
         ↓ aprovado
  export_result           → salva JSON em data/outputs/ e retorna via API REST
```

O grafo é implementado com `StateGraph` do LangGraph. O nó `human_review` usa `interrupt()` para pausar a execução completamente — ela só retoma quando o usuário chama `POST /classificar/{thread_id}/review`.

---

## Ferramenta integrada ao agente

O agente integra **duas ferramentas** ao fluxo:

1. **RAG (Retrieval-Augmented Generation) com Chroma**  
   O nó `retrieve_context` consulta um índice vetorial local (`data/chroma_db/`) construído a partir de documentos reais da LC 214/2025 e das Notas Técnicas do CT-e. Os trechos recuperados são usados para embasar a justificativa gerada pelo LLM — o agente nunca "inventa" a legislação.

2. **Tabela determinística `TABELA_CCLASSTRIB`** (`src/tools/tabela_cclasstrib.py`)  
   O nó `determine_cclasstrib` consulta um lookup em código Python puro — o `cClassTrib` e a alíquota **nunca são gerados pelo LLM**. São sempre resultado de uma tabela mapeada a partir da legislação. Se a combinação não existe na tabela, o agente sinaliza "revisão manual necessária".

---

## Stack tecnológica

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Orquestração do agente | LangGraph (StateGraph, `interrupt()`, SqliteSaver) |
| LLM local | Ollama — `llama3.2:latest` |
| Embeddings (RAG) | `nomic-embed-text` via Ollama |
| Vector store | Chroma (local, persistente) |
| Persistência de estado | SQLite (`langgraph-checkpoint-sqlite`) |
| Validação de schemas | Pydantic v2 |
| API REST | FastAPI + Uvicorn |
| Testes | pytest (55 testes) + golden set (15 cenários) |

> Funciona 100% offline — sem APIs pagas, sem chamadas externas.

---

## Como executar o projeto

### Pré-requisitos

- Python 3.11 ou superior
- [Ollama](https://ollama.com) instalado
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/prbretas/agenteclasstrib.git
cd agenteclasstrib/src/agenteclasstrib
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Baixar os modelos no Ollama

```bash
# Terminal separado — mantém o Ollama rodando
ollama serve

# Em outro terminal:
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 5. Indexar os documentos regulatórios (RAG)

```bash
python scripts/run_ingestao.py
```

> Isso processa os arquivos em `data/docs_regulatorios/` e cria o índice vetorial em `data/chroma_db/`. Necessário apenas uma vez por máquina.

### 6. Subir a API

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8080
```

Acesse a documentação interativa em: **http://127.0.0.1:8080/docs**

---

## Exemplo de entrada

```json
{
  "modal": "rodoviario",
  "origem_uf": "SP",
  "destino_uf": "RJ",
  "regime_tributario": "lucro_real",
  "data_emissao": "2026-09-15",
  "contratado_pessoa_fisica": false
}
```

**Endpoint:** `POST http://127.0.0.1:8080/classificar`

---

## Exemplo de saída

```json
{
  "thread_id": "4ce43e4c-5875-40aa-bd2b-9a67ac3664ae",
  "status": "pendente_revisao",
  "cclasstrib": "01",
  "aliquota_total": 0.01,
  "fase_transicao": "2026_teste",
  "justificativa": "A operação de frete rodoviário entre SP e RJ, realizada por empresa do Lucro Real em setembro de 2026, enquadra-se na fase-teste da Reforma Tributária. Conforme Art. 337 da LC 214/2025, a alíquota somada de IBS e CBS é de 1% (0,9% CBS + 0,1% IBS) durante todo o ano de 2026.",
  "fontes_citadas": ["lc_214_2025_frete - Art. 337"]
}
```

Após receber o `thread_id`, o usuário pode **aprovar** ou **rejeitar** via:

```
POST http://127.0.0.1:8080/classificar/{thread_id}/review
Body: {"aprovado": true, "comentario": "Classificação correta"}
```

Se aprovado, o resultado é exportado em `data/outputs/resultado_YYYYMMDD_HHMMSS.json`.

---

## Principais decisões tomadas

1. **cClassTrib via tabela determinística, não LLM** — O LLM é usado apenas para gerar a justificativa em linguagem natural. O código tributário vem de um lookup em Python para garantir determinismo e rastreabilidade.

2. **RAG com documentos reais** — Em vez de depender do conhecimento do LLM sobre a legislação, os trechos relevantes da LC 214/2025 são recuperados do índice vetorial e injetados no prompt. Isso garante que a justificativa cita fontes reais.

3. **Human-in-the-loop via `interrupt()`** — O grafo para completamente no nó `human_review` e só retoma quando o usuário envia a aprovação pela API. Isso é implementado com o mecanismo nativo do LangGraph, com estado persistido no SQLite.

4. **API REST genérica** — O resultado é disponibilizado via FastAPI para integração com qualquer sistema externo, sem dependência de plataformas ou ERPs específicos.

5. **Ollama 100% local** — Nenhuma chamada a APIs pagas (OpenAI, Anthropic, etc.). O projeto funciona offline com `llama3.2` e `nomic-embed-text`.

---

## Limitações da solução (V1.0)

- **Tabela de cClassTrib incompleta** — A tabela cobre os cenários mais comuns (2026-teste, Simples Nacional, TAC, internacional), mas combinações menos frequentes retornam "revisão manual necessária". Cobertura total depende de validação com contador especializado.

- **LLM local menor** — O `llama3.2` (~2 GB) é adequado para a demonstração, mas pode gerar justificativas menos precisas que modelos maiores. Cada requisição ao LLM demora 3-5 minutos na primeira execução.

- **Não emite CT-e real** — O agente sugere a classificação, mas não integra com SEFAZ nem emite documentos fiscais reais. *(Planejado para V2.0)*

- **Interface apenas via API/CLI** — Não há interface gráfica. A interação é via endpoints REST ou linha de comando. *(Planejado para V2.0)*

- **Base RAG limitada** — A base regulatória cobre trechos selecionados da LC 214/2025 e Notas Técnicas. Alterações futuras na legislação precisarão de reingestão manual. *(Planejado para V2.0)*

---

## Versão 2.0 — Roadmap

As evoluções abaixo estão planejadas para após a avaliação do projeto. Detalhes completos em [`ROADMAP.md`](./ROADMAP.md).

| Feature | Descrição |
|---|---|
| 🧾 **Emissão CT-e (homologação)** | Integração com API de terceiros (NFe.io / Focus NFe) para enviar o resultado aprovado diretamente à SEFAZ em ambiente de homologação |
| 🖥️ **Interface gráfica web** | Frontend em React + Vite com formulário de entrada, painel de aprovação/rejeição e histórico de classificações |
| 🔄 **RAG incremental e atualizado** | Ingestão incremental por hash + scraping agendado de fontes oficiais (ENCAT, DOU, SEFAZ) para manter a base regulatória sempre atualizada |

> Todas as features V2.0 serão desenvolvidas na branch `v2`, mantendo a `main` estável com a versão avaliada.

---

## Rodando os testes

```bash
# Suite completa (55 testes)
python -m pytest tests/ -v

# Golden set (15 cenários tributários, meta >= 80%)
python scripts/run_golden_set.py
```

---

## Estrutura do repositório

```
src/
  graph/          # nós do LangGraph (parse, retrieve, classify, determine, generate, review, export)
  rag/            # pipeline de ingestão e retrieval (Chroma)
  tools/          # TABELA_CCLASSTRIB determinística
  schemas/        # modelos Pydantic (AgentState, Operacao, ...)
  api.py          # API FastAPI com 3 endpoints REST
  main.py         # ponto de entrada CLI

data/
  docs_regulatorios/   # LC 214/2025 e Notas Técnicas CT-e (fonte do RAG)
  golden_set/          # 15 cenários de teste com resultado esperado
  chroma_db/           # índice vetorial (gerado localmente, não versionado)
  outputs/             # JSONs exportados após aprovação humana

tests/            # 55 testes automatizados (pytest)
scripts/          # run_ingestao.py, run_golden_set.py
docs/prompts/     # histórico de prompts por issue (ISSUE-000 a ISSUE-014)

.kiro/specs/      # requirements.md, design.md, tasks.md
.kiro/steering/   # contexto do agente de desenvolvimento (Kiro)
```

---

## Fontes regulatórias

- LC 214/2025 — Lei Complementar que instituiu o IBS e a CBS
- EC 132/2023 — Emenda Constitucional da Reforma Tributária
- NT 2025.001 do CT-e — Nota Técnica com os novos campos do documento fiscal
- Cronograma de transição 2026–2033 (SEFAZ)

---

## Autor

Philippe Bretas — Curso SCTEC / SENAI · Avaliação M2.1 · 2026
