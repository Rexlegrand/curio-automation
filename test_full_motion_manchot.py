"""Test full motion design (prototype) — reel manchot empereur du 20/08/2026.

Remplace les 2 clips talking-head (curio_a, curio_b) par UNE seule
composition Remotion (Curio-CameraJourneyDynamic, remotion/src/curio-motion/
06-CameraJourneyDynamic.tsx) qui enchaîne les 3 illustrations déjà générées
pour ce reel avec un mouvement de caméra continu (pan/zoom + dézoom final) —
plus aucune coupure vers un clip Curio qui parle. Hook et CTA restent les
assets Curio existants, inchangés (choix validé avec Benjamin).

Réutilise compute_segments() et _render_captions_overlay() du pipeline réel
(generators/video_assembler.py) pour que durées ET sous-titres restent
exactement calés sur l'audio ElevenLabs du reel, comme en production —
aucune durée recodée en dur, même moteur de sous-titres (Remotion
TikTokCaptions, une ligne à la fois).

Sortie : testing_remotion/manchot_20260820_full_motion_test.mp4 (test only,
jamais dans output/, règle mémoire).
"""

import json
import shutil
import subprocess

from config import ROOT, VIDEO_BITRATE, VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH
from generators.video_assembler import _render_captions_overlay, compute_segments

REEL_DIR = ROOT / "output" / "2026-08-20" / "le_manchot_empereur_qui_jeune_deux_mois_pour_son_uf"
AUDIO_PATH = REEL_DIR / "audio_v2.mp3"

REMOTION_DIR = ROOT / "remotion"
PUBLIC_SUBDIR = "curio_motion/test_manchot_20260820"
TESTING_DIR = ROOT / "testing_remotion"

TRAVEL_SECONDS = 0.8
DEZOOM_SECONDS = 1.4


def main():
    segments, total = compute_segments(REEL_DIR, AUDIO_PATH)
    # TIMELINE order : 0 hook, 1 illus_1, 2 curio_a, 3 illus_2, 4 curio_b, 5 illus_3, 6 cta
    hook_path, hook_dur, _ = segments[0]
    cta_path, cta_dur, _ = segments[6]

    hold_raw = [
        segments[1][1] + segments[2][1],  # illus_1 + curio_a
        segments[3][1] + segments[4][1],  # illus_2 + curio_b
        segments[5][1],                   # illus_3 seule
    ]
    overhead = 2 * TRAVEL_SECONDS + DEZOOM_SECONDS
    hold_sum = sum(hold_raw)
    hold_final = [h - overhead * (h / hold_sum) for h in hold_raw]

    print(f"  Audio : {AUDIO_PATH.name} — total montage {total}s")
    print(f"  Hold bruts (illus+ex-clip) : {[round(h, 2) for h in hold_raw]}")
    print(f"  Hold finaux (après retrait travel+dézoom) : {[round(h, 2) for h in hold_final]}")

    props = {
        "spots": [
            {"src": f"{PUBLIC_SUBDIR}/illus_{i + 1}.png", "holdSeconds": round(h, 3)}
            for i, h in enumerate(hold_final)
        ],
        "travelSeconds": TRAVEL_SECONDS,
        "dezoomSeconds": DEZOOM_SECONDS,
    }
    props_path = REMOTION_DIR / "_camera_journey_props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))

    TESTING_DIR.mkdir(exist_ok=True)
    camera_journey_mp4 = TESTING_DIR / "manchot_20260820_camera_journey.mp4"

    print("  Remotion rend Curio-CameraJourneyDynamic...")
    render_cmd = [
        "npx", "remotion", "render", "Curio-CameraJourneyDynamic",
        str(camera_journey_mp4),
        f"--props={props_path}",
    ]
    result = subprocess.run(render_cmd, cwd=REMOTION_DIR, capture_output=True, text=True)
    props_path.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"Remotion a échoué (camera journey) : {result.stderr.strip()[-1500:]}")
    print(f"  [ok] {camera_journey_mp4.name}")

    camera_journey_dur = sum(hold_final) + 2 * TRAVEL_SECONDS + DEZOOM_SECONDS
    print(f"  Durée camera journey : {camera_journey_dur:.2f}s (attendu ~{hold_sum:.2f}s)")

    normalize = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={VIDEO_FPS},format=yuv420p"
    )

    inputs = [hook_path, camera_journey_mp4, cta_path]
    durations = [hook_dur, camera_journey_dur, cta_dur]
    total_final = hook_dur + camera_journey_dur + cta_dur

    # Étape 1 — concat vidéo + audio, sans sous-titres.
    no_subs = TESTING_DIR / "_tmp_manchot_no_subtitles.mp4"
    cmd = ["ffmpeg", "-y"]
    filters = []
    for i, (path, dur) in enumerate(zip(inputs, durations)):
        cmd += ["-i", str(path)]
        filters.append(f"[{i}:v]trim=start=0:end={dur},{normalize},setpts=PTS-STARTPTS[v{i}]")
    audio_index = len(inputs)
    cmd += ["-i", str(AUDIO_PATH)]
    concat_in = "".join(f"[v{i}]" for i in range(len(inputs)))
    filters.append(f"{concat_in}concat=n={len(inputs)}:v=1:a=0[vout]")
    filters.append(f"[{audio_index}:a]apad[aout]")

    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(total_final),
        "-c:v", "libx264", "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
        "-r", str(VIDEO_FPS),
        "-c:a", "aac", "-b:a", "192k",
        str(no_subs),
    ]
    print(f"  FFmpeg assemble le montage sans sous-titres ({total_final:.2f}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg a échoué (montage) : {result.stderr.strip()[-1500:]}")

    # Étape 2 — sous-titres Remotion (une ligne à la fois, style TikTok, même
    # moteur que le pipeline réel — subtitles.srt du reel, calé sur total_final).
    print("  Remotion rend les sous-titres (une ligne à la fois)...")
    seq_dir, pad_width = _render_captions_overlay(REEL_DIR, total_final)
    print(f"  [ok] séquence de sous-titres rendue ({seq_dir.name})")

    # Étape 3 — incruste les sous-titres, réencode le final.
    final_mp4 = TESTING_DIR / "manchot_20260820_full_motion_test.mp4"
    overlay_cmd = [
        "ffmpeg", "-y",
        "-i", str(no_subs),
        "-framerate", str(VIDEO_FPS), "-i", str(seq_dir / f"element-%0{pad_width}d.png"),
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]", "-map", "0:a",
        "-t", str(total_final),
        "-c:v", "libx264", "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
        "-r", str(VIDEO_FPS),
        "-c:a", "copy",
        str(final_mp4),
    ]
    print("  FFmpeg incruste les sous-titres...")
    result = subprocess.run(overlay_cmd, capture_output=True, text=True)
    shutil.rmtree(seq_dir)
    no_subs.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg a échoué (incrustation sous-titres) : {result.stderr.strip()[-1500:]}")

    print(f"  [ok] {final_mp4}")


if __name__ == "__main__":
    main()
