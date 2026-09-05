"""Rendu et montage du SECOND reel « le Sahara nourrit l'Amazonie ».

Même matière, autre ordre : on part du chiffre, on remonte à l'origine, puis on
explique. Et surtout, un montage BÂTI sur le switch plein écran / deux carrés
plutôt qu'un montage auquel on ajoute des bascules : chaque bloc d'explication
appelle Curio dans la carte du haut, chaque preuve reprend le plein écran.

    python test_sahara2.py beats    # rend les six compositions
    python test_sahara2.py reel     # assemble avec la voix, le hook et le CTA

La narration vit dans assets/sahara_amazonie/audio2/, les mots dans
remotion/public/sahara/mots2/. Le premier montage n'est pas touché.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.resolve()
REMOTION_DIR = REPO / "remotion"
AUDIO = REPO / "assets/sahara_amazonie/audio2"
OUT_DIR = REPO / "testing_remotion" / "sahara2"
HOOK = REPO / "assets/sahara_amazonie/hook_video.mp4"
CTA = REPO / "assets/clips/curio_cta.mp4"

W, H, FPS = 1080, 1920, 30
PAUSE = 10 / FPS
GL = ["--gl=angle"]

# Ordre du montage : segment de voix -> plan qui le porte.
PLAN = [
    ("00-hook", "sahara2-hook"),
    ("01-chiffre", "sahara2-01-chiffre"),
    ("02-origine", "sahara2-02-origine"),
    ("03-algues", "sahara2-03-algues"),
    ("04-voyage", "sahara2-04-voyage"),
    ("05-phosphore", "sahara2-05-phosphore"),
    ("06-chute", "sahara2-06-chute"),
    ("07-cta", "sahara2-cta"),
]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r


def duration(path: Path) -> float:
    """Pas de ffprobe sur cette machine (§16 du brief) : la durée se lit sur la
    sortie de ffmpeg."""
    r = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"durée illisible : {path}")


def timings() -> list:
    out, start = [], 0.0
    for seg, plan in PLAN:
        voix = duration(AUDIO / f"{seg}.mp3")
        d = voix + PAUSE
        out.append({"segment": seg, "plan": plan, "start": start, "voix": voix,
                    "duration": d})
        start += d
    return out


def rendre() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="sahara2_"))
    try:
        for _, plan in PLAN:
            dst = work / f"{plan}.mp4"
            print(f"  {plan}")
            run(["npx", "remotion", "render", "src/index.experiments.ts", plan,
                 str(dst), *GL, "--log=error"], cwd=REMOTION_DIR)
            shutil.copyfile(dst, OUT_DIR / f"{plan}.mp4")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n✅ {OUT_DIR}")


def normalise(src: Path, dst: Path, duree: float) -> None:
    """Ramène un plan externe au format du reel et coupe à sa durée de voix.
    La piste audio est jetée : une seule voix porte le reel (règle v2.15)."""
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", f"{duree:.3f}",
         "-an", "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(dst)])


def monter() -> None:
    t = timings()
    total = t[-1]["start"] + t[-1]["duration"]
    print(f"{'SEGMENT':14s} {'DÉBUT':>7s} {'VOIX':>7s} {'PLAN':>7s}  COMPOSITION")
    for e in t:
        print(f"{e['segment']:14s} {e['start']:7.2f} {e['voix']:7.2f} "
              f"{e['duration']:7.2f}  {e['plan']}")
    print(f"{'':14s} {'':7s} {'':7s} {total:7.2f}  TOTAL")

    work = Path(tempfile.mkdtemp(prefix="sahara2_montage_"))
    try:
        plans = []
        for e in t:
            dst = work / f"{e['segment']}.mp4"
            src = OUT_DIR / f"{e['plan']}.mp4"
            if not src.exists():
                sys.exit(f"plan non rendu : {src}")
            # Hook et CTA compris : montés bruts, ils échappaient au système de
            # sous-titres et le reel n'en avait ni sur sa première ni sur sa
            # dernière phrase.
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                 "-t", f"{e['duration']:.3f}", "-an",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                 "-pix_fmt", "yuv420p", str(dst)])
            plans.append(dst)

        liste = work / "plans.txt"
        liste.write_text("".join(f"file '{p}'\n" for p in plans))
        video = work / "video.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(liste), "-c", "copy", str(video)])

        # Chaque segment est prolongé de son silence AVANT le collage : padder
        # après coup ne mettrait la pause qu'à la toute fin de la piste.
        padded = []
        for e in t:
            dst = work / f"voix_{e['segment']}.m4a"
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-i", str(AUDIO / f"{e['segment']}.mp3"),
                 "-af", f"apad=pad_dur={PAUSE:.3f}", "-t", f"{e['duration']:.3f}",
                 "-c:a", "aac", "-b:a", "192k", str(dst)])
            padded.append(dst)
        liste_audio = work / "voix.txt"
        liste_audio.write_text("".join(f"file '{p}'\n" for p in padded))
        voix = work / "voix.m4a"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(liste_audio), "-c", "copy", str(voix)])

        final = OUT_DIR / "reel_sahara2.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voix),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
        (OUT_DIR / "timings.json").write_text(json.dumps(t, indent=2), encoding="utf-8")
        print(f"\n✅ {final}  —  {total:.2f} s")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("beats", "reel"):
        sys.exit(f"usage: python {Path(__file__).name} beats|reel")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (rendre if sys.argv[1] == "beats" else monter)()


if __name__ == "__main__":
    main()
