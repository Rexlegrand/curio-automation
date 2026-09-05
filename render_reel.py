"""Rend les plans d'un reel de série.

    python render_reel.py mariannes            # les neuf plans
    python render_reel.py mariannes 04-chiffre # un seul, pour itérer

Généralisation de `test_sahara.py`. Rien n'est écrit dans `output/` : les
rendus partent dans `testing_remotion/<slug>/`, où `build_reel.py` va les
chercher.

Chaque plan sort aussi trois images fixes de contrôle — début, milieu, fin —
pour juger un beat sans ouvrir la vidéo. C'est ce qui a permis de voir que le
mot « Phosphore » du sahara ne s'affichait pas.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from reels import charger

REPO = Path(__file__).parent.resolve()
REMOTION_DIR = REPO / "remotion"

# Trois instants par plan, en proportion de sa durée.
RATIOS = {"debut": 0.18, "milieu": 0.55, "fin": 0.94}

# Sans ce drapeau, Chrome headless ne crée aucun contexte WebGL sur cette
# machine ("Could not create a WebGL context ... BindToCurrentSequence failed")
# et tout rendu three.js échoue.
GL = ["--gl=angle"]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-2500:]}")
    return r


def composition(reel, cle: str) -> str:
    """Nom de la composition qui porte un segment. Même règle que
    `build_reel.py` : le numéro d'ordre du segment ne sert qu'au tri."""
    return f"{reel.slug}-{cle.split('-', 1)[1]}" if cle[0].isdigit() else f"{reel.slug}-{cle}"


def durees(reel) -> dict:
    """Durée de chaque plan, en images, lue sur `timings.json`.

    C'est le même fichier qui a servi à poser les durées des compositions :
    une seule source, donc aucun risque que les images de contrôle soient
    prises hors du plan. `npx remotion compositions` le donnerait aussi, mais
    au prix d'un démarrage de bundler par plan."""
    fichier = REPO / "testing_remotion" / reel.slug / "timings.json"
    if not fichier.exists():
        sys.exit(f"{fichier} manquant — lancer d'abord "
                 f"`python build_reel.py {reel.slug} --timings`")
    return {e["segment"]: round(e["duration"] * 30) for e in json.load(open(fichier))}


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug> [segment]")
    reel = charger(sys.argv[1])
    out = REPO / "testing_remotion" / reel.slug
    out.mkdir(parents=True, exist_ok=True)

    cles = reel.cles
    if len(sys.argv) > 2:
        if sys.argv[2] not in cles:
            sys.exit(f"segment inconnu : {sys.argv[2]} (parmi {', '.join(cles)})")
        cles = [sys.argv[2]]

    n_par_cle = durees(reel)
    for cle in cles:
        comp = composition(reel, cle)
        n = n_par_cle[cle]
        print(f"\n=== {comp}  ({n} images)")
        work = Path(tempfile.mkdtemp(prefix=f"{reel.slug}_"))
        try:
            video = work / f"{comp}.mp4"
            run(["npx", "remotion", "render", "src/index.experiments.ts", comp,
                 str(video), *GL, "--log=error"], cwd=REMOTION_DIR)
            shutil.copyfile(video, out / f"{comp}.mp4")
            print(f"✅ {out / f'{comp}.mp4'}")

            for nom, ratio in RATIOS.items():
                still = work / f"{comp}_{nom}.png"
                run(["npx", "remotion", "still", "src/index.experiments.ts", comp,
                     str(still), f"--frame={round(ratio * (n - 1))}", *GL, "--log=error"],
                    cwd=REMOTION_DIR)
                shutil.copyfile(still, out / f"{comp}_{nom}.png")
            print(f"✅ trois images de contrôle")
        finally:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
