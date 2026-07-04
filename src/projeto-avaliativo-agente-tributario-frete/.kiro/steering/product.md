---
inclusion: always
---

# Product Overview: Agente de Classificação Tributária de Frete (RAG + LangGraph)

## Propósito

O produto é um agente de IA local que analisa os dados de uma operação de transporte de cargas
(frete) e sugere a classificação tributária aplicável (IBS/CBS, cClassTrib, alíquota estimada)
conforme a Reforma Tributária brasileira (EC 132/2023 e LC 214/2025), justificando a resposta com
base em documentação regulatória real (Lei Complementar, Notas Técnicas do CT-e e cronograma
oficial de transição 2026–2033).

O problema real que resolve: desde 03/08/2026, documentos fiscais eletrônicos de frete (CT-e)
emitidos sem o correto preenchimento dos campos de IBS/CBS são **rejeitados automaticamente** pela
SEFAZ. Empresas do regime regular precisam classificar corretamente cada operação; empresas do
Simples Nacional têm regras diferentes até 2027; transporte internacional e TAC (transportador
autônomo pessoa física) têm tratamento próprio. Esse é hoje um ponto de atrito operacional real em
sistemas de gestão de frete e emissão de CT-e.

Este é um projeto acadêmico (mini-projeto individual, avaliação M2.1) e também um estudo aplicado
de LangGraph voltado à automação de classificação tributária em operações de transporte de cargas.

## Público-alvo

- Uso principal: o próprio desenvolvedor, como ferramenta de apoio e estudo.
- Persona de referência: analista fiscal/operacional de uma transportadora ou embarcador que
  precisa decidir rapidamente como classificar uma operação de frete no novo sistema tributário.

## Funcionalidades-chave

1. Receber os dados de uma operação de frete (modal, origem/destino, regime tributário do
   contratante, data de emissão).
2. Consultar uma base de conhecimento local (RAG) com a LC 214/2025 e Notas Técnicas relevantes.
3. Classificar o cenário tributário aplicável (fase da transição: 2026 teste / 2027+ / regime
   especial).
4. Sugerir o código cClassTrib e a alíquota estimada aplicável, usando uma tabela determinística
   de apoio (não é o LLM que "inventa" o código).
5. Gerar uma justificativa em linguagem natural citando a base legal recuperada.
6. Pausar para validação humana antes de considerar o resultado final (human-in-the-loop).
7. Exportar o resultado (JSON/CSV) e disponibilizar via API REST para integração com qualquer
   sistema externo.

## Objetivos de negócio / acadêmicos

- Entregar um agente funcional com LangGraph que automatize um processo real (requisito da
  avaliação M2.1, 30% do módulo).
- Demonstrar domínio de RAG ("documentação viva") aplicado a um problema tributário real e atual.
- Gerar um artefato de portfólio reutilizável e integrável via API em qualquer contexto de
  gestão de frete ou emissão de documentos fiscais eletrônicos.

## Métricas de sucesso

- Taxa de acerto de classificação ≥ 80% em um golden set de 15–20 cenários representativos.
- 100% das respostas do agente citam pelo menos um trecho da base regulatória (nenhuma resposta
  "sem fonte").
- Fluxo completo executável localmente, sem dependência de API paga, dentro do prazo de entrega
  (20/07/2026).
