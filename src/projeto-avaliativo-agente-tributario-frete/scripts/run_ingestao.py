"""
Script para executar a ingestão RAG dos documentos regulatórios.
Executa: python scripts/run_ingestao.py
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path para importar src.*
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.ingestao import executar_ingestao

if __name__ == "__main__":
    executar_ingestao()
    print("Ingestão concluída. Índice disponível em data/chroma_db/")
