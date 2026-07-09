# Estudo de Integração — AgenteClassTrib + mcp-transportation

> **Autor:** Philippe Bretas  
> **Data:** Julho 2026  
> **Objetivo:** Avaliar como conectar o agente de classificação tributária (AgenteClassTrib) com o servidor MCP de frete tributário (mcp-transportation), formando um sistema integrado e coeso.

---

## 1. Visão Geral dos Dois Projetos

### AgenteClassTrib (`SCTEC-agente-tributario-frete`)

| Aspecto | Detalhe |
|---|---|
| Linguagem | Python 3.12 |
| Orquestração | LangGraph (StateGraph + interrupt) |
| LLM | Ollama llama3.2 (local) |
| Interface | FastAPI REST (3 endpoints) |
| Foco | **Classificar** uma operação de frete → retornar `cClassTrib` + alíquota + justificativa |
| Dado central | Qual código fiscal usar no CT-e? |
| Human-in-the-loop | Sim — pausa para aprovação antes de exportar |

### mcp-transportation (`mcp-frete-tributario`)

| Aspecto | Detalhe |
|---|---|
| Linguagem | TypeScript / Node.js ≥ 20 |
| Protocolo | MCP (Model Context Protocol) via stdio |
| Interface | 4 ferramentas MCP expostas para qualquer cliente (Claude, Cursor, Kiro) |
| Foco | **Calcular e simular** carga tributária (valores monetários, alíquotas por ano) |
| Dado central | Quanto de imposto pago? Como evolui de 2026 a 2033? |
| Human-in-the-loop | Não — ferramentas síncronas, sem estado |

### Conclusão rápida

Os dois projetos são **complementares, não concorrentes**:

```
mcp-transportation          →   responde "quanto?"
AgenteClassTrib             →   responde "qual código usar no CT-e?"
Integração dos dois         →   responde ambas as perguntas com uma única chamada
```

---

## 2. Análise de Compatibilidade

### 2.1 Domínio de negócio

Ambos trabalham com o mesmo contexto: Reforma Tributária brasileira, LC 214/2025, frete, IBS/CBS, período 2026–2033. Os campos de entrada são quase idênticos:

| Campo | AgenteClassTrib | mcp-transportation |
|---|---|---|
| UF de origem | `origem_uf` | `ufOrigem` |
| UF de destino | `destino_uf` | `ufDestino` |
| Ano/data | `data_emissao` | `ano` |
| Valor do frete | não usa | `valorFrete` |
| CNPJ | não usa | `cnpjOrigem` / `cnpjDestino` |
| Regime tributário | `regime_tributario` | não usa |
| Modal | `modal` | não usa |

O AgenteClassTrib sabe **classificar** mas não calcula **valor monetário**.  
O mcp-transportation sabe **calcular valores** mas não classifica `cClassTrib`.  
Juntos, cobrem o ciclo completo de um CT-e.

### 2.2 Stack tecnológica

| Ponto | Situação |
|---|---|
| Linguagens diferentes | Python ↔ TypeScript — comunicação via API ou stdio |
| Protocolos diferentes | REST (AgenteClassTrib) ↔ MCP/stdio (mcp-transportation) |
| Estado | AgenteClassTrib tem estado persistido (SQLite + LangGraph) — mcp-transportation é stateless |
| LLM | AgenteClassTrib usa LLM para justificativa — mcp-transportation é puramente determinístico |

A diferença de linguagem não é um obstáculo — o MCP usa JSON-RPC sobre stdio, e o AgenteClassTrib expõe uma API REST padrão. Ambos os protocolos são interoperáveis.

---

## 3. Formas de Integração — Três Abordagens

### Opção A — AgenteClassTrib como ferramenta MCP (recomendada para V2)

**Ideia:** Criar um wrapper MCP em Python que expõe o AgenteClassTrib como uma ferramenta MCP. Com isso, qualquer cliente MCP (Claude Desktop, Kiro, Cursor) pode chamar ambos os servidores simultaneamente.

```
Cliente MCP (Kiro / Claude Desktop)
         │
         ├── stdio → mcp-transportation (Node.js)
         │            └── calcular_carga_tributaria_frete
         │            └── simular_impacto_rota
         │
         └── stdio → mcp-agenteclasstrib (Python - novo wrapper)
                      └── classificar_operacao_frete
                      └── consultar_classificacao
                      └── aprovar_classificacao
```

**Como implementar:**  
Criar um novo servidor MCP em Python usando o `mcp` SDK oficial que encapsula as chamadas HTTP ao AgenteClassTrib:

```python
# mcp-agenteclasstrib/src/index.py (exemplo simplificado)
from mcp.server import Server
from mcp.server.stdio import stdio_server
import httpx

server = Server("agenteclasstrib")

@server.call_tool()
async def classificar_operacao(arguments: dict):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://127.0.0.1:8080/classificar",
            json=arguments
        )
    return resp.json()

@server.call_tool()  
async def aprovar_classificacao(arguments: dict):
    thread_id = arguments["thread_id"]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://127.0.0.1:8080/classificar/{thread_id}/review",
            json={"aprovado": arguments["aprovado"]}
        )
    return resp.json()
```

**Vantagens:**
- O AgenteClassTrib não precisa mudar nada
- Qualquer cliente MCP ganha acesso às duas capacidades
- O Kiro já suporta múltiplos servidores MCP simultaneamente
- Human-in-the-loop preservado — o LLM do cliente chama `classificar`, depois `aprovar`

**Desvantagens:**
- Requer que o `uvicorn` (AgenteClassTrib) esteja rodando antes de usar o wrapper MCP
- Dois processos para gerenciar

---

### Opção B — mcp-transportation como ferramenta do AgenteClassTrib

**Ideia:** Adicionar o mcp-transportation como uma **ferramenta interna** do grafo LangGraph. O nó `determine_cclasstrib` pode chamar `calcular_carga_tributaria_frete` para enriquecer a resposta com o valor monetário além do código fiscal.

```
AgenteClassTrib (LangGraph)
         │
         ├── retrieve_context (RAG)
         ├── classify_scenario
         ├── determine_cclasstrib
         │    └── [NOVO] chama mcp-transportation via subprocess/stdio
         │         └── calcular_carga_tributaria_frete(uf_origem, uf_destino, ano, valor)
         │         └── retorna valorIBS, valorCBS, totalNovoRegime
         ├── generate_justification (LLM cita valores calculados)
         ├── human_review
         └── export_result (JSON agora inclui valores monetários)
```

**Como implementar:**  
Usar o `mcp` Python SDK para criar um cliente que se conecta ao servidor Node.js:

```python
# src/tools/mcp_transportation_client.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def calcular_carga(uf_origem: str, uf_destino: str, ano: int, valor_frete: float):
    server_params = StdioServerParameters(
        command="node",
        args=["/caminho/para/mcp-transportation/dist/index.js"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "calcular_carga_tributaria_frete",
                {"valorFrete": valor_frete, "ufOrigem": uf_origem,
                 "ufDestino": uf_destino, "ano": ano}
            )
    return result
```

**Vantagens:**
- O output do AgenteClassTrib fica mais rico (código fiscal + valor calculado)
- O LLM pode citar os valores reais na justificativa
- Um único fluxo — o usuário chama um endpoint só

**Desvantagens:**
- Dependência de runtime: Node.js precisa estar instalado onde o Python roda
- Aumenta a complexidade do grafo
- A chamada assíncrona ao servidor MCP adiciona latência

---

### Opção C — Frontend unificado (V2.0 — mais simples de implementar agora)

**Ideia:** O frontend React (planejado para V2.0) pode chamar **ambas as APIs diretamente** e compor a tela com informações dos dois sistemas — sem integração backend entre eles.

```
Frontend React (V2.0)
         │
         ├── POST http://127.0.0.1:8080/classificar
         │    └── AgenteClassTrib: retorna cClassTrib, justificativa
         │
         └── [inline] calcula ou chama mcp-transportation
              └── calcular_carga_tributaria_frete(uf, uf, ano, valor)
              └── Exibe valorIBS, valorCBS, comparativo antigo vs novo regime
```

Para o frontend chamar o mcp-transportation diretamente (que usa stdio), seria necessário um pequeno adapter HTTP — por exemplo, um endpoint Express simples que envolve o servidor MCP:

```typescript
// adapter/server.ts
import express from 'express';
// inicializa o cliente MCP internamente e expõe como REST
app.post('/calcular', async (req, res) => {
  const result = await mcpClient.callTool('calcular_carga_tributaria_frete', req.body);
  res.json(result);
});
```

**Vantagens:**
- Mais simples — não altera nenhum backend
- Ótimo para demonstração da V2.0
- Os dois servidores permanecem independentes e reutilizáveis

**Desvantagens:**
- O frontend precisa orquestrar duas chamadas
- Não há um único artefato exportado com tudo consolidado

---

## 4. Comparativo das Abordagens

| Critério | Opção A (Wrapper MCP) | Opção B (Tool no LangGraph) | Opção C (Frontend) |
|---|---|---|---|
| Complexidade de implementação | Média | Alta | Baixa |
| Altera o AgenteClassTrib? | Não | Sim | Não |
| Altera o mcp-transportation? | Não | Não | Não |
| Funciona sem frontend? | Sim | Sim | Não |
| Human-in-the-loop preservado? | Sim | Sim | Sim |
| Requer Node.js + Python rodando? | Sim | Sim | Sim |
| Resultado unificado em um JSON? | Sim | Sim | Não |
| Ideal para demonstração rápida | Não | Não | Sim |
| Ideal para produção | Sim | Sim | Não |

---

## 5. Recomendação

### ✅ Decisão: Opção C — Frontend unificado (React + Vite)

**Motivo da escolha:** Nenhum backend é alterado. O AgenteClassTrib e o mcp-transportation permanecem exatamente como estão, testados e funcionais. A integração acontece exclusivamente na camada de apresentação — que será desenvolvida do zero de qualquer forma na Feature 2.

**Implementar em ordem:**

1. **Adapter HTTP para o mcp-transportation** — o servidor MCP usa stdio (não HTTP), então o React não pode chamá-lo diretamente. Um pequeno servidor Express (~30 linhas) dentro do próprio `mcp-transportation` expõe as 4 ferramentas como endpoints REST. Isso ainda é Opção C — não altera nenhuma lógica existente.

2. **CORS no AgenteClassTrib** — adicionar `CORSMiddleware` ao `api.py` (2 linhas) para liberar o frontend em `localhost:5173`.

3. **Frontend React + Vite** — o React chama os dois sistemas e compõe a tela com dados consolidados: código fiscal (AgenteClassTrib) + valores monetários (mcp-transportation).

**Resultado final para o usuário:**

```
Tela de resultado (React)
├── cClassTrib: 01                          ← AgenteClassTrib
├── Fase: 2026_teste
├── Justificativa: "Conforme Art. 337..."   ← AgenteClassTrib (LLM)
├── Fontes: lc_214_2025_frete               ← AgenteClassTrib (RAG)
├── ─────────────────────────────────────
├── Valor IBS: R$ 5,00                      ← mcp-transportation
├── Valor CBS: R$ 5,00                      ← mcp-transportation
├── Total novo regime: R$ 10,00             ← mcp-transportation
└── [✅ Aprovar]  [❌ Rejeitar]             ← AgenteClassTrib (human-in-the-loop)
```

### Fluxo ideal na V2.0 com tudo integrado:

```
Usuário (via Frontend ou Claude Desktop)
    │
    ├── "Classifica o frete SP→RJ, lucro real, setembro 2026"
    │    └── AgenteClassTrib: cClassTrib=01, alíquota=1%, justificativa com base na lei
    │
    ├── "Qual o valor do imposto para R$ 5.000 nessa rota?"
    │    └── mcp-transportation: valorIBS=R$ 5, valorCBS=R$ 5, total=R$ 10
    │
    └── "Aprova" → resultado exportado com código fiscal + valores monetários
```

---

## 6. Próximos Passos Sugeridos (Issues para V2.0)

Criar as seguintes issues na branch `v2` para implementar a Opção C:

| Issue | Título | Repositório | Depende de |
|---|---|---|---|
| Nova | [V2][INTEG] Adapter HTTP Express para expor mcp-transportation via REST | mcp-transportation | — |
| Nova | [V2][INTEG] Habilitar CORS no AgenteClassTrib (api.py) | AgenteClassTrib | — |
| Nova | [V2][INTEG] Frontend React exibe dados combinados dos dois sistemas | AgenteClassTrib | Issues #47–50 + adapter |

---

## 7. Referências

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [mcp-transportation (seu projeto)](https://github.com/prbretas/mcp-transportation)
- [AgenteClassTrib (este projeto)](https://github.com/prbretas/projeto-avaliativo-AgenteClassTrib)
- [LangGraph — documentação](https://langchain-ai.github.io/langgraph/)
- [FastMCP — Python MCP framework](https://github.com/jlowin/fastmcp)

---

*Content was rephrased for compliance with licensing restrictions.*
