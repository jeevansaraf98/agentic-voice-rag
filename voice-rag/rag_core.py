from pathlib import Path
from typing import List
from dotenv import load_dotenv
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

INDEX_DIR = Path("data/index")

load_dotenv()
MODEL = os.getenv("MODEL", "llama3")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Load once at import
_embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
_vectorstore = FAISS.load_local(str(INDEX_DIR), _embeddings, allow_dangerous_deserialization=True)
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 4})
_llm = ChatOllama(model=MODEL, temperature=0.2)

def retrieve_context(query: str) -> List[str]:
    docs = _retriever.invoke(query)
    return [d.page_content for d in docs]

def generate_answer(question: str, context_chunks: List[str]) -> str:
    sys = "You are a concise, factual assistant. Use the provided context when possible."
    ctx = "\n\n".join(context_chunks) if context_chunks else ""
    prompt = f"""{sys}

Question: {question}

Context:
{ctx}

Answer:"""
    return _llm.invoke(prompt).content
