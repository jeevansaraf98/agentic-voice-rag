import time
import whisper
import logging, os
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

_model = None

def _load():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
        logger.info("whisper model loaded: base")

def transcribe(audio_path: str) -> str:
    _load()
    t0 = time.time()
    result = _model.transcribe(audio_path, fp16=False)
    text = result.get("text","").strip()
    logger.info(f"whisper.transcribe | len={len(text)} | {((time.time()-t0)*1000):.1f} ms")
    return text
