"""Montage du reel « le Sahara nourrit l'Amazonie ».

Trois étapes, toutes locales sauf la narration déjà générée :

  1. concaténation des neuf segments de narration en une piste continue, et
     relevé des frontières réelles entre segments ;
  2. transcription Whisper SEGMENT PAR SEGMENT, jamais d'une traite : avec la
     narration entière en `initial_prompt`, Whisper recrache le prompt au lieu
     de transcrire (constaté sur le reel « lacs roses ») ;
  3. montage FFmpeg : hook Dreamina, sept beats Remotion, clip CTA, sur la
     piste de voix continue.

La règle qui commande tout le reste : la vidéo suit l'audio, jamais l'inverse.
Chaque beat dure EXACTEMENT son segment de narration, ce qui garantit que les
switches tombent sur les phrases. Les durées posées au jugé pendant la
construction des beats s'en écartaient jusqu'à 3,1 secondes.

La piste audio native du hook Dreamina et celle du clip CTA ne sont jamais
montées : une seule voix, du premier au dernier cadre (règle v2.15 du brief).
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.resolve()
AUDIO = REPO / "assets/sahara_amazonie/audio"
BEATS_DIR = REPO / "testing_remotion/sahara"
OUT_DIR = REPO / "testing_remotion/sahara"
HOOK = REPO / "assets/sahara_amazonie/hook_video.mp4"
CTA = REPO / "assets/clips/curio_cta.mp4"
WHISPER = Path.home() / "Library/Python/3.9/bin/whisper"

W, H, FPS = 1080, 1920, 30

# Silence tenu après chaque segment de voix. Sans lui, une phrase démarre sur
# la dernière syllabe de la précédente et chaque changement de plan se lit
# comme une coupe — c'est le reproche fait à la première version. Miroir de
# PAUSE dans remotion/src/sahara/timing.ts.
PAUSE = 10 / FPS

# Ordre du montage : segment de narration -> plan vidéo qui le porte.
PLAN = [
    ("00-hook", "sahara-hook"),
    ("01-hook-suite", "sahara-01-hook"),
    ("02-deux-mondes", "sahara-02-deux-mondes"),
    ("03-route", "sahara-03-route"),
    ("04-camions", "sahara-04-camions"),
    ("05-deux-sols", "sahara-05-deux-sols"),
    ("06-revelation", "sahara-06-revelation"),
    ("07-chute", "sahara-07-chute"),
    ("08-cta", "sahara-cta"),
]


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


def timings() -> list:
    """Durée de chaque plan : son segment de voix, plus la pause qui le suit."""
    out, start = [], 0.0
    for seg, plan in PLAN:
        voix = duration(AUDIO / f"{seg}.mp3")
        d = voix + PAUSE
        out.append({"segment": seg, "plan": plan, "start": start,
                    "voix": voix, "duration": d})
        start += d
    return out


def main() -> None:
    t = timings()
    total = t[-1]["start"] + t[-1]["duration"]

    print(f"{'SEGMENT':16s} {'DÉBUT':>8s} {'VOIX':>7s} {'PLAN':>7s}  COMPOSITION")
    for e in t:
        print(f"{e['segment']:16s} {e['start']:8.2f} {e['voix']:7.2f} "
              f"{e['duration']:7.2f}  {e['plan']}")
    print(f"{'':16s} {'':8s} {total:8.2f}  TOTAL")

    (OUT_DIR / "timings.json").write_text(json.dumps(t, indent=2), encoding="utf-8")
    print(f"\n✅ {OUT_DIR / 'timings.json'}")

    if "--timings" in sys.argv:
        print("\nDurées à poser dans remotion/src/sahara/timing.ts :")
        for e in t:
            if e["plan"].startswith("sahara-"):
                print(f"  {e['plan']:24s} {round(e['duration'] * FPS):4d} images")
        return

    work = Path(tempfile.mkdtemp(prefix="sahara_montage_"))
    try:
        montage(t, work, total)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def normalise(src: Path, dst: Path, duree: float) -> None:
    """Ramène un plan externe au format du reel et coupe à sa durée de voix.

    Le hook Dreamina sort en 720×1280 à 24,15 fps et le clip CTA a sa propre
    cadence : concaténés tels quels, FFmpeg produirait des sauts d'horodatage.
    La piste audio est jetée ici — une seule voix porte le reel, du premier au
    dernier cadre (règle v2.15).
    """
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", f"{duree:.3f}",
         "-an", "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(dst)])


def montage(t: list, work: Path, total: float) -> None:
    plans = []
    for e in t:
        dst = work / f"{e['segment']}.mp4"
        src = BEATS_DIR / f"{e['plan']}.mp4"
        if not src.exists():
            sys.exit(f"plan non rendu : {src}")
        # Tous les plans, hook et CTA compris, sortent maintenant de Remotion :
        # montés bruts en FFmpeg, les deux clips de Curio échappaient au
        # système de sous-titres et le reel n'en avait ni sur sa première ni
        # sur sa dernière phrase. Réencodage quand même — un concat par copie
        # de flux laisserait des sauts d'horodatage.
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

    final = OUT_DIR / "reel_sahara.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voix),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
    print(f"\n✅ {final}  —  {total:.2f} s")


if __name__ == "__main__":
    main()
