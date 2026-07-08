"""Sous-titres SRT via Whisper local (CLI openai-whisper, coût 0$).

Règles d'affichage (validées prod) :
- Une seule phrase à l'écran à la fois, jamais deux. « Attends... » s'affiche
  seul, le reste du hook n'apparaît que quand il est prononcé.
- Chaque sous-titre est calé sur les timestamps mot à mot de Whisper.
- Phrase trop longue pour 2 lignes de 28 caractères : coupée en plusieurs
  sous-titres consécutifs, aux frontières de mots.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from config import WHISPER_MODEL

WHISPER_FALLBACK = Path.home() / "Library/Python/3.9/bin/whisper"

MAX_LINE_CHARS = 28
MAX_LINES = 2
SENTENCE_END = re.compile(r"[.!?…]$|\.\.\.$")


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


def _join(words):
    """Assemble des mots Whisper en texte : pas d'espace avant ' ou - (qu'il, Abonne-toi)."""
    out = ""
    for w in words:
        token = w["word"].strip()
        if out and not token.startswith(("'", "-", ",", ".", "…")):
            out += " "
        out += token
    return out


def _wrap(text):
    """Coupe un texte en lignes de MAX_LINE_CHARS max, aux espaces."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= MAX_LINE_CHARS or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _chunk_sentence(sentence):
    """Découpe une phrase trop longue en morceaux équilibrés de ≤ 2 lignes."""
    from math import ceil

    lines = _wrap(_join(sentence))
    k = ceil(len(lines) / MAX_LINES)
    if k <= 1:
        return [sentence]
    total = len(_join(sentence))
    target = total / k
    chunks, current, current_len = [], [], 0
    for w in sentence:
        current.append(w)
        current_len += len(w["word"].strip()) + 1
        if len(chunks) < k - 1 and current_len >= target:
            chunks.append(current)
            current, current_len = [], 0
    if current:
        chunks.append(current)
    # garde-fou : si un morceau dépasse encore 2 lignes, coupe glouton
    safe = []
    for chunk in chunks:
        if len(_wrap(_join(chunk))) <= MAX_LINES:
            safe.append(chunk)
            continue
        part = []
        for w in chunk:
            if len(_wrap(_join(part + [w]))) > MAX_LINES and part:
                safe.append(part)
                part = [w]
            else:
                part.append(w)
        if part:
            safe.append(part)
    return safe


def _sentences_from_words(words):
    """Groupe les mots Whisper en phrases, puis en blocs affichables ≤ 2 lignes.

    words : [{"word": " Attends...", "start": 0.0, "end": 0.6}, ...]
    Retourne [(texte, start, end)]. Une phrase à l'écran maximum.
    """
    sentences, current = [], []
    for w in words:
        current.append(w)
        if SENTENCE_END.search(w["word"].strip()):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)

    blocks = []
    for sentence in sentences:
        blocks.extend(_chunk_sentence(sentence))

    result = []
    for i, chunk in enumerate(blocks):
        text = "\n".join(_wrap(_join(chunk)))
        start = chunk[0]["start"]
        end = chunk[-1]["end"] + 0.25
        if i + 1 < len(blocks):
            end = min(end, blocks[i + 1][0]["start"])
        result.append((text, start, end))
    return result


def _srt_time(seconds):
    ms = round(seconds * 1000)
    h, rest = divmod(ms, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_subtitles(audio_path, output_dir, initial_prompt=None):
    """Transcrit l'audio choisi en subtitles.srt (une phrase par sous-titre).

    initial_prompt : passer la narration exacte du script pour guider Whisper
    (orthographe, noms propres) — indispensable pour un média éducatif.
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
        "--output_format", "json",
        "--output_dir", str(output_dir),
        "--task", "transcribe",
        "--verbose", "False",
        "--word_timestamps", "True",
    ]
    if initial_prompt:
        cmd += ["--initial_prompt", initial_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Whisper a échoué : {result.stderr.strip()[-500:]}")

    produced = output_dir / f"{audio_path.stem}.json"
    if not produced.exists():
        raise RuntimeError(f"Whisper n'a pas produit {produced.name}")
    data = json.loads(produced.read_text())
    produced.unlink()
    words = [w for seg in data["segments"] for w in seg.get("words", [])]
    if not words:
        raise RuntimeError("Whisper n'a renvoyé aucun timestamp de mot.")

    entries = []
    for i, (text, start, end) in enumerate(_sentences_from_words(words), start=1):
        entries.append(f"{i}\n{_srt_time(start)} --> {_srt_time(end)}\n{text}\n")
    target.write_text("\n".join(entries))
    print(f"  [ok] {target.name} ({len(entries)} sous-titres, 1 phrase max à l'écran)")
    return target
