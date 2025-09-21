from pathlib import Path
from dotenv import load_dotenv
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader

DATA_DIR = Path("data/raw")
INDEX_DIR = Path("data/index")

def load_docs():
    docs = []
    for p in DATA_DIR.rglob("*"):
        if p.suffix.lower() in {".txt", ".md"}:
            docs.extend(TextLoader(str(p), encoding="utf-8").load())
        elif p.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(p)).load())
    return docs

def main():
    load_dotenv()
    embed_model = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    print("Loading docs...")
    raw_docs = load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_documents(raw_docs)
    print(f"Chunks: {len(chunks)}")

    print("Embedding...")
    embeddings = HuggingFaceEmbeddings(model_name=embed_model)

    print("Building FAISS...")
    vs = FAISS.from_documents(chunks, embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(INDEX_DIR))
    print(f"Saved index to {INDEX_DIR}")

if __name__ == "__main__":
    main()
