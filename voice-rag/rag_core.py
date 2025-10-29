from pathlib import Path
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import os

import logging, os, time

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

import logging, os
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# -------------------- Config --------------------
INDEX_DIR = Path("data/index")
load_dotenv()
MODEL = os.getenv("MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

SYSTEM_PROMPT = """You are a precise, concise assistant.
Use the provided context to answer the question.
If the context is missing or insufficient, explicitly say you don’t have enough information."""

# Thresholds are for similarity in [0,1]. If your FAISS returns distances, we map d -> 1/(1+d).
TOP1_THRESH = float(os.getenv("TOP1_THRESH", "0.35"))
MEAN3_THRESH = float(os.getenv("MEAN3_THRESH", "0.32"))

# -------------------- Globals (loaded once) --------------------
_embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
_vectorstore = FAISS.load_local(str(INDEX_DIR), _embeddings, allow_dangerous_deserialization=True)
_llm = ChatOllama(model=MODEL, temperature=0.2)

@dataclass
class RetrievedChunk:
    text: str
    score: float              # as returned by FAISS (often a distance). We will map to similarity as needed.
    metadata: Dict[str, Any]

def _faiss_to_similarity(score: float) -> float:
    """Map a FAISS score (often an L2 distance) to a similarity in (0,1].
    If you use cosine/IP index with normalized vectors returning higher=better, you can:
      - set FAISS_RETURNS_DISTANCE=0 in env, and return score directly (clamped to [0,1]).
    """
    returns_distance = os.getenv("FAISS_RETURNS_DISTANCE", "1") == "1"
    if returns_distance:
        # distance d in [0, +inf) -> sim in (0,1]
        return 1.0 / (1.0 + max(0.0, float(score)))
    # If FAISS returns similarity already (e.g., cosine/IP normalized), clamp to [0, 1]
    return max(0.0, min(1.0, float(score)))

def retrieve_context(question: str, k: int = 5) -> List[RetrievedChunk]:
    docs_scores = _vectorstore.similarity_search_with_score(question, k=k)
    print("DOC score", docs_scores)
    out: List[RetrievedChunk] = []
    for doc, score in docs_scores:
        out.append(RetrievedChunk(
            text=doc.page_content,
            score=float(score),
            metadata=getattr(doc, "metadata", {}) or {},
        ))
    # quick debug listing
    dbg = [(c.metadata.get("source",""), round(c.score,4)) for c in out[:5]]
    logger.debug(f"retrieve_context | top_raw={dbg}")
    return out

def context_strength(chunks: List[RetrievedChunk]) -> Dict[str, float]:
    if not chunks:
        return {"top1": 0.0, "mean3": 0.0}
    sims = [_faiss_to_similarity(c.score) for c in chunks]
    sims_sorted = sorted(sims, reverse=True)
    top1 = sims_sorted[0]
    mean3 = sum(sims_sorted[:3]) / min(3, len(sims_sorted))
    logger.debug(f"context_strength | sims_top3={[round(s,4) for s in sims_sorted[:3]]} | "
                 f"TOP1_THRESH={TOP1_THRESH} | MEAN3_THRESH={MEAN3_THRESH}")
    return {"top1": float(top1), "mean3": float(mean3)}

def is_context_strong(stats: Dict[str, float]) -> bool:
    return (stats.get("top1", 0.0) >= TOP1_THRESH) and (stats.get("mean3", 0.0) >= MEAN3_THRESH)

def generate_answer(question: str, ctx_chunks: List[RetrievedChunk]) -> str:
    context_block = "\n\n".join([f"- {c.text}" for c in ctx_chunks]) if ctx_chunks else ""
    prompt = f"""{SYSTEM_PROMPT}

Question: {question}

Context:
{context_block}

Answer:"""
    # log a safe preview of the prompt
    logger.debug("generate_answer | prompt_preview:\n" + prompt[:800] + ("..." if len(prompt)>800 else ""))
    t0 = time.time()
    resp = _llm.invoke(prompt)
    elapsed = (time.time()-t0)*1000
    logger.info(f"generate_answer | llm_time_ms={elapsed:.1f}")
    return getattr(resp, "content", str(resp))
