from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel
from pathlib import Path
import tempfile, os, shutil
import time, uuid
from typing import Dict, Any

from agent_graph import app_graph, AgentState
from stt_whisper import transcribe

import logging, os
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(title="Voice RAG Agent (LangGraph)")

class AskIn(BaseModel):
    question: str
    tts: bool = False

def run_agent(question: str, use_tts: bool = False) -> dict:
    request_id = str(uuid.uuid4())[:8]
    t0 = time.time()
    init: AgentState = {"question": question, "use_tts": use_tts, "request_id": request_id}
    logger.info(f"[{request_id}] /ask start | tts={use_tts} | q='{question[:120]}'")

    final_state: AgentState = app_graph.invoke(init)

    elapsed = (time.time() - t0) * 1000
    logger.info(
        f"[{request_id}] /ask done | route={final_state.get('route')} "
        f"| strength={final_state.get('strength')} | refused={final_state.get('refused')} "
        f"| tts_path={final_state.get('tts_path')} | {elapsed:.1f} ms"
    )
    return {
        "request_id": request_id,
        "question": question,
        "route": final_state.get("route"),
        "strength": final_state.get("strength"),
        "refused": final_state.get("refused", False),
        "answer": final_state.get("answer"),
        "tts_path": final_state.get("tts_path"),
    }

@app.get("/ask")
def ask_get(q: str, tts: bool = False):
    return run_agent(q, use_tts=tts)

@app.post("/ask")
def ask_post(payload: AskIn = Body(...)):
    return run_agent(payload.question, use_tts=payload.tts)

@app.post("/voice_ask")
async def voice_ask(file: UploadFile = File(...), tts: bool = True):
    # Save temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or '')[-1] or ".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        audio_path = tmp.name
    try:
        text = transcribe(audio_path)
        result = run_agent(text, use_tts=tts)
        result.update({"transcript": text})
        return result
    finally:
        try: os.remove(audio_path)
        except Exception: pass
