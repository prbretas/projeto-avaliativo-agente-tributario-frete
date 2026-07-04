"""Testes do pipeline de ingestão RAG."""
import pytest
from pathlib import Path


def test_indexacao_gera_chunks():
    """Verifica que o chunking gera pelo menos 5 chunks dos documentos regulatórios."""
    from src.rag.ingestao import carregar_documentos, fazer_chunking, DOCS_DIR

    docs = carregar_documentos(DOCS_DIR)
    assert len(docs) >= 1, "Deve carregar ao menos 1 documento"
    chunks = fazer_chunking(docs)
    assert len(chunks) >= 5, f"Deve gerar ao menos 5 chunks, gerou {len(chunks)}"


def test_retrieval_traz_trecho_relevante():
    """
    Verifica que o retrieval traz trechos relevantes para uma pergunta conhecida.
    Usa o vectorstore já indexado em data/chroma_db.
    Pula se o Chroma ainda não foi indexado.
    """
    chroma_dir = Path(__file__).parent.parent / "data" / "chroma_db"
    # Considera não indexado se o diretório não existe ou contém apenas .gitkeep
    arquivos = [f for f in chroma_dir.iterdir() if f.name != ".gitkeep"] if chroma_dir.exists() else []
    if not arquivos:
        pytest.skip("Chroma ainda não indexado — rode scripts/run_ingestao.py primeiro")

    from src.rag.ingestao import carregar_vectorstore

    vs = carregar_vectorstore()
    resultados = vs.similarity_search_with_relevance_scores(
        "aliquota IBS CBS frete 2026", k=3
    )
    assert len(resultados) > 0, "Deve retornar ao menos 1 resultado"
    # Verifica que o documento mais relevante tem score razoável
    melhor_score = resultados[0][1]
    assert melhor_score > 0.0, f"Score esperado > 0, obteve {melhor_score}"
