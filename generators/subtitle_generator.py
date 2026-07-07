"""Sous-titres SRT via Whisper local (CLI openai-whisper, coût 0$)."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from config import WHISPER_MODEL

WHISPER_FALLBACK = Path.home() / "Library/Python/3.9/bin/whisper"


def _fix_line_breaks(srt_text):
    """Recolle les élisions coupées par Whisper : « ou s / 'accrocher » → « ou / s'accrocher »."""
    srt_text = re.sub(r"[ ]([a-zA-Z])\n'", r"\n\1'", srt_text)
    srt_text = re.sub(r"([a-zA-Z]) '", r"\1'", srt_text)
    return srt_text


def _whisper_bin():
    found = shutil.which("whisper")
    if found:
        return found
    if WHISPER_FALLBACK.exists():
        return str(WHISPER_FALLBACK)
    sys.exit(
        "Erreur : commande 'whisper' introuvable.\n"
        "Installe openai-whisper : pip install openai-whisper"
    )


def generate_subtitles(audio_path, output_dir, initial_prompt=None):
    """Transcrit l'audio choisi en subtitles.srt. Skip si déjà présent.

    initial_prompt : passer la narration exacte du script pour guider Whisper
    (noms propres, orthographe) — indispensable pour un média éducatif.
    """
    target = output_dir / "subtitles.srt"
    if target.exists():
        print(f"  [skip] {target.name} existe déjà")
        return target

    print(f"  Whisper ({WHISPER_MODEL}) transcrit {audio_path.name}...")
    cmd = [
        _whisper_bin(),
        str(audio_path),
        "--language", "French",
        "--model", WHISPER_MODEL,
        "--output_format", "srt",
        "--output_dir", str(output_dir),
        "--task", "transcribe",
        "--verbose", "False",
        "--word_timestamps", "True",
        "--max_line_width", "28",
        "--max_line_count", "2",
    ]
    if initial_prompt:
        cmd += ["--initial_prompt", initial_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Whisper a échoué : {result.stderr.strip()[-500:]}")

    produced = output_dir / f"{audio_path.stem}.srt"
    if not produced.exists():
        raise RuntimeError(f"Whisper n'a pas produit {produced.name}")
    produced.rename(target)
    target.write_text(_fix_line_breaks(target.read_text()))
    print(f"  [ok] {target.name}")
    return target
