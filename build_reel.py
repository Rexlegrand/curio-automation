"""Montage d'un reel de série.

    python build_reel.py mariannes --timings   # durées à poser dans timing.ts
    python build_reel.py mariannes             # montage final

Généralisation de `build_reel_sahara.py`. Trois étapes, toutes locales :

  1. relevé de la durée réelle de chaque segment de narration ;
  2. concaténation des segments en une piste de voix continue, chacun prolongé
     de son silence AVANT le collage — padder après coup ne mettrait la pause
     qu'à la toute fin de la piste ;
  3. collage des plans Remotion sur cette piste.

La règle qui commande tout le reste : la vidéo suit l'audio, jamais l'inverse.
Chaque plan dure EXACTEMENT son segment de narration, ce qui garantit que les
switches tombent sur les phrases. Sur le sahara, les durées posées au jugé
s'en écartaient jusqu'à 3,1 secondes.

Le hook vient de Dreamina et le CTA d'un asset fixe, mais les deux passent
quand même par Remotion (compositions `<slug>-hook` et `<slug>-cta`) : montés
bruts en FFmpeg ils échappaient au système de sous-titres, et le reel n'en
avait ni sur sa première ni sur sa dernière phrase — les deux moments qui
décident qu'on reste ou qu'on passe.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from reels import charger

REPO = Path(__file__).parent.resolve()
W, H, FPS = 1080, 1920, 30

# Silence tenu après chaque segment de voix. Sans lui, une phrase démarre sur
# la dernière syllabe de la précédente et chaque changement de plan se lit
# comme une coupe. Miroir de PAUSE dans remotion/src/reels/timing.ts.
PAUSE = 10 / FPS


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r


def duration(path: Path) -> float:
    """Durée d'un média. Pas de ffprobe sur cette machine (§16 du brief) : on
    la lit sur la sortie de ffmpeg."""
    r = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"durée illisible : {path}")


def timings(reel) -> list:
    """Durée de chaque plan : son segment de voix, plus la pause qui le suit."""
    audio = REPO / f"assets/{reel.slug}/audio"
    out, start = [], 0.0
    for cle, _ in reel.segments:
        voix = duration(audio / f"{cle}.mp3")
        d = voix + PAUSE
        out.append({"segment": cle, "plan": f"{reel.slug}-{cle.split('-', 1)[1]}"
                    if cle[0].isdigit() else f"{reel.slug}-{cle}",
                    "start": start, "voix": voix, "duration": d})
        start += d
    return out


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug> [--timings]")
    reel = charger(sys.argv[1])
    out_dir = REPO / "testing_remotion" / reel.slug
    out_dir.mkdir(parents=True, exist_ok=True)

    t = timings(reel)
    total = t[-1]["start"] + t[-1]["duration"]

    print(f"{'SEGMENT':16s} {'DÉBUT':>8s} {'VOIX':>7s} {'PLAN':>7s}  COMPOSITION")
    for e in t:
        print(f"{e['segment']:16s} {e['start']:8.2f} {e['voix']:7.2f} "
              f"{e['duration']:7.2f}  {e['plan']}")
    print(f"{'':16s} {'':8s} {total:8.2f}  TOTAL")

    (out_dir / "timings.json").write_text(json.dumps(t, indent=2), encoding="utf-8")
    print(f"\n✅ {out_dir / 'timings.json'}")

    if "--timings" in sys.argv:
        print(f"\nDurées à poser dans remotion/src/reels/{reel.slug}.ts :")
        for e in t:
            print(f"  {e['segment']:16s} {round(e['duration'] * FPS):4d} images")
        return

    work = Path(tempfile.mkdtemp(prefix=f"{reel.slug}_montage_"))
    try:
        montage(reel, t, work, total, out_dir)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def montage(reel, t: list, work: Path, total: float, out_dir: Path) -> None:
    plans = []
    for e in t:
        dst = work / f"{e['segment']}.mp4"
        src = out_dir / f"{e['plan']}.mp4"
        if not src.exists():
            sys.exit(f"plan non rendu : {src}")
        # Réencodage plutôt qu'une copie de flux : les plans sortent de rendus
        # séparés et un concat par copie laisserait des sauts d'horodatage.
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

    audio = REPO / f"assets/{reel.slug}/audio"
    padded = []
    for e in t:
        dst = work / f"voix_{e['segment']}.m4a"
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(audio / f"{e['segment']}.mp3"),
             "-af", f"apad=pad_dur={PAUSE:.3f}", "-t", f"{e['duration']:.3f}",
             "-c:a", "aac", "-b:a", "192k", str(dst)])
        padded.append(dst)
    liste_audio = work / "voix.txt"
    liste_audio.write_text("".join(f"file '{p}'\n" for p in padded))
    voix = work / "voix.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(liste_audio), "-c", "copy", str(voix)])

    final = out_dir / f"reel_{reel.slug}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voix),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
    print(f"\n✅ {final}  —  {total:.2f} s")


if __name__ == "__main__":
    main()
