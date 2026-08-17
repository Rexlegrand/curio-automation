"""Montage final : FFmpeg (hook + illustrations + clips + audio) + Remotion (sous-titres).

La durée du reel est calée sur la durée de l'audio choisi (+ AUDIO_TAIL) :
les clips (hook, Curio A/B, CTA) gardent leur durée fixe (assets physiques à
longueur imposée) ; les 3 illustrations se partagent le temps restant au
prorata des timecodes RÉELS du script.json de ce reel (segments correspondant,
dans l'ordre, aux slots illustration_1/2/3 de TIMELINE) — jamais un poids
statique codé en dur, pour rester synchronisé même quand l'audio final
(ElevenLabs) s'éloigne de la durée nominale visée par le script (v2.8).

Audio des clips vidéo (hook, Curio A/B, CTA) : AUCUN — même quand le fichier
en porte une (assets/clips/curio_cta.mp4 a sa propre piste lip-sync Seedance),
elle n'est jamais mappée dans le montage. La voix ElevenLabs choisie (v1/v2)
est la SEULE piste audio du reel, plaquée en continu du début à la fin, hook
compris — le CTA doit suivre la même règle que le hook (v2.15, retour arrière
sur v2.14 : le lip-sync natif du clip CTA sonnait dans une voix différente de
celle d'ElevenLabs, cassait le rythme du reel).

Sous-titres : rendus par le projet Remotion (remotion/) au lieu d'un burn-in
FFmpeg/ASS. Une seule ligne à l'écran à la fois, jamais de wrap multi-lignes
(règle CLAUDE.md, resserrée par rapport à l'ancien ASS qui tolérait 2 lignes
empilées) — voir remotion/src/tiktok-captions/. Le montage se fait en 3 passes
FFmpeg/Remotion : (1) concat vidéo+audio sans sous-titres, (2) Remotion rend
une séquence PNG transparente calée sur les timestamps du subtitles.srt du
reel et sur la durée exacte du montage, (3) FFmpeg incruste cette séquence sur
la vidéo de l'étape 1 pour produire reel_final.mp4.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import (
    AUDIO_TAIL,
    ROOT,
    TIMELINE,
    VIDEO_BITRATE,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)

REMOTION_DIR = ROOT / "remotion"
REMOTION_COMPOSITION = "TikTokCaptions"

FFMPEG_DURATION = re.compile(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)")


def media_duration(path):
    """Durée d'un média en secondes, lue via ffmpeg -i (pas de ffprobe sur cette machine)."""
    result = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True)
    match = FFMPEG_DURATION.search(result.stderr)
    if not match:
        raise RuntimeError(f"Durée illisible pour {path}")
    h, m, s, cs = match.groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 10 ** len(cs)


def _segment_duration(segment):
    """Durée nominale d'un segment script.json : accepte {"start","end"} ou {"timecode":"a-b"}."""
    if "start" in segment and "end" in segment:
        return float(segment["end"]) - float(segment["start"])
    if "timecode" in segment:
        start, end = segment["timecode"].split("-")
        return float(end) - float(start)
    raise ValueError(f"segment sans start/end ni timecode exploitable : {segment!r}")


def _load_segments(output_dir):
    script_path = output_dir / "script.json"
    if not script_path.exists():
        raise FileNotFoundError(f"{script_path} introuvable — impossible de caler les illustrations sur les timecodes réels.")
    segments = json.loads(script_path.read_text()).get("segments")
    if not segments or len(segments) != len(TIMELINE):
        raise RuntimeError(
            f"script.json a {len(segments) if segments else 0} segments, {len(TIMELINE)} attendus "
            "(1 par slot de TIMELINE, même ordre) — structure incompatible avec le montage."
        )
    return [_segment_duration(s) for s in segments]


def compute_segments(output_dir, audio_path):
    """Retourne [(chemin, durée, trim_start)] : total = durée audio + AUDIO_TAIL.

    Les slots "fixed" gardent leur durée nominale de config. Le slot
    "dynamic" (CTA, v2.14) est mesuré sur le fichier réel plutôt que codé en
    dur, pour ne pas se désynchroniser si le clip est remplacé par un autre
    d'une durée différente. Les slots "flex" (illustrations) se partagent le
    budget restant au prorata de la durée nominale du segment script.json
    correspondant (même index que TIMELINE).
    """
    total = media_duration(audio_path) + AUDIO_TAIL
    nominal_durations = _load_segments(output_dir)

    imposed = {}
    for i, (source, spec) in enumerate(TIMELINE):
        if "fixed" in spec:
            imposed[i] = spec["fixed"]
        elif "dynamic" in spec:
            path = output_dir / source if isinstance(source, str) else source
            imposed[i] = media_duration(path)

    fixed = sum(imposed.values())
    flex_weights = sum(d for (_, spec), d in zip(TIMELINE, nominal_durations) if "flex" in spec)
    flex_budget = total - fixed
    if flex_budget < 1.5:
        raise RuntimeError(
            f"Audio trop court ({total - AUDIO_TAIL:.1f}s) : il reste {flex_budget:.1f}s "
            f"pour les 3 illustrations après les {fixed:.1f}s de clips fixes."
        )

    segments = []
    for i, ((source, spec), nominal) in enumerate(zip(TIMELINE, nominal_durations)):
        path = output_dir / source if isinstance(source, str) else source
        duration = imposed[i] if i in imposed else flex_budget * nominal / flex_weights
        segments.append((path, round(duration, 2), spec.get("trim_start", 0.0)))
    return segments, round(total, 2)


def _preflight(segments, output_dir, audio_path):
    missing = [str(p) for p, _, _ in segments if not p.exists()]
    if not audio_path.exists():
        missing.append(str(audio_path))
    if not (output_dir / "subtitles.srt").exists():
        missing.append(str(output_dir / "subtitles.srt"))
    if missing:
        raise FileNotFoundError("Fichiers manquants pour le montage :\n" + "\n".join(f"  - {m}" for m in missing))


def _render_captions_overlay(output_dir, total_seconds):
    """Rend les sous-titres (Remotion, une ligne à la fois) en séquence PNG transparente.

    srtText et totalSeconds passés via un fichier --props temporaire, jamais en
    JSON inline sur la ligne de commande : les apostrophes françaises du script
    ("qu'il", "l'appelle"...) cassent l'échappement shell. totalSeconds impose
    la durée exacte du montage à la composition Remotion (calculateMetadata,
    remotion/src/tiktok-captions/TikTokCaptions.tsx) — les sous-titres doivent
    durer aussi longtemps que la vidéo, jamais calés sur le seul dernier
    timestamp du SRT.

    seq_dir est un dossier temporaire système (tempfile.mkdtemp), jamais un
    sous-dossier de output_dir (v2.19) : le CLI Remotion découpe le CHEMIN
    ABSOLU ENTIER sur les points pour détecter une extension de fichier (bug
    amont, remotion/node_modules/@remotion/renderer/get-extension-of-filename.js
    fait un split('.') sur tout le chemin, pas juste le nom de fichier final).
    Le home du Mac (/Users/benjamin.ptryhuml/...) contient un point dans
    "benjamin.ptryhuml" : tout chemin de sortie de séquence sous output_dir
    (ou même relatif via "..", qui contient aussi des points) fait planter le
    render avec "The output directory of the image sequence cannot have an
    extension". Un dossier temp système (/var/folders/.../T/...) n'a pas ce
    problème car son chemin ne contient aucun point.
    """
    seq_dir = Path(tempfile.mkdtemp(prefix="remotion_captions_"))

    props_path = output_dir / "_remotion_props.json"
    props_path.write_text(
        json.dumps(
            {
                "srtText": (output_dir / "subtitles.srt").read_text(),
                "totalSeconds": total_seconds,
            },
            ensure_ascii=False,
        )
    )

    cmd = [
        "npx", "remotion", "render", REMOTION_COMPOSITION, str(seq_dir),
        "--sequence", "--image-format=png", f"--props={props_path}",
    ]
    result = subprocess.run(cmd, cwd=REMOTION_DIR, capture_output=True, text=True)
    props_path.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"Remotion a échoué : {result.stderr.strip()[-800:]}")

    expected_frames = round(total_seconds * VIDEO_FPS)
    frame_count = len(list(seq_dir.glob("element-*.png")))
    if frame_count != expected_frames:
        raise RuntimeError(
            f"Remotion a rendu {frame_count} images, {expected_frames} attendues "
            f"({total_seconds}s à {VIDEO_FPS}fps) — séquence incomplète."
        )

    pad_width = len(str(expected_frames - 1))
    return seq_dir, pad_width


def assemble_reel(output_dir, audio_path):
    """Assemble reel_final.mp4, durée calée sur l'audio. Skip si déjà présent."""
    output_dir = output_dir.resolve()
    audio_path = audio_path.resolve()
    target = output_dir / "reel_final.mp4"
    if target.exists():
        print(f"  [skip] {target.name} existe déjà")
        return target

    segments, total = compute_segments(output_dir, audio_path)
    _preflight(segments, output_dir, audio_path)

    normalize = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={VIDEO_FPS},format=yuv420p"
    )

    # Étape 1 — concat vidéo + audio, sans sous-titres, fichier intermédiaire.
    no_subs = output_dir / "_tmp_no_subtitles.mp4"
    cmd = ["ffmpeg", "-y"]
    filters = []
    for i, (path, duration, trim_start) in enumerate(segments):
        if path.suffix == ".png":
            cmd += ["-loop", "1", "-t", f"{duration}", "-framerate", str(VIDEO_FPS), "-i", str(path)]
            filters.append(f"[{i}:v]{normalize},setpts=PTS-STARTPTS[v{i}]")
        else:
            cmd += ["-i", str(path)]
            filters.append(
                f"[{i}:v]trim=start={trim_start}:end={trim_start + duration},"
                f"{normalize},setpts=PTS-STARTPTS[v{i}]"
            )
    audio_index = len(segments)
    cmd += ["-i", str(audio_path)]

    concat_in = "".join(f"[v{i}]" for i in range(len(segments)))
    filters.append(f"{concat_in}concat=n={len(segments)}:v=1:a=0[vout]")
    # Voix ElevenLabs seule, en continu sur tout le reel (hook + CTA compris,
    # v2.15) — les pistes audio natives des clips vidéo (dont curio_cta.mp4)
    # ne sont jamais mappées, quelle que soit leur présence dans le fichier.
    filters.append(f"[{audio_index}:a]apad[aout]")

    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(total),
        "-c:v", "libx264", "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
        "-r", str(VIDEO_FPS),
        "-c:a", "aac", "-b:a", "192k",
        no_subs.name,
    ]

    plan = " | ".join(f"{p.name} {d}s" + (f" (début +{t}s)" if t else "") for p, d, t in segments)
    print(f"  Plan de montage ({total}s) : {plan}")
    print(f"  Audio : ElevenLabs en continu sur les {total}s (voix native des clips ignorée)")
    print(f"  FFmpeg assemble {total}s de vidéo...")
    result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg a échoué (montage) : {result.stderr.strip()[-800:]}")

    # Étape 2 — sous-titres Remotion (une ligne à la fois, style TikTok).
    print("  Remotion rend les sous-titres (une ligne à la fois)...")
    seq_dir, pad_width = _render_captions_overlay(output_dir, total)
    print(f"  [ok] séquence de sous-titres rendue ({seq_dir.name})")

    # Étape 3 — incruste les sous-titres sur la vidéo, réencode reel_final.mp4.
    overlay_cmd = [
        "ffmpeg", "-y",
        "-i", no_subs.name,
        "-framerate", str(VIDEO_FPS), "-i", str(seq_dir / f"element-%0{pad_width}d.png"),
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]", "-map", "0:a",
        "-t", str(total),
        "-c:v", "libx264", "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
        "-r", str(VIDEO_FPS),
        "-c:a", "copy",
        target.name,
    ]
    print("  FFmpeg incruste les sous-titres...")
    result = subprocess.run(overlay_cmd, cwd=output_dir, capture_output=True, text=True)
    shutil.rmtree(seq_dir)
    no_subs.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg a échoué (incrustation sous-titres) : {result.stderr.strip()[-800:]}")

    print(f"  [ok] {target.name}")
    return target
