# Agente de Classificação Tributária de Frete

> Agente de IA local para classificação tributária de operações de frete conforme a Reforma
> Tributária brasileira (IBS/CBS — LC 214/2025).

## Objetivo

Automatizar a classificação tributária de operações de frete (CT-e), sugerindo o código
cClassTrib e a alíquota aplicável com base na legislação vigente (LC 214/2025 e Notas Técnicas),
reduzindo o risco de rejeição de documentos fiscais pela SEFAZ.

## Público-alvo

Analista fiscal/operacional de transportadora ou embarcador que precisa classificar rapidamente
operações de frete no novo sistema tributário. No contexto acadêmico, o próprio desenvolvedor
(módulo TMS — Gestão de Frete Embarcador / TOTVS Protheus).

## Funcionalidades principais

- Receber dados de uma operação de frete (modal, origem/destino, regime tributário, data)
- Consultar base de conhecimento regulatória local via RAG (LC 214/2025 + Notas Técnicas)
- Classificar o cenário tributário (fase de transição 2026–2033, Simples Nacional, TAC, internacional)
- Sugerir código cClassTrib e alíquota via tabela determinística (não gerado por LLM)
- Gerar justificativa em linguagem natural com citação da base legal
- Pausar para validação humana antes de finalizar (human-in-the-loop)
- Exportar resultado em JSON/CSV simulando integração com TMS

## Restrições

- Funciona 100% localmente (sem APIs pagas — usa Ollama)
- Não emite CT-e real nem integra com SEFAZ
- Interface via CLI/notebook (sem GUI)
