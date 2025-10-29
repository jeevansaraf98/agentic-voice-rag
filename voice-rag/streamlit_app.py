import streamlit as st
import requests
import os

st.set_page_config(page_title="Voice RAG Agent", page_icon="🗣️", layout="centered")

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.title("🗣️ Multimodal RAG Agent (LangGraph)")
tab1, tab2 = st.tabs(["Text Q&A", "Voice Q&A"])

with tab1:
    q = st.text_input("Ask a question")
    tts = st.checkbox("Read answer aloud (TTS)", value=False)
    if st.button("Ask", use_container_width=True) and q.strip():
        res = requests.get(f"{API_BASE}/ask", params={"q": q, "tts": tts}).json()
        st.write("**Route:**", res.get("route"))
        if res.get("strength"):
            st.write("**Context strength:**", res["strength"])
        if res.get("refused"):
            st.warning("Refused due to weak context.")
        st.markdown("**Answer:**")
        st.write(res.get("answer", ""))
        if res.get("tts_path"):
            try:
                audio_bytes = open(res["tts_path"], "rb").read()
                st.audio(audio_bytes, format="audio/wav")
            except Exception:
                pass
        with st.expander("Raw response"):
            st.json(res)

with tab2:
    tts2 = st.checkbox("Read answer aloud (TTS)", value=True, key="tts2")
    file = st.file_uploader("Upload audio file (wav/mp3/m4a)", type=["wav","mp3","m4a"])
    if st.button("Transcribe & Ask", use_container_width=True) and file:
        files = {"file": (file.name, file.getvalue(), file.type)}
        res = requests.post(f"{API_BASE}/voice_ask", files=files, params={"tts": tts2}).json()
        st.write("**Transcript:**", res.get("transcript",""))
        st.write("**Route:**", res.get("route"))
        if res.get("strength"):
            st.write("**Context strength:**", res["strength"])
        if res.get("refused"):
            st.warning("Refused due to weak context.")
        st.markdown("**Answer:**")
        st.write(res.get("answer", ""))
        if res.get("tts_path"):
            try:
                audio_bytes = open(res["tts_path"], "rb").read()
                st.audio(audio_bytes, format="audio/wav")
            except Exception:
                pass
        with st.expander("Raw response"):
            st.json(res)

st.sidebar.header("Runbook")
st.sidebar.code("""
# 1) Index
python ingest.py

# 2) Backend
uvicorn app:app --reload

# 3) Frontend
streamlit run streamlit_app.py
""")
