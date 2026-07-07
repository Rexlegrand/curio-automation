"""Montage final FFmpeg : hook + illustrations + clips + audio + sous-titres.

La durée du reel est calée sur la durée de l'audio choisi (+ AUDIO_TAIL) :
les clips gardent leur durée fixe, les illustrations se partagent le temps
restant au prorata de leur poids défini dans TIMELINE.
"""

import re
import subprocess

from config import (
    AUDIO_TAIL,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_MARGIN_V,
    TIMELINE,
    VIDEO_BITRATE,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)

# Style aligné sur la référence publiée @curio.education :
# blanc bold, contour noir épais, ombre légère, pas de boîte de fond
ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Curio,Arial,{SUBTITLE_FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,2,2,80,80,{SUBTITLE_MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

SRT_TIME = re.compile(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)")
FFMPEG_DURATION = re.compile(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)")


def _ass_time(h, m, s, ms):
    return f"{int(h)}:{int(m):02d}:{int(s):02d}.{int(ms) // 10:02d}"


def srt_to_ass(srt_path, ass_path):
    """Convertit le SRT Whisper en ASS stylé charte Curio (60px, blanc, contour noir, Y=75%)."""
    events = []
    block_text = []
    times = None
    lines = srt_path.read_text().splitlines() + [""]
    for line in lines:
        line = line.strip()
        match = SRT_TIME.match(line)
        if match:
            times = match.groups()
            block_text = []
        elif line == "":
            if times and block_text:
                start = _ass_time(*times[0:4])
                end = _ass_time(*times[4:8])
                text = "\\N".join(block_text)
                events.append(f"Dialogue: 0,{start},{end},Curio,,0,0,0,,{text}")
            times = None
            block_text = []
        elif times is not None and not line.isdigit():
            block_text.append(line)
    ass_path.write_text(ASS_HEADER + "\n".join(events) + "\n")
    return ass_path


def media_duration(path):
    """Durée d'un média en secondes, lue via ffmpeg -i (pas de ffprobe sur cette machine)."""
    result = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True)
    match = FFMPEG_DURATION.search(result.stderr)
    if not match:
        raise RuntimeError(f"Durée illisible pour {path}")
    h, m, s, cs = match.groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 10 ** len(cs)


def compute_segments(output_dir, audio_path):
    """Retourne [(chemin, durée, trim_start)] : total = durée audio + AUDIO_TAIL."""
    total = media_duration(audio_path) + AUDIO_TAIL
    fixed = sum(spec["fixed"] for _, spec in TIMELINE if "fixed" in spec)
    flex_weights = sum(spec["flex"] for _, spec in TIMELINE if "flex" in spec)
    flex_budget = total - fixed
    if flex_budget < 1.5:
        raise RuntimeError(
            f"Audio trop court ({total - AUDIO_TAIL:.1f}s) : il reste {flex_budget:.1f}s "
            f"pour les 3 illustrations après les {fixed:.0f}s de clips fixes."
        )
    segments = []
    for source, spec in TIMELINE:
        path = output_dir / source if isinstance(source, str) else source
        duration = spec["fixed"] if "fixed" in spec else flex_budget * spec["flex"] / flex_weights
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
    srt_to_ass(output_dir / "subtitles.srt", output_dir / "subtitles_styled.ass")

    normalize = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={VIDEO_FPS},format=yuv420p"
    )

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
    filters.append(f"{concat_in}concat=n={len(segments)}:v=1:a=0[vcat]")
    filters.append("[vcat]ass=subtitles_styled.ass[vout]")
    filters.append(f"[{audio_index}:a]apad[aout]")

    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(total),
        "-c:v", "libx264", "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
        "-r", str(VIDEO_FPS),
        "-c:a", "aac", "-b:a", "192k",
        target.name,
    ]

    plan = " | ".join(f"{p.name} {d}s" + (f" (début +{t}s)" if t else "") for p, d, t in segments)
    print(f"  Plan de montage ({total}s) : {plan}")
    print(f"  FFmpeg assemble {total}s de vidéo...")
    result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg a échoué : {result.stderr.strip()[-800:]}")
    print(f"  [ok] {target.name}")
    return target
