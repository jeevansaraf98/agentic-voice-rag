import os
import subprocess
import tempfile
from pathlib import Path
import logging, os
import time
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# Expect piper binary on PATH or set PIPER_BIN
PIPER_BIN = os.getenv("PIPER_BIN", "piper")
# Provide a default voice if you like, otherwise pass via args
DEFAULT_VOICE = os.getenv("PIPER_VOICE", "")  # path to .onnx
DEFAULT_VOICE_CFG = os.getenv("PIPER_VOICE_CFG", "")  # path to .json

def synthesize_wav(
    text: str,
    voice_model: str = None,
    voice_config: str = None,
    out_path: str = None,
    speaker: int = None,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
) -> str:
    """Call Piper CLI to synthesize WAV from text. Returns path to WAV."""
    if not text:
        raise ValueError("Empty text for TTS.")

    model = voice_model or DEFAULT_VOICE
    cfg = voice_config or DEFAULT_VOICE_CFG
    if not model:
        # allow running without TTS asset; return None gracefully
        return None

    if out_path is None:
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        out_path = path

    cmd = [PIPER_BIN, "-m", model, "-c", cfg, "-f", out_path]
    if speaker is not None:
        cmd += ["-s", str(speaker)]
    cmd += ["-l", str(length_scale), "-n", str(noise_scale), "-w", str(noise_w)]

    logger.info(f"piper | cmd={' '.join(cmd)}")
    t0 = time.time()
    proc = subprocess.Popen(...)

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        proc.communicate(input=text, timeout=120)
    finally:
        try:
            proc.kill()
        except Exception:
            pass

    if not Path(out_path).exists() or Path(out_path).stat().st_size == 0:
        raise RuntimeError("Piper did not produce audio. Check model paths and PIPER_BIN.")
    logger.info(f"piper | wrote={out_path} | {((time.time()-t0)*1000):.1f} ms")
    return out_path
