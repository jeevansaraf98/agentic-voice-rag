from pathlib import Path
from typing import List
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_RAW = Path("data/raw")
INDEX_DIR = Path("data/index")

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def load_documents() -> List:
    docs = []
    for p in DATA_RAW.rglob("*"):
        if p.suffix.lower() in {".txt", ".md"}:
            docs += TextLoader(str(p), autodetect_encoding=True).load()
        elif p.suffix.lower() == ".pdf":
            docs += PyPDFLoader(str(p)).load()
    # enrich metadata
    for i, d in enumerate(docs):
        md = dict(d.metadata or {})
        # Preserve existing source if loader set it; otherwise leave empty
        source_path = md.get("source", "")
        source_name = Path(source_path).name if source_path else ""
        md.update({"source": source_name, "chunk": i})
        d.metadata = md
    return docs

def main():
    print("[ingest] Loading raw documents...")
    docs = load_documents()
    print(f"[ingest] Loaded {len(docs)} pages.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"[ingest] Split to {len(chunks)} chunks.")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vs = FAISS.from_documents(chunks, embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(INDEX_DIR))
    print(f"[ingest] Saved FAISS index to {INDEX_DIR}")

if __name__ == "__main__":
    main()
