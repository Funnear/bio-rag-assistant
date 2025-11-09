# built-in libs
from pathlib import Path
import tempfile

# extra libs
from pikepdf import Pdf, PdfError
from pypdf.errors import PdfReadError

# langchain libs
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# project libs
from env_handler import load_paths
from state_machine import *


# --------- common helpers ---------

def _build_splitter() -> RecursiveCharacterTextSplitter:
    """Shared text splitter config."""
    return RecursiveCharacterTextSplitter(
        chunk_size=1200,     # ~350 tokens
        chunk_overlap=200,   # ~50–60 tokens
    )

def _clean_pdf_to_temp(original_path: Path, tmp_dir: Path) -> Path:
    """
    Create a cleaned temporary copy of the given PDF using pikepdf.
    The original file (with highlights) is left untouched.
    Returns the path to the cleaned temp file.
    """
    clean_path = tmp_dir / original_path.name
    try:
        with Pdf.open(original_path) as pdf:
            pdf.save(clean_path)
    except PdfError as e:
        # If cleaning fails, re-raise so caller can decide what to do
        raise PdfError(f"Failed to clean PDF '{original_path}': {e}") from e
    return clean_path


def _load_pdfs(pdf_paths: list[Path]):
    """Load all PDFs into a flat list of Documents, skipping unreadable files.
    Each original PDF is first cleaned into a temporary copy.
    """
    docs = []

    # temp directory is automatically deleted when context exits
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        for path in pdf_paths:
            try:
                # 1) make cleaned temp copy
                clean_path = _clean_pdf_to_temp(path, tmpdir)

                # 2) load from cleaned copy
                loader = PyPDFLoader(str(clean_path))
                docs.extend(loader.load())

            except (PdfError, PdfReadError) as e:
                print(f"[WARN] Skipping problematic PDF '{path.name}': {e}")
            except Exception as e:
                print(f"[WARN] Unexpected error for '{path.name}': {e}")

    return docs


def _build_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")


def _build_retriever_from_chroma(chroma_dir: Path):
    emb = _build_embeddings()
    vectordb = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=emb,
    )
    return vectordb.as_retriever(search_kwargs={"k": 10})


# --------- for state EMPTY ---------
def init_ingest() -> Chroma:
    """
    Initial ingest:
    - Read ALL PDFs from datasets_dir
    - Build a fresh Chroma DB (overwrite existing)
    - Write metadata hashes
    - Return retriever
    """
    
    datasets_dir, chroma_dir, metadata_path = load_paths()

    # find all PDFs
    pdf_paths = sorted(datasets_dir.glob("*.pdf"))
    if not pdf_paths:
        raise RuntimeError(f"No PDF files found in {datasets_dir}")

    # load + split
    docs = _load_pdfs(pdf_paths)
    splitter = _build_splitter()
    chunks = splitter.split_documents(docs)

    # embeddings + Chroma (fresh index)
    emb = _build_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        persist_directory=str(chroma_dir),
    )

    # metadata: filename -> hash
    files_map = {p.name: compute_file_hash(p) for p in pdf_paths}
    save_metadata(metadata_path, files_map)

    # retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})
    return retriever


# --------- for state UP_TO_DATE or OUTDATED ---------
def restore_from_cache() -> Chroma:
    """
    Open existing Chroma DB from disk and return a retriever.
    Assumes embeddings/model are the same as during ingest.
    """
    _, chroma_dir, _ = load_paths()
    retriever = _build_retriever_from_chroma(chroma_dir)
    return retriever

# --------- for state OUTDATED, only on demand ---------
def ingest_new_data() -> Chroma:
    """
    Incremental ingest:
    - Detect new/changed PDFs via state_machine.detect_kb_state
    - Add their chunks to existing Chroma DB
    - Update metadata hashes
    - Return an up-to-date retriever
    """
    datasets_dir, chroma_dir, metadata_path = load_paths()

    kb_state, kb_info = detect_kb_state(datasets_dir, metadata_path)

    to_process_names = kb_info.get("new_files", []) + kb_info.get("changed_files", [])
    if not to_process_names:
        # Nothing to do; just restore current retriever
        return _build_retriever_from_chroma(chroma_dir)

    pdf_paths = [datasets_dir / name for name in to_process_names]

    # 1) load + split only new/changed docs
    docs = _load_pdfs(pdf_paths)
    splitter = _build_splitter()
    chunks = splitter.split_documents(docs)

    # 2) open existing Chroma and append
    emb = _build_embeddings()
    vectordb = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=emb,
    )
    vectordb.add_documents(chunks)

    # 3) update metadata
    meta_map = load_metadata(metadata_path)
    for p in pdf_paths:
        meta_map[p.name] = compute_file_hash(p)
    save_metadata(metadata_path, meta_map)

    # 4) updated retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})
    return retriever

