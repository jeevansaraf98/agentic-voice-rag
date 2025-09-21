
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from rag_core import retrieve_context, generate_answer

class State(TypedDict):
    question: str
    route: Literal["retrieve","direct"]
    context: str
    answer: str

def router(state: State) -> State:
    q = state["question"].lower()
    need = any(k in q for k in ["doc","policy","langgraph","faiss","vector","kb","knowledge"])
    state["route"] = "retrieve" if need else "direct"
    return state

def retrieve(state: State) -> State:
    if state["route"] != "retrieve":
        state["context"] = ""
        return state
    ctx = "\n\n".join(retrieve_context(state["question"]))
    state["context"] = ctx
    return state

def answer(state: State) -> State:
    ctx_chunks = state["context"].split("\n\n") if state["context"] else []
    state["answer"] = generate_answer(state["question"], ctx_chunks)
    return state

graph = StateGraph(State)
graph.add_node("router", router)
graph.add_node("retrieve", retrieve)
graph.add_node("answer", answer)
graph.set_entry_point("router")
graph.add_edge("router", "retrieve")
graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

app_graph = graph.compile()
