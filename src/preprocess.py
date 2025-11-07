import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def setup_environment():
    """
    Sets up the environment by loading variables from a .env file located at the project root.
    """
    # Get project root by walking up until you find .env
    root_dir = Path(__file__).resolve().parents[1]   # 1 = go up from /src to project root
    dotenv_path = root_dir / ".env"

    # Load environment variables from .env file
    # LangChain gets OPENAI_API_KEY from here
    load_dotenv(dotenv_path=dotenv_path)


def retrieve_data():
    """
    Load from PDF, split into chunks, create embeddings and set up a retriever.
    """
    
    # Load + split
    pdf_path = Path("datasets") / "When microRNAs activate translation 2008.pdf"
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,  # ~350 tokens
        chunk_overlap=200,  # ~50–60 tokens
    )
    chunks = splitter.split_documents(docs)

    # Embeddings + Chroma
    emb = OpenAIEmbeddings(model="text-embedding-3-small")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        persist_directory="./.chroma_db"
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})

    return retriever

