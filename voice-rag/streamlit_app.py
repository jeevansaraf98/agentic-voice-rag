import io
import requests
import streamlit as st

st.set_page_config(page_title="Agentic Voice‑RAG", page_icon="🎤", layout="centered")

st.title("🎤 Agentic Voice‑RAG — Streamlit UI")
st.caption("Speech → RAG → Agent → LLM (local)")

with st.sidebar:
    st.header("Server")
    api_base = st.text_input("FastAPI base URL", "http://127.0.0.1:8000")
    st.markdown(
        "- Start backend: `uvicorn app:app --reload`\n"
        "- Ollama running with a model (e.g., `llama3`)"
    )
    st.divider()
    st.header("About")
    st.write("Calls your FastAPI endpoints: `/ask`, `/voice_ask`.")

tab_text, tab_voice = st.tabs(["💬 Text Q&A", "🎙️ Voice Q&A"])

with tab_text:
    st.subheader("Ask a question (text)")
    q = st.text_input("Your question", placeholder="How do I import a WireGuard tunnel on Windows?")
    col1, col2 = st.columns([1,1])
    with col1:
        do_get = st.button("Ask (GET)")
    with col2:
        do_post = st.button("Ask (POST JSON)")

    if (do_get or do_post) and q.strip():
        try:
            if do_get:
                res = requests.get(f"{api_base}/ask", params={"q": q}, timeout=120)
            else:
                res = requests.post(f"{api_base}/ask", json={"question": q}, timeout=120)
            res.raise_for_status()
            data = res.json()
            st.success("Answer")
            st.write(data.get("answer", ""))
            with st.expander("Raw response"):
                st.json(data)
        except Exception as e:
            st.error(f"Request failed: {e}")

with tab_voice:
    st.subheader("Ask by voice (upload an audio file)")
    st.caption("Tip: short clips (5–20s), 16 kHz mono WAV work best. mp3/m4a also OK.")
    file = st.file_uploader("Choose an audio file", type=["wav","mp3","m4a","ogg","webm"], accept_multiple_files=False)
    if file is not None:
        st.audio(file)
    if st.button("Transcribe & answer", disabled=file is None):
        try:
            # Stream file as multipart
            files = {"file": (file.name, file.getbuffer(), "application/octet-stream")}
            res = requests.post(f"{api_base}/voice_ask", files=files, timeout=300)
            res.raise_for_status()
            data = res.json()
            st.success("Answer")
            st.write(data.get("answer",""))
            st.caption(f"Transcribed question: {data.get('question','')}")
            with st.expander("Raw response"):
                st.json(data)
        except Exception as e:
            st.error(f"Request failed: {e}")
