# Requirements: Agente de Classificação Tributária de Frete (RAG + LangGraph)

## Contexto

Este documento define os requisitos funcionais e não funcionais do agente descrito em
`.kiro/steering/product.md`. As entregas devem ser executáveis localmente, dentro do prazo da
avaliação M2.1 (entrega: 20/07/2026, 15h).

---

## Requisito 1 — Entrada de dados da operação de frete

**User Story:** Como usuário do agente, eu quero informar os dados básicos de uma operação de
frete, para que o agente tenha contexto suficiente para classificar a operação tributariamente.

### Acceptance Criteria (EARS)

1. QUANDO o usuário fornecer modal (rodoviário, aéreo, aquaviário), origem, destino, regime
   tributário do contratante (Simples Nacional, Lucro Presumido, Lucro Real) e data de emissão,
   ENTÃO o sistema DEVE aceitar esses dados e prosseguir para a etapa de recuperação de contexto.
2. SE algum campo obrigatório estiver ausente, ENTÃO o sistema DEVE solicitar o dado faltante
   antes de prosseguir, em vez de assumir um valor padrão silenciosamente.
3. QUANDO a data de emissão informada for anterior a 01/01/2026, ENTÃO o sistema DEVE avisar que
   está fora do escopo de cobertura da base regulatória (que trata da transição 2026–2033).

---

## Requisito 2 — Recuperação de contexto regulatório (RAG)

**User Story:** Como usuário, eu quero que o agente busque automaticamente os trechos relevantes
da legislação, para que a classificação não dependa do conhecimento "de memória" do LLM.

### Acceptance Criteria (EARS)

1. QUANDO os dados da operação forem processados, ENTÃO o sistema DEVE consultar a base vetorial
   local (Chroma) e retornar os trechos mais relevantes da LC 214/2025 e das Notas Técnicas
   indexadas.
2. SE nenhum trecho relevante for encontrado com score mínimo aceitável, ENTÃO o sistema DEVE
   sinalizar "contexto insuficiente" em vez de gerar uma classificação sem embasamento.
3. QUANDO o contexto for recuperado, ENTÃO o sistema DEVE registrar quais documentos/trechos
   foram usados, para permitir citação na justificativa final.

---

## Requisito 3 — Classificação do cenário tributário

**User Story:** Como usuário, eu quero que o agente identifique em qual fase da transição
tributária (2026 teste, 2027+ regra plena, regime especial) a operação se enquadra, para aplicar
a regra correta.

### Acceptance Criteria (EARS)

1. QUANDO a data de emissão estiver entre 01/01/2026 e 31/12/2026, ENTÃO o sistema DEVE classificar
   a operação como "fase-teste" (alíquota somada de 1%: 0,9% CBS + 0,1% IBS).
2. QUANDO o regime tributário do contratante for Simples Nacional E a data for em 2026, ENTÃO o
   sistema DEVE indicar que o destaque de IBS/CBS é facultativo.
3. QUANDO o regime tributário do contratante for Simples Nacional E a data for a partir de
   01/01/2027, ENTÃO o sistema DEVE indicar que o destaque de IBS/CBS passa a ser obrigatório.
4. QUANDO o modal for "transporte internacional de cargas", ENTÃO o sistema DEVE indicar o regime
   de imunidade/alíquota zero com manutenção de crédito sobre insumos.
5. QUANDO o contratado for um transportador autônomo pessoa física (TAC), ENTÃO o sistema DEVE
   indicar que o TAC não é contribuinte e que a obrigação recai sobre o contratante.

---

## Requisito 4 — Sugestão de código cClassTrib e alíquota

**User Story:** Como usuário, eu quero que o agente sugira o código de classificação tributária
aplicável, para reduzir o risco de rejeição do CT-e por preenchimento incorreto.

### Acceptance Criteria (EARS)

1. QUANDO o cenário tributário for classificado, ENTÃO o sistema DEVE consultar uma tabela
   determinística (não gerada por LLM) para obter o cClassTrib correspondente.
2. SE o cenário não corresponder a nenhuma entrada conhecida da tabela, ENTÃO o sistema DEVE
   retornar "classificação não determinada" e sinalizar a necessidade de revisão manual, em vez de
   inferir um código.
3. QUANDO o código for determinado, ENTÃO o sistema DEVE apresentar também a alíquota nominal
   estimada aplicável ao cenário.

---

## Requisito 5 — Justificativa citável

**User Story:** Como usuário, eu quero receber uma explicação em linguagem natural com a base
legal usada, para poder validar e defender a classificação perante auditoria ou contador.

### Acceptance Criteria (EARS)

1. QUANDO a classificação e o cClassTrib forem determinados, ENTÃO o sistema DEVE gerar uma
   justificativa em português citando os trechos regulatórios recuperados na etapa de RAG.
2. O sistema NUNCA DEVE apresentar uma justificativa sem pelo menos uma citação de fonte
   rastreável (documento + trecho).
3. QUANDO a geração da justificativa falhar ou retornar formato inválido, ENTÃO o sistema DEVE
   tentar novamente uma vez antes de sinalizar erro ao usuário.

---

## Requisito 6 — Validação humana (human-in-the-loop)

**User Story:** Como usuário responsável pela decisão final, eu quero revisar e aprovar a
classificação antes que ela seja considerada definitiva, para manter controle sobre decisões
fiscais.

### Acceptance Criteria (EARS)

1. QUANDO a justificativa for gerada, ENTÃO o sistema DEVE pausar a execução do grafo (via
   `interrupt()`) e aguardar aprovação, rejeição ou edição do usuário.
2. SE o usuário rejeitar a classificação, ENTÃO o sistema DEVE permitir reclassificação manual ou
   nova tentativa antes de exportar o resultado.
3. QUANDO o usuário aprovar, ENTÃO o sistema DEVE marcar o resultado como validado e prosseguir
   para exportação.

---

## Requisito 7 — Exportação do resultado

**User Story:** Como usuário, eu quero exportar o resultado da classificação, para simular a
integração com um sistema de gestão de frete/TMS.

### Acceptance Criteria (EARS)

1. QUANDO o resultado for aprovado, ENTÃO o sistema DEVE exportá-lo em formato JSON (e
   opcionalmente CSV) contendo: dados da operação, cenário classificado, cClassTrib, alíquota,
   justificativa e fontes citadas.
2. O sistema DEVE persistir o estado da execução (checkpointer SQLite) para permitir auditoria
   posterior da decisão tomada.

---

## Requisito 8 — Qualidade e avaliação

**User Story:** Como autor do projeto, eu quero validar o agente contra casos conhecidos, para
garantir confiabilidade mínima antes da entrega.

### Acceptance Criteria (EARS)

1. O projeto DEVE incluir um golden set com no mínimo 15 cenários representativos e resultado
   esperado.
2. QUANDO o golden set for executado, ENTÃO o sistema DEVE atingir taxa de acerto ≥ 80% na
   classificação de cenário e cClassTrib.
3. O sistema DEVE rodar integralmente com modelo local via Ollama, sem nenhuma chamada a API paga.

---

## Fora de escopo (explicitamente não incluído nesta versão)

- Emissão real de CT-e ou integração com SEFAZ.
- Cálculo de créditos tributários complexos (diesel, pedágio, manutenção) — fica como evolução
  futura.
- Suporte a idiomas além do português.
- Interface gráfica além de CLI/notebook simples.
