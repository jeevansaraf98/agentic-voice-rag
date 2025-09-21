# Agentic Voice-RAG — Speech → RAG → Agent → LLM (+ Streamlit UI + Piper TTS)

A **local, free** voice assistant that answers from your own docs using:
- **Whisper** (speech-to-text)
- **FAISS + sentence-transformers** (retrieval)
- **LangGraph** agent (router → retrieve → answer → judge)
- **Ollama** (local LLM runtime, e.g., `llama3`)
- **FastAPI + Uvicorn** (HTTP API with Swagger UI)
- **Streamlit** front-end
- **Piper** TTS (optional text-to-speech replies)

---

## 🧠 Architecture

```
🎤 Audio
  └─ Whisper (STT) → text
       └─ Agent (LangGraph):
            router → retrieve → answer → judge  [→ voice_out (Piper)]
                 │         │        │         └─ refuses if context is weak
                 │         │        └─ LLM via Ollama (llama3)
                 │         └─ FAISS + embeddings (sentence-transformers)
                 └─ router decides when RAG is needed
```

**HTTP Endpoints**
- `GET /ask` — text → RAG → answer (JSON)  
- `POST /ask` — same as above (JSON body)  
- `POST /voice_ask` — audio file → Whisper → RAG → answer (JSON)  
- `POST /voice_talk` — text → Piper → `answer.wav` (optional)  
- `/docs` — Swagger UI

---

## 📁 Project layout

```
agentic-voice-rag/
├─ app.py                # FastAPI endpoints (calls the agent graph)
├─ agent_graph.py        # LangGraph: router → retrieve → answer → judge
├─ rag_core.py           # retrieve_context(), generate_answer()
├─ stt_whisper.py        # transcribe() using Whisper
├─ tts_piper.py          # synthesize_wav() wrapper for Piper TTS
├─ ingest.py             # build FAISS index from data/raw/
├─ streamlit_app.py      # Streamlit front-end (Text + Voice)
├─ data/
│  ├─ raw/               # put .md/.txt/.pdf here
│  └─ index/             # FAISS index (generated; ignored by Git)
├─ requirements.txt
└─ .env                  # MODEL, EMBED_MODEL (optional)
```

---

## 🧩 What each library does (quick map)

| Piece | Why it exists | Where used |
|---|---|---|
| **FastAPI** | HTTP routes & auto-docs (OpenAPI/Swagger) | `app.py` |
| **Uvicorn** | ASGI server (async) | runs FastAPI |
| **Pydantic** | Request/response schemas | `app.py` models |
| **LangGraph** | Step orchestration as a state graph | `agent_graph.py` |
| **LangChain (+ community, HF, Ollama)** | RAG blocks & LLM bridge | `rag_core.py` |
| **sentence-transformers** | Text embeddings | `ingest.py`, `rag_core.py` |
| **FAISS (CPU)** | Vector search index | `ingest.py`, `rag_core.py` |
| **Whisper** | Speech-to-text | `stt_whisper.py` |
| **torch** | Backend for Whisper | runtime dep |
| **ffmpeg** *(tool)* | Audio decode/convert | system PATH |
| **Streamlit** | Simple front-end | `streamlit_app.py` |
| **Piper** *(tool)* | TTS synthesis | `tts_piper.py` shells out |
| **requests** | HTTP client for Streamlit | `streamlit_app.py` |
| **pypdf** | PDF ingestion (optional) | `ingest.py` |

> External tools (install separately): **ffmpeg**, **Ollama**, **Piper** (+ voice).

---

## ⚙️ Setup (Windows, Git Bash) — one-time

> Open **Git Bash** in your project root.

### 1) Python env & deps
```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
# If torch fails from PyPI:
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch
```

### 2) Tools
- **ffmpeg** (PowerShell/Admin):  
  `winget install --id Gyan.FFmpeg -e`
- **Ollama** (PowerShell/Admin):  
  `winget install --id Ollama.Ollama -e`  
  Pull a model: `ollama pull llama3`
- **Piper TTS** (optional): download **piper.exe** and a voice (`.onnx` + `.onnx.json`).  
  Put `piper.exe` on PATH or set `PIPER_BIN=C:\path\to\piper.exe`. Place voices under `voices/`.

### 3) Data → index
```bash
# put docs in data/raw/ (md/txt/pdf)
python ingest.py
```

### 4) Run backend
```bash
uvicorn app:app --reload
# Swagger: http://127.0.0.1:8000/docs
```

### 5) Run Streamlit UI (optional)
```bash
streamlit run streamlit_app.py
# UI on http://localhost:8501 (sidebar has FastAPI base URL)
```

---

## 🧠 The agent (LangGraph)

**`agent_graph.py`** coordinates four steps:

- **router** → decide if the question needs RAG or can be answered directly  
- **retrieve** → pull top-k chunks from FAISS  
- **answer** → generate a concise answer grounded in context  
- **judge** → refuse if context overlap is too low (avoid hallucinations)

Minimal integration in `app.py`:
```python
from agent_graph import app_graph

@app.get("/ask")
def ask_get(q: str):
    result = app_graph.invoke({"question": q})
    return {"answer": result["answer"], "ctx_used": len(result.get("context", []))}

@app.post("/ask")
def ask_post(body: AskIn):
    result = app_graph.invoke({"question": body.question})
    return {"answer": result["answer"], "ctx_used": len(result.get("context", []))}
```

---

## 🎙️ STT (Whisper) & 🗣️ TTS (Piper)

**Whisper tips (Windows/CPU):**
- Use `fp16=False` when calling `transcribe()` to avoid FP16 warnings.
- Normalize inputs to **16 kHz mono PCM** for best accuracy:
```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le ask.wav
```

**Piper usage (`tts_piper.py`):**
```python
from tts_piper import synthesize_wav
wav = synthesize_wav(
    "Hello from Piper!",
    voice_model="voices/en_US-lessac-medium.onnx"  # keep its .onnx.json next to it
)
```

**Add `/voice_talk` (optional):**
```python
from fastapi.responses import FileResponse
from tts_piper import synthesize_wav

@app.post("/voice_talk")
def voice_talk(body: AskIn):
    result = app_graph.invoke({"question": body.question})
    answer = result["answer"] or "Sorry, I have no answer."
    wav_path = synthesize_wav(answer, voice_model="voices/en_US-lessac-medium.onnx")
    return FileResponse(wav_path, media_type="audio/wav", filename="answer.wav")
```

---

## 🖥️ Streamlit UI (included)

Run:
```bash
streamlit run streamlit_app.py
```
- **Text Q&A** → calls `/ask` (GET or POST)  
- **Voice Q&A** → uploads audio to `/voice_ask`  
- (Optionally add a 3rd tab to call `/voice_talk` and play the WAV)

---

## 🔧 Tuning that matters

- **Docs**: keep focused; re-ingest after changes (`python ingest.py`)  
- **Embeddings**: start `all-MiniLM-L6-v2`; upgrade to `all-mpnet-base-v2` if recall is weak  
- **Retriever**: `k=4–6`; raise if answers feel generic  
- **Judge**: tighten the overlap threshold or switch to cosine similarity  
- **LLM**: `llama3:8B` Q4_0 is a solid default; smaller if latency is high  
- **Whisper**: use `tiny`/`base` on CPU; set `fp16=False`

---

## 🧹 Git hygiene

Add to `.gitignore`:
```
.venv/
.env
data/index/
data/raw/third_party/
voices/          # (voice binaries are large; keep out of Git)
*.wav
*.mp3
*.m4a
__pycache__/
*.pyc
```

If you accidentally committed `data/index/`:
```bash
git rm -r --cached data/index
echo "data/index/" >> .gitignore
git add .gitignore
git commit -m "Stop tracking FAISS index; ignore build artifacts"
git push
```

---

## 🧪 Quick tests

**Text**
```bash
curl "http://127.0.0.1:8000/ask?q=How%20do%20I%20import%20a%20WireGuard%20tunnel%20on%20Windows?"
```

**Voice**
```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le ask.wav
curl -X POST -F "file=@ask.wav" http://127.0.0.1:8000/voice_ask
```

**TTS**
```bash
curl -X POST http://127.0.0.1:8000/voice_talk \
  -H "Content-Type: application/json" \
  -d '{"question":"Give me a 1-line summary of WireGuard."}' \
  --output answer.wav
```

---

## ❓ Troubleshooting

- **`No module named whisper`** → `python -m pip install -U openai-whisper`  
- **`ffmpeg not found`** → install via winget/choco; reopen terminal  
- **`Connection refused 11434`** → run `ollama serve` and `ollama pull llama3`  
- **`stt_whisper not found`** → start Uvicorn from folder with `app.py`, or `uvicorn --app-dir . app:app --reload`  
- **`Piper binary not found`** → set `PIPER_BIN` or add `piper.exe` to PATH; ensure `.onnx` and `.onnx.json` exist
