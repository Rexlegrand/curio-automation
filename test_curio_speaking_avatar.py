"""Test du Curio « avatar qui parle » — piste 100% locale, zéro coût, zéro API.

But de la piste : supprimer Dreamina du pipeline. Aujourd'hui le hook animé
passe par une plateforme externe (génération manuelle, dépôt du MP4 à la main,
~10 min et une tâche humaine par reel). Ici le personnage est un simple PNG
découpé, animé par Remotion : rendu local, gratuit, reproductible.

Ce script ne produit PAS un reel complet. Il rend un extrait de validation de
10s sur le reel « lacs roses » du 17/08, pour juger UNIQUEMENT l'effet
d'illumination :

    0 → 4s   Curio en grand au centre, fond flouté, il fait le hook
    4 → 10s  Curio se range en pastille ronde en bas à droite, fond net,
             il continue à parler façon vignette d'appel Discord

La lumière autour de Curio n'est pas décorative : elle suit le niveau RÉEL de
la voix, mesuré ici image par image (RMS sur l'audio ElevenLabs du reel) et
passé à Remotion en prop `levels`. Le rendu est donc déterministe et se recale
tout seul sur n'importe quel autre audio.

Rien n'est écrit dans output/ : le rendu part dans testing_remotion/.
"""

import array
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import VIDEO_FPS  # noqa: E402

REPO = Path(__file__).parent.resolve()
REEL_DIR = REPO / ("output/2026-08-17/il_existe_des_lacs_entierement_roses_leur_couleur_vient_de_"
                   "minuscules_algues_et_du_sel_de_loin_on_dirait_un_immense_lac_de_fraise_on_en_"
                   "trouve_par_exemple_en_australie_et_au_senegal")
CURIO_CUTOUT = REPO / "assets/curio_cutout/curio_flat.png"
REMOTION_DIR = REPO / "remotion"
PUBLIC_DIR = REMOTION_DIR / "public" / "curio-avatar"
OUT_DIR = REPO / "testing_remotion/curio_speaking_avatar"

DURATION_S = 10.0
HANDOFF_S = 4.0  # Curio quitte le centre pour la pastille
TOTAL_FRAMES = round(DURATION_S * VIDEO_FPS)
HANDOFF_FRAME = round(HANDOFF_S * VIDEO_FPS)

SAMPLE_RATE = 48000
# Deux couleurs d'anneau à comparer : le bleu de la charte Curio et le vert
# « quelqu'un parle » de Discord, qui est la référence visuelle du procédé.
GLOW_VARIANTS = {
    "bleu": "rgba(120, 200, 255, 0.85)",
    "vert": "rgba(60, 230, 130, 0.85)",
}

# Enveloppe de la voix : montée quasi instantanée (une syllabe doit allumer
# l'anneau tout de suite), descente lente (sinon l'anneau clignote et fatigue).
ATTACK = 0.55
RELEASE = 0.14


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace") if isinstance(r.stderr, bytes) else r.stderr
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{err[-1500:]}")
    return r


def voice_levels(audio_path, n_frames):
    """Niveau de voix par image de rendu, 0 → 1, lissé en attaque/relâchement."""
    raw = run([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", str(audio_path), "-t", f"{n_frames / VIDEO_FPS:.4f}",
        "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "-",
    ]).stdout
    pcm = array.array("h")
    pcm.frombytes(raw[: len(raw) - len(raw) % 2])

    per_frame = SAMPLE_RATE // VIDEO_FPS
    rms = []
    for i in range(n_frames):
        chunk = pcm[i * per_frame:(i + 1) * per_frame]
        if not chunk:
            rms.append(0.0)
            continue
        rms.append(math.sqrt(sum(s * s for s in chunk) / len(chunk)))

    # Normalisation sur le 95e centile plutôt que sur le maximum : un seul pic
    # (claquement, souffle) écraserait sinon tout le reste du reel.
    ref = sorted(rms)[int(len(rms) * 0.95)] or 1.0
    levels, prev = [], 0.0
    for v in rms:
        target = min(v / ref, 1.0)
        coeff = ATTACK if target > prev else RELEASE
        prev += (target - prev) * coeff
        levels.append(round(prev, 4))
    return levels


def stage_public_assets():
    """Remotion ne lit que remotion/public/ : on y dépose les sources."""
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)
    shutil.copyfile(CURIO_CUTOUT, PUBLIC_DIR / "curio_flat.png")
    shutil.copyfile(REEL_DIR / "illus_1.png", PUBLIC_DIR / "bg_hook.png")
    shutil.copyfile(REEL_DIR / "illus_2.png", PUBLIC_DIR / "bg_content.png")


def render(levels, glow_color, work, name):
    props = {
        "curioSrc": "curio-avatar/curio_flat.png",
        "bgHookSrc": "curio-avatar/bg_hook.png",
        "bgContentSrc": "curio-avatar/bg_content.png",
        "levels": levels,
        "handoffFrame": HANDOFF_FRAME,
        "glowColor": glow_color,
        "totalFrames": TOTAL_FRAMES,
    }
    # work est un dossier temp système : son chemin ne contient aucun point.
    # Le CLI Remotion découpe le chemin absolu entier sur les points pour
    # deviner une extension (bug amont, cf. CLAUDE.md v2.19).
    props_path = work / f"props_{name}.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))
    silent = work / f"avatar_{name}.mp4"
    run([
        "npx", "remotion", "render", "src/index.experiments.ts", "CurioSpeakingAvatar",
        str(silent), f"--props={props_path}", "--muted", "--log=error",
    ], cwd=REMOTION_DIR)

    final = OUT_DIR / f"curio_speaking_{name}.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(silent), "-i", str(REEL_DIR / "audio_v2.mp3"),
        "-map", "0:v", "-map", "1:a", "-t", f"{DURATION_S:.4f}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final),
    ])
    return final


def main():
    for p in (REEL_DIR, CURIO_CUTOUT):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="curio_avatar_"))
    print(f"[work] {work}")

    print("[1/3] enveloppe de la voix (RMS image par image)")
    levels = voice_levels(REEL_DIR / "audio_v2.mp3", TOTAL_FRAMES)
    parle = sum(1 for v in levels if v > 0.25)
    print(f"      {len(levels)} images — {parle} au-dessus du seuil de parole "
          f"({parle / len(levels) * 100:.0f}%), pic {max(levels):.2f}")

    print("[2/3] copie des sources dans remotion/public/curio-avatar/")
    stage_public_assets()

    finals = []
    try:
        for i, (name, color) in enumerate(GLOW_VARIANTS.items(), start=1):
            print(f"[3/3] rendu {i}/{len(GLOW_VARIANTS)} — anneau {name}")
            finals.append(render(levels, color, work, name))
    finally:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)

    shutil.rmtree(work, ignore_errors=True)
    print()
    for f in finals:
        print(f"✅ {f}")


if __name__ == "__main__":
    main()
