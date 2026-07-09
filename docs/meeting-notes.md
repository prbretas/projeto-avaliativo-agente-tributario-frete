# Ata de reunião — AgenteClassTrib

## Sessão de planejamento inicial — 04/07/2026

**Participantes:** Philippe Bretas (desenvolvedor)  
**Ferramenta:** Claude.ai (sessão de planejamento com IA)

### Funcionalidades discutidas

- Agente RAG + LangGraph para classificar tributariamente operações de frete (CT-e)
- Uso de LLM local via Ollama (sem custo com API)
- Human-in-the-loop via `interrupt()` do LangGraph
- Tabela determinística de cClassTrib (não gerado por LLM)
- Exportar resultado em JSON e disponibilizar via API REST (FastAPI) para integração com qualquer sistema externo

### Regras de negócio definidas

- 2026 é o "ano-teste": alíquota 1% (0,9% CBS + 0,1% IBS), destacada mas compensável
- Simples Nacional: destaque facultativo em 2026, obrigatório a partir de 01/01/2027
- Transporte internacional: imunidade/alíquota zero com manutenção de crédito
- TAC (transportador autônomo pessoa física): não é contribuinte; obrigação recai sobre o contratante
- A partir de 03/08/2026: regime regular obrigado a preencher cClassTrib em todos os CT-e

### Decisões tomadas

- Stack: Python 3.11 + LangGraph + Ollama + Chroma + SQLite + Pydantic + pytest
- Sem APIs pagas (restrição do autor)
- Prazo de entrega: 20/07/2026 15h (avaliação M2.1 — 30% do módulo)
- Artefatos de rastreabilidade: log de prompts por issue em `docs/prompts/`

### Observações

- Validação da tabela TABELA_CCLASSTRIB pendente — confirmar com fonte oficial ou contador antes de finalizar ISSUE-002
- Demo pode ser exigida pelo AVA (verificar enunciado da avaliação)
