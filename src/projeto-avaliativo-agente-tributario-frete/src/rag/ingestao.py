"""
Pipeline de ingestão RAG para documentos regulatórios.
Realiza chunking, geração de embeddings e indexação no Chroma.
"""
import warnings
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from langchain_community.vectorstores import Chroma

# Caminhos relativos à raiz do projeto
_BASE = Path(__file__).parent.parent.parent
DOCS_DIR = _BASE / "data" / "docs_regulatorios"
CHROMA_DIR = _BASE / "data" / "chroma_db"

EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
COLLECTION_NAME = "base_regulatoria_frete"
SCORE_MINIMO = 0.3  # threshold para contexto insuficiente (R2.2)


def carregar_documentos(docs_dir: Path = DOCS_DIR) -> list:
    """Carrega todos os .txt do diretório de documentos regulatórios."""
    docs = []
    for arquivo in docs_dir.glob("*.txt"):
        loader = TextLoader(str(arquivo), encoding="utf-8")
        docs_carregados = loader.load()
        for doc in docs_carregados:
            doc.metadata["documento"] = arquivo.stem
        docs.extend(docs_carregados)
    return docs


def fazer_chunking(
    documentos: list,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list:
    """Divide documentos em chunks com overlap para contexto contínuo."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documentos)


def indexar_chroma(chunks: list, persist_dir: Path = CHROMA_DIR) -> "Chroma":
    """Gera embeddings e indexa os chunks no Chroma persistente."""
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(persist_dir),
            collection_name=COLLECTION_NAME,
        )
    return vectorstore


def carregar_vectorstore(persist_dir: Path = CHROMA_DIR) -> "Chroma":
    """Carrega vectorstore Chroma já indexado."""
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )


def recuperar_contexto(
    query: str,
    k: int = 4,
    persist_dir: Path = CHROMA_DIR,
) -> list[dict]:
    """
    Recupera os k chunks mais relevantes para a query.
    Retorna lista de dicts com 'documento', 'trecho' e 'score'.
    Retorna lista vazia se score máximo estiver abaixo de SCORE_MINIMO (contexto insuficiente).
    """
    vs = carregar_vectorstore(persist_dir)
    resultados = vs.similarity_search_with_relevance_scores(query, k=k)
    if not resultados or resultados[0][1] < SCORE_MINIMO:
        return []  # sinaliza contexto_insuficiente ao nó retrieve_context
    return [
        {
            "documento": doc.metadata.get("documento", "desconhecido"),
            "trecho": doc.page_content,
            "score": score,
        }
        for doc, score in resultados
    ]


def executar_ingestao() -> "Chroma":
    """Pipeline completo: carregar → chunkar → indexar."""
    print("Iniciando ingestão RAG...")
    docs = carregar_documentos()
    print(f"  {len(docs)} documentos carregados.")
    chunks = fazer_chunking(docs)
    print(f"  {len(chunks)} chunks gerados.")
    vs = indexar_chroma(chunks)
    print(f"  Indexação concluída em {CHROMA_DIR}")
    return vs


if __name__ == "__main__":
    executar_ingestao()
