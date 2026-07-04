---
inclusion: always
---

# Technology Stack

## Stack tecnológica

- **Linguagem:** Python 3.11+
- **Orquestração de agente:** LangGraph (StateGraph, checkpointer, `interrupt()` para
  human-in-the-loop)
- **LLM:** Ollama local (modelo padrão: `llama3.2:latest` — instalado localmente; alternativa: `llama3:latest`).
  Não usar APIs pagas (OpenAI/Anthropic) neste projeto — restrição deliberada do autor.
- **Embeddings:** `nomic-embed-text` via Ollama
- **Vector store:** Chroma (persistente, local, sem custo)
- **Persistência de estado do grafo:** SQLite (`SqliteSaver` do LangGraph)
- **Validação de schema/output estruturado:** Pydantic
- **Testes:** `pytest` + golden set de cenários em `/data/golden_set` (arquivos JSON)
- **Controle de versão:** Git

## Restrições técnicas

- O agente deve rodar 100% localmente (sem chamadas a serviços de IA pagos), pois o autor não
  possui orçamento para API paga neste projeto.
- O código deve ser compreensível por alguém ainda aprendendo Python (evitar abstrações
  desnecessariamente complexas; preferir clareza a "esperteza").
- Nenhum código deve tratar o cClassTrib/alíquota como texto livre gerado pelo LLM — a decisão
  final do código tributário deve vir de uma tabela/lookup determinístico no código, com o LLM
  atuando apenas na interpretação do cenário e na geração da justificativa.
- Toda resposta do agente deve conter citação da fonte regulatória usada (rastreabilidade).

## Preferências de implementação

- Priorizar `structured_output` (Pydantic) em toda chamada ao LLM que precise ser consumida por
  outro nó do grafo, para reduzir variação de formato típica de modelos locais menores.
- Registrar logs de cada transição de nó (para depuração e para a demonstração final do projeto).
