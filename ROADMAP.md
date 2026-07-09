# Roadmap — Agente Tributário de Frete

> Este documento registra as evoluções planejadas para a **Versão 2.0** do sistema.  
> A V1.0 está completa, funcional e aprovada conforme os requisitos do projeto avaliativo.  
> As melhorias abaixo serão implementadas **após a avaliação** do professor.

---

## Versão atual — V1.0 ✅

- [x] Classificação tributária via tabela determinística (`cClassTrib`)
- [x] RAG local com LC 214/2025 e Notas Técnicas CT-e
- [x] LLM local via Ollama (llama3.2) — 100% offline
- [x] Human-in-the-loop com `interrupt()` do LangGraph
- [x] API REST com FastAPI (3 endpoints)
- [x] Exportação de resultado aprovado em JSON
- [x] 55 testes automatizados + golden set com 15 cenários (meta ≥ 80%)

---

## Versão 2.0 — Roadmap 🚀

### Feature 1 — Integração com API de Emissão CT-e (Homologação)

> **Escolha:** Opção C — API de emissão de CT-e de terceiros (NFe.io, Focus NFe ou Plugnotas)

**Motivação:**  
Hoje o agente sugere a classificação mas não emite nada. Com essa integração, o fluxo fica completo: o resultado aprovado pelo usuário é automaticamente enviado para emissão em ambiente de homologação da SEFAZ.

**O que será feito:**
- Adicionar nó `emit_cte` no grafo LangGraph, executado após `export_result`
- Integrar com a API REST da NFe.io (ou Focus NFe) em modo homologação
- O JSON aprovado é transformado no payload esperado pela API de emissão
- Retorno com número do protocolo e status da SEFAZ é salvo junto ao resultado
- Nó é **opcional** — pode ser desabilitado via variável de ambiente

**Dependências:**
- Conta gratuita/trial em NFe.io ou Focus NFe
- Certificado digital A1 (ambiente de homologação)
- Nova variável de ambiente: `CTE_API_KEY`, `CTE_API_URL`, `CTE_EMIT_ENABLED`

**Referências:**
- [NFe.io — API CT-e](https://nfe.io/docs/cte)
- [Focus NFe — Emissão CT-e](https://focusnfe.com.br/documentacao)
- [Plugnotas — CT-e REST](https://plugnotas.com.br)

---

### Feature 2 — Interface Gráfica Web (React + Vite) + Integração mcp-transportation

> **Escolha:** Opção A — React + Vite em pasta `frontend/`  
> **Integração:** Opção C — Frontend unificado (sem alteração de backend)

**Motivação:**  
A interação atual é exclusivamente via Swagger UI ou cURL. Uma interface dedicada torna o sistema mais acessível para usuários não técnicos (contadores, operadores fiscais) e demonstra melhor o fluxo human-in-the-loop.

Além disso, o projeto [mcp-transportation](https://github.com/prbretas/mcp-transportation) — servidor MCP com cálculo de carga tributária de frete — será integrado via frontend, sem alterar nenhum backend. O React chama os dois sistemas e compõe uma tela unificada com código fiscal (AgenteClassTrib) + valores monetários (mcp-transportation).

**O que será feito:**
- Criar pasta `frontend/` com projeto React + Vite + TypeScript
- Habilitar CORS na FastAPI para `localhost:5173` (2 linhas em `api.py`)
- Adicionar endpoint `GET /resultados` na API para listar histórico de outputs
- Criar adapter HTTP Express no `mcp-transportation` (~30 linhas) para expor as ferramentas MCP via REST, já que o frontend não consegue chamar stdio diretamente

**Telas planejadas:**

| Tela | Descrição |
|---|---|
| **Formulário** | Campos do `POST /classificar` com validação e dropdowns para `modal`, `regime_tributario` e `origem_uf/destino_uf` |
| **Resultado** | Exibe `cClassTrib`, alíquota, justificativa e fontes citadas (AgenteClassTrib) + valorIBS, valorCBS, comparativo antigo vs novo regime (mcp-transportation) — com botões "✅ Aprovar" e "❌ Rejeitar" |
| **Comentário de rejeição** | Modal para inserir comentário antes de rejeitar |
| **Histórico** | Lista paginada dos JSONs em `data/outputs/` com filtro por data e status |

**Stack frontend:**
- React 18 + Vite + TypeScript
- TailwindCSS (estilização)
- React Query (chamadas à API)
- React Hook Form + Zod (validação do formulário)

**Por que Opção C (e não integração backend)?**  
Os dois backends (Python/FastAPI e Node.js/MCP) permanecem intocados — testados e funcionais. A integração acontece exclusivamente no frontend, que será desenvolvido do zero de qualquer forma. Zero risco de regressão.

---

### Feature 3 — RAG com Ingestão Incremental e Atualização Automática

> **Escolha:** Opção C — Ingestão incremental por hash + scraping agendado de fontes oficiais

**Motivação:**  
A legislação tributária muda. Hoje qualquer atualização requer reingestão manual completa. A V2.0 deve detectar alterações automaticamente e reindexar apenas o que mudou.

**O que será feito:**

#### Parte 3A — Ingestão Incremental
- Criar `data/docs_regulatorios/manifest.json` com hash SHA-256 e data de cada documento
- Modificar `scripts/run_ingestao.py` para comparar hashes antes de reindexar
- Documentos não alterados são ignorados — ingestão apenas do diff

#### Parte 3B — Scraping Agendado de Fontes Oficiais
- Script `scripts/run_update_sources.py` que verifica periodicamente:
  - Portal ENCAT / SVRS (Notas Técnicas CT-e): `https://www.svrs.rs.gov.br/CT-e`
  - Diário Oficial da União — filtro por `IBS`, `CBS`, `LC 214`, `CT-e`
  - Portal SEFAZ Nacional: `https://www.gov.br/fazenda/pt-br/composicao/sefaz`
- Novos documentos são baixados para `data/docs_regulatorios/` e a ingestão incremental é disparada automaticamente

#### Parte 3C — Agendamento
- **Windows:** Agendador de Tarefas (Task Scheduler) — script `.bat` rodando semanalmente
- **Linux/Mac:** cron job — `0 6 * * 1 python scripts/run_update_sources.py`
- Log de execução em `data/logs/rag_update.log`

**Nova estrutura de dados:**
```
data/
  docs_regulatorios/
    manifest.json          ← novo: controle de versão dos documentos
    lc_214_2025_frete.txt
    notas_tecnicas_cte_2026.txt
    [novos documentos baixados automaticamente]
  logs/
    rag_update.log         ← novo: histórico de atualizações
```

---

## Resumo das Features V2.0

| # | Feature | Complexidade | Impacto |
|---|---|---|---|
| 1 | Integração CT-e homologação (API terceiro) | Média | Alto — fluxo completo |
| 2 | Interface gráfica React + Vite + integração mcp-transportation (Opção C) | Baixa-Média | Alto — usabilidade + dados combinados |
| 3 | RAG incremental + scraping agendado | Média | Alto — manutenibilidade |

**Ordem de implementação sugerida:** 2 → 3 → 1  
(Interface primeiro: independente, impacto imediato, e já integra o mcp-transportation sem tocar nos backends)

> **Decisão de integração registrada:** A conexão com o [mcp-transportation](https://github.com/prbretas/mcp-transportation) será feita via **Opção C — Frontend unificado**. Nenhum backend é alterado. Ver análise completa em `docs/ESTUDO-INTEGRACAO-MCP.md`.

---

## Notas

- Todas as features da V2.0 serão desenvolvidas na branch `v2`
- A branch `main` permanece estável com a V1.0 aprovada
- Cada feature terá sua própria branch `feature/v2-*` criada a partir de `v2`
- Este roadmap será refinado conforme feedback da avaliação do professor
