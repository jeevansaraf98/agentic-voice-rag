from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import tempfile
#from agent_graph import app_graph
from rag_core import retrieve_context, generate_answer
from stt_whisper import transcribe
# from tts_piper import tts_to_wav   # enable later for audio replies

app = FastAPI(title="Voice RAG Agent")

class AskIn(BaseModel):
    question: str

@app.get("/ask")
def ask_get(q: str = Query(..., description="Your question")):
    ctx = retrieve_context(q)
    ans = generate_answer(q, ctx)
    return {"answer": ans, "ctx_used": len(ctx)}

#Agent-RAG
#@app.get("/ask")
#def ask_get(q: str):
 #   result = app_graph.invoke({"question": q})
 #   return {"answer": result["answer"], "ctx_used": len(result.get("context", []))}

@app.post("/ask")
def ask_post(body: AskIn):
    ctx = retrieve_context(body.question)
    ans = generate_answer(body.question, ctx)
    return {"answer": ans, "ctx_used": len(ctx)}

#Agent-RAG
#@app.post("/ask")
#def ask_post(body: AskIn):
 #   result = app_graph.invoke({"question": body.question})
  #  return {"answer": result["answer"], "ctx_used": len(result.get("context", []))}


@app.post("/voice_ask")
async def voice_ask(file: UploadFile = File(...)):
    tmp = Path(tempfile.gettempdir()) / file.filename
    with open(tmp, "wb") as f:
        f.write(await file.read())

    question = transcribe(str(tmp))
    ctx = retrieve_context(question)
    ans = generate_answer(question, ctx)
    return {"question": question, "answer": ans, "ctx_used": len(ctx)}

#Agent-RAG

#@app.post("/voice_ask")
#async def voice_ask(file: UploadFile = File(...)):
 #   tmp = Path(tempfile.gettempdir()) / file.filename
  #  with open(tmp, "wb") as f:
    #     f.write(await file.read())
   # question = transcribe(str(tmp))
   # result = app_graph.invoke({"question": question})
   # return {"question": question, "answer": result["answer"], "ctx_used": len(result.get("context", []))}


# Optional: audio reply
# @app.post("/voice_talk")
# async def voice_talk(file: UploadFile = File(...)):
#     tmp = Path(tempfile.gettempdir()) / file.filename
#     with open(tmp, "wb") as f:
#         f.write(await file.read())
#     question = transcribe(str(tmp))
#     ctx = retrieve_context(question)
#     ans = generate_answer(question, ctx)
#     out_wav = Path(tempfile.gettempdir()) / "reply.wav"
#     tts_to_wav(ans, str(out_wav))
#     return FileResponse(str(out_wav), media_type="audio/wav", filename="answer.wav")
