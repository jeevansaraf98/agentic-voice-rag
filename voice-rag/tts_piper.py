"""import subprocess
from pathlib import Path
import shutil

def tts_to_wav(text: str, out_path: str, voice="en_US-lessac-medium"):
    # If the 'piper' binary exists locally, use it; otherwise try docker exec into a 'piper' container.
    piper_bin = shutil.which("piper")
    if piper_bin:
        with open(out_path, "wb") as f:
            subprocess.run([piper_bin, "-m", voice, "-f", out_path],
                           input=text.encode("utf-8"), check=True)
        return out_path
    # fallback: docker exec (assumes a container named 'piper' is running)
    subprocess.run(["docker","exec","-i","piper","piper","-m",voice,"-f",out_path],
                   input=text.encode("utf-8"), check=True)
    return out_path
"""
"""
tts_piper.py — lightweight wrapper around the Piper TTS binary.

Usage (Windows):
1) Install Piper (binary) and a voice:
   - Put e.g. `piper.exe` on PATH.
   - Download a voice (e.g., `en_US-lessac-medium.onnx` + `en_US-lessac-medium.onnx.json`).
   - Place voice files in a folder, e.g., `voices/` in your project.
2) From Python:
   >>> from tts_piper import synthesize_wav
   >>> wav = synthesize_wav("Hello from Piper!", voice_model="voices/en_US-lessac-medium.onnx")

The wrapper shells out to `piper` and returns the WAV file path.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

__all__ = ["synthesize_wav", "find_piper"]


def find_piper() -> Optional[str]:
    """
    Locate the Piper binary.
    Resolution order:
      - PIPER_BIN env var
      - "piper" on PATH
      - "piper.exe" on PATH (Windows convenience)
    Returns the executable path or None.
    """
    env_bin = os.getenv("PIPER_BIN")
    if env_bin and Path(env_bin).exists():
        return env_bin
    for name in ("piper", "piper.exe"):
        path = shutil.which(name)
        if path:
            return path
    return None


def synthesize_wav(
    text: str,
    *,
    voice_model: str,
    voice_config: Optional[str] = None,
    out_path: Optional[str] = None,
    piper_bin: Optional[str] = None,
    speaker: Optional[int] = None,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
) -> str:
    """
    Synthesize `text` to a WAV file using Piper.

    Args:
        text: Text to speak.
        voice_model: Path to the `.onnx` voice model (e.g., `voices/en_US-lessac-medium.onnx`).
        voice_config: (Optional) Path to the matching `.json` config. If None, tries `<model>.json` beside `voice_model`.
        out_path: (Optional) Path to write WAV. If None, creates a temp file.
        piper_bin: (Optional) Override path to Piper binary. If None, tries `find_piper()`.
        speaker: (Optional) Speaker index for multi-speaker voices.
        length_scale, noise_scale, noise_w: Prosody controls passed to Piper.

    Returns:
        Path to the generated WAV file.

    Raises:
        FileNotFoundError: if Piper binary or voice files are missing.
        subprocess.CalledProcessError: if Piper exits non-zero.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty text passed to synthesize_wav()")

    piper = piper_bin or find_piper()
    if not piper:
        raise FileNotFoundError(
            "Piper binary not found. Set PIPER_BIN env var or add piper to PATH."
        )

    model_path = Path(voice_model)
    if not model_path.exists():
        raise FileNotFoundError(f"Voice model not found: {model_path}")

    cfg_path = Path(voice_config) if voice_config else model_path.with_suffix(model_path.suffix + ".json")
    if not cfg_path.exists():
        # Some distributions use ".onnx.json", others ".json"; try both
        alt_cfg = model_path.with_suffix(".json")
        if alt_cfg.exists():
            cfg_path = alt_cfg
        else:
            raise FileNotFoundError(f"Voice config not found: {cfg_path}")

    out_file = Path(out_path) if out_path else Path(tempfile.gettempdir()) / "piper_out.wav"

    cmd = [
        str(piper),
        "-m", str(model_path),
        "-c", str(cfg_path),
        "-f", str(out_file),
        "--length_scale", str(length_scale),
        "--noise_scale", str(noise_scale),
        "--noise_w", str(noise_w),
    ]
    if speaker is not None:
        cmd += ["--speaker", str(speaker)]

    # Piper reads text from stdin and writes WAV to -f <file>
    subprocess.run(cmd, input=text.encode("utf-8"), check=True, capture_output=True)
    return str(out_file)
