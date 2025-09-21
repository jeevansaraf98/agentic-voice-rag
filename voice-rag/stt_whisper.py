import whisper

# Load once (choose "base" for CPU, "small"/"medium" if you have GPU)
_model = whisper.load_model("base")

def transcribe(audio_path: str) -> str:
    out = _model.transcribe(audio_path, fp16=False)
    return out.get("text", "").strip()

