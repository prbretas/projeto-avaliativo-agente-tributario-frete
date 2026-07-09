"""Teste direto do LLM para verificar formato de resposta."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="llama3.2:latest", temperature=0.1)

prompt = '''Você é um especialista tributário. Responda APENAS com JSON no formato exato abaixo, sem texto antes ou depois:
{"justificativa": "explicacao aqui", "fontes_citadas": ["LC 214/2025 - Art. 337"]}

Contexto: frete rodoviario SP para RJ, regime Lucro Real, data 2026-09-15, fase-teste 2026, aliquota 1% (0.9% CBS + 0.1% IBS), cClassTrib 01.
Trecho regulatorio: "Art. 337 - Em 2026 a aliquota somada de IBS e CBS sera de 1% para fins de teste."'''

print("Enviando prompt ao LLM...")
r = llm.invoke([HumanMessage(content=prompt)])
print("=== RESPOSTA DO LLM ===")
print(repr(r.content[:600]))
print()
print("=== CONTEUDO BRUTO ===")
print(r.content[:600])
