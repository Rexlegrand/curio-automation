"""Test full motion design v2 (prototype) — reel manchot empereur du 20/08/2026.

Contrairement à test1 (06-CameraJourneyDynamic : zoom séquentiel spot par
spot, dézoom uniquement à la fin), test2 montre D'ABORD le plateau entier
(les 3 illustrations visibles d'un coup, comme un board) puis "clique" sur
chaque photo l'une après l'autre — zoom avant, hold, zoom arrière vers le
plateau — avant de passer à la suivante (composition Curio-BoardClickZoom,
remotion/src/curio-motion/07-BoardClickZoom.tsx). Hook et CTA restent les
assets Curio existants, inchangés (même choix que test1).

Réutilise compute_segments() et _render_captions_overlay() du pipeline réel
(generators/video_assembler.py) — mêmes durées et mêmes sous-titres que la
prod, aucune valeur recodée en dur ici.

Sortie : testing_remotion/manchot_20260820/test2/ (test only, jamais dans
output/, règle mémoire).
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
OUT_DIR = ROOT / "testing_remotion" / "manchot_20260820" / "test2"

BOARD_INTRO_SECONDS = 1.2
ZOOM_TRANSITION_SECONDS = 0.5


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
    overhead = BOARD_INTRO_SECONDS + len(hold_raw) * 2 * ZOOM_TRANSITION_SECONDS
    hold_sum = sum(hold_raw)
    hold_final = [h - overhead * (h / hold_sum) for h in hold_raw]

    print(f"  Audio : {AUDIO_PATH.name} — total montage {total}s")
    print(f"  Hold bruts (illus+ex-clip) : {[round(h, 2) for h in hold_raw]}")
    print(f"  Overhead (intro plateau + 6 transitions clic) : {overhead:.2f}s")
    print(f"  Hold finaux : {[round(h, 2) for h in hold_final]}")

    props = {
        "spots": [
            {"src": f"{PUBLIC_SUBDIR}/illus_{i + 1}.png", "holdSeconds": round(h, 3)}
            for i, h in enumerate(hold_final)
        ],
        "boardIntroSeconds": BOARD_INTRO_SECONDS,
        "zoomTransitionSeconds": ZOOM_TRANSITION_SECONDS,
    }
    props_path = REMOTION_DIR / "_board_click_zoom_props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    board_mp4 = OUT_DIR / "manchot_20260820_test2_board_only.mp4"

    print("  Remotion rend Curio-BoardClickZoom...")
    render_cmd = [
        "npx", "remotion", "render", "Curio-BoardClickZoom",
        str(board_mp4),
        f"--props={props_path}",
    ]
    result = subprocess.run(render_cmd, cwd=REMOTION_DIR, capture_output=True, text=True)
    props_path.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"Remotion a échoué (board click zoom) : {result.stderr.strip()[-1500:]}")
    print(f"  [ok] {board_mp4.name}")

    board_dur = BOARD_INTRO_SECONDS + sum(hold_final) + len(hold_final) * 2 * ZOOM_TRANSITION_SECONDS
    print(f"  Durée board click zoom : {board_dur:.2f}s (attendu ~{hold_sum:.2f}s)")

    normalize = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={VIDEO_FPS},format=yuv420p"
    )

    inputs = [hook_path, board_mp4, cta_path]
    durations = [hook_dur, board_dur, cta_dur]
    total_final = hook_dur + board_dur + cta_dur

    # Étape 1 — concat vidéo + audio, sans sous-titres.
    no_subs = OUT_DIR / "_tmp_no_subtitles.mp4"
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

    # Étape 2 — sous-titres Remotion (même moteur que la prod).
    print("  Remotion rend les sous-titres (une ligne à la fois)...")
    seq_dir, pad_width = _render_captions_overlay(REEL_DIR, total_final)
    print(f"  [ok] séquence de sous-titres rendue ({seq_dir.name})")

    # Étape 3 — incruste les sous-titres, réencode le final.
    final_mp4 = OUT_DIR / "manchot_20260820_test2.mp4"
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
