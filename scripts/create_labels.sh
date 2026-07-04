#!/usr/bin/env bash
# Cria labels padrao para o projeto
REPO="prbretas/projeto-avaliativo-agente-tributario-frete"

gh label create "story"           --repo "$REPO" --color "0052cc" --description "User Story" --force
gh label create "chore"           --repo "$REPO" --color "e4e669" --description "Configuracao e setup" --force
gh label create "test"            --repo "$REPO" --color "0e8a16" --description "Testes automatizados" --force
gh label create "docs"            --repo "$REPO" --color "c5def5" --description "Documentacao" --force
gh label create "priority:high"   --repo "$REPO" --color "e11d48" --description "Alta prioridade - bloqueante" --force
gh label create "priority:medium" --repo "$REPO" --color "f97316" --description "Media prioridade" --force
gh label create "priority:low"    --repo "$REPO" --color "84cc16" --description "Baixa prioridade" --force
gh label create "ai"              --repo "$REPO" --color "8b5cf6" --description "IA LangGraph LLM" --force
gh label create "rag"             --repo "$REPO" --color "7c3aed" --description "Retrieval-Augmented Generation" --force
gh label create "api"             --repo "$REPO" --color "06b6d4" --description "API REST FastAPI" --force
gh label create "data-model"      --repo "$REPO" --color "10b981" --description "Modelos de dados Pydantic" --force
gh label create "setup"           --repo "$REPO" --color "f59e0b" --description "Ambiente e infraestrutura" --force

echo "Todas as labels criadas!"
