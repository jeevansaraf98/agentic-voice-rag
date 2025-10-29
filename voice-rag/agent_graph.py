# agent_graph.py
from typing import TypedDict, Literal, List, Optional, Dict, Any, Final
import time, logging, os
from langgraph.graph import StateGraph, END

from rag_core import (
    retrieve_context,
    generate_answer,
    context_strength,
    is_context_strong,
    RetrievedChunk,
)

# --- logging setup ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --- refusal text defined ABOVE judge to avoid linter warning ---
REFUSAL_TEXT: Final[str] = (
    "I don't have enough reliable context to answer confidently. "
    "Could you rephrase or provide more details?"
)

class AgentState(TypedDict, total=False):
    question: str
    route: Literal["retrieve", "direct"]
    chunks: List[RetrievedChunk]
    strength: Dict[str, float]
    answer: str           # <-- state key 'answer' is fine; just don't use it as a NODE name
    refused: bool
    use_tts: bool
    tts_path: Optional[str]
    request_id: str

def router(state: AgentState) -> AgentState:
    print("Router STATE: ", state)
    rid = state.get("request_id", "????")
    q = (state.get("question") or "").lower()
    need_rag = any(k in q for k in ["doc","docs","kb","policy","manual","faiss","vector","langgraph","knowledge","pdf"])
    state["route"] = "retrieve" if need_rag else "direct"
    logger.info(f"[{rid}] node=router | need_rag={need_rag}")
    return state

def retrieve(state: AgentState) -> AgentState:
    rid = state.get("request_id", "????")
    t0 = time.time()
    chunks = retrieve_context(state["question"], k=5)
    strength = context_strength(chunks)
    state["chunks"] = chunks
    state["strength"] = strength
    top = [(c.metadata.get("source",""), round(c.score,4)) for c in chunks[:3]]
    logger.info(f"[{rid}] node=retrieve | top={top} | strength={strength} | {(time.time()-t0)*1000:.1f} ms")
    return state

def answer_node(state: AgentState) -> AgentState:
    """Renamed from 'answer' to avoid collision with state key 'answer'."""
    print("ANSWER node STATE: ", state)
    rid = state.get("request_id", "????")
    t0 = time.time()
    chunks = state.get("chunks", []) if state.get("route") == "retrieve" else []
    logger.debug(f"[{rid}] node=answer_node | ctx_len={len(chunks)} | q='{state.get('question','')[:120]}'")
    out = generate_answer(state["question"], chunks)
    state["answer"] = out
    logger.info(f"[{rid}] node=answer_node | {(time.time()-t0)*1000:.1f} ms")
    return state

def judge(state: AgentState) -> AgentState:
    print("Judge node STATE: ", state)
    rid = state.get("request_id", "????")
    strong = True
    if state.get("route") == "retrieve":
        strong = is_context_strong(state.get("strength", {"top1": 0.0, "mean3": 0.0}))
    state["refused"] = not strong
    logger.info(f"[{rid}] node=judge | strong={strong} | refused={state['refused']} | strength={state.get('strength')}")
    if state["refused"]:
        state["answer"] = REFUSAL_TEXT
    return state

# voice_out is optional; no-op if TTS not configured
try:
    from tts_piper import synthesize_wav
except Exception:
    def synthesize_wav(text: str, *args, **kwargs) -> Optional[str]:
        return None

def voice_out(state: AgentState) -> AgentState:
    rid = state.get("request_id", "????")
    if state.get("use_tts"):
        path = synthesize_wav(state.get("answer", ""))
        state["tts_path"] = path
        logger.info(f"[{rid}] node=voice_out | path={path}")
    else:
        logger.info(f"[{rid}] node=voice_out | skipped")
    return state

# ------- Build graph (node names must NOT match state keys) -------
graph = StateGraph(AgentState)

graph.add_node("router", router)
graph.add_node("retrieve", retrieve)
graph.add_node("answer_node", answer_node)   # <-- renamed node
graph.add_node("judge", judge)
graph.add_node("voice_out", voice_out)

graph.set_entry_point("router")

def _route(state: AgentState) -> str:
    return "retrieve" if state.get("route") == "retrieve" else "answer_node"

graph.add_conditional_edges("router", _route, {"retrieve": "retrieve", "answer_node": "answer_node"})
graph.add_edge("retrieve", "answer_node")
graph.add_edge("answer_node", "judge")
graph.add_edge("judge", "voice_out")
graph.add_edge("voice_out", END)

app_graph = graph.compile()
