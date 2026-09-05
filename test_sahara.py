"""Aperçus du reel « le Sahara nourrit l'Amazonie ».

Un beat par composition, rendu et validé isolément avant d'être assemblé —
le reel fait sept beats et une reprise complète à chaque essai coûterait des
minutes de rendu pour rien.

    python test_sahara.py 03

Rien n'est écrit dans output/ : les rendus partent dans testing_remotion/.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.resolve()
REMOTION_DIR = REPO / "remotion"
OUT_DIR = REPO / "testing_remotion" / "sahara"

BEATS = {
    "00": ("sahara-00-stage", "banc d'essai — bascule plein écran / carte"),
    "hook": ("sahara-hook", "le hook animé, sous-titré"),
    "cta": ("sahara-cta", "le CTA, sous-titré"),
    "01": ("sahara-01-hook", "le hook — dune, raccord sec, canopée"),
    "02": ("sahara-02-deux-mondes", "les deux mondes — deux fenêtres"),
    "03": ("sahara-03-route", "le voyage — globe et trajectoire"),
    "04": ("sahara-04-camions", "le chiffre — la flotte qui recule"),
    "05": ("sahara-05-deux-sols", "pourquoi ça compte — avec et sans"),
    "06": ("sahara-06-revelation", "la révélation — orbite jusqu'au microscope"),
    "07": ("sahara-07-chute", "la chute — le lac mort nourrit la forêt"),
}

# Images fixes de contrôle : arrivée sur le globe, tracé en cours, tracé fini.
# Trois instants par beat, en proportion de sa durée : chaque beat a la sienne.
STILL_RATIOS = {"debut": 0.18, "milieu": 0.55, "fin": 0.94}

# Sans ce drapeau, Chrome headless ne crée aucun contexte WebGL sur cette
# machine ("Could not create a WebGL context ... BindToCurrentSequence failed")
# et tout rendu three.js échoue.
GL = ["--gl=angle"]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-2500:]}")
    return r


# Durées connues des beats, pour placer les images de contrôle. Les lire depuis
# Remotion demanderait un appel de plus par rendu, pour une valeur qui ne change
# qu'en même temps que le script.
# Calées sur la narration réelle — miroir de remotion/src/sahara/timing.ts.
DURATIONS = {
    "sahara-00-stage": 200,
    "sahara-hook": 104,
    "sahara-cta": 123,
    "sahara-01-hook": 149,
    "sahara-02-deux-mondes": 286,
    "sahara-03-route": 250,
    "sahara-04-camions": 286,
    "sahara-05-deux-sols": 255,
    "sahara-06-revelation": 444,
    "sahara-07-chute": 195,
}


def stills(composition: str) -> dict:
    n = DURATIONS[composition]
    return {name: round(r * n) for name, r in STILL_RATIOS.items()}


def assemble() -> None:
    """Colle les sept beats bout à bout, dans l'ordre du script.

    Ce n'est pas encore le montage final : il manque la voix, les sous-titres
    et le CTA, et les durées ici sont celles que j'ai posées beat par beat, pas
    celles de l'audio. C'est un aperçu pour juger l'enchaînement — le seul
    endroit où l'on voit si les switches tombent juste.
    """
    ordre = ["01", "02", "03", "04", "05", "06", "07"]
    clips = [OUT_DIR / f"{BEATS[b][0]}.mp4" for b in ordre]
    manquants = [c.name for c in clips if not c.exists()]
    if manquants:
        sys.exit("beats non rendus : " + ", ".join(manquants))

    liste = OUT_DIR / "_concat.txt"
    liste.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    final = OUT_DIR / "reel_sahara_apercu.mp4"
    # Réencodage plutôt que copie de flux : les beats sortent de rendus
    # séparés et un concat par copie laisserait des sauts d'horodatage.
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(liste), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30", str(final)])
    liste.unlink()
    total = sum(DURATIONS[BEATS[b][0]] for b in ordre)
    print(f"\n✅ {final}  —  {total} images, {total / 30:.2f} s")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "reel":
        assemble()
        return
    if len(sys.argv) < 2 or sys.argv[1] not in BEATS:
        sys.exit(f"usage: python {Path(__file__).name} {'|'.join(BEATS)}|reel")
    composition, titre = BEATS[sys.argv[1]]
    print(f"beat {sys.argv[1]} — {titre}")


    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Dossier temp système : son chemin ne contient aucun point. Le CLI Remotion
    # découpe le chemin absolu entier sur les points pour deviner une extension
    # (bug amont, cf. CLAUDE.md v2.19).
    work = Path(tempfile.mkdtemp(prefix="sahara_"))
    try:
        video = work / f"{composition}.mp4"
        print("[1/2] rendu vidéo")
        run(["npx", "remotion", "render", "src/index.experiments.ts", composition,
             str(video), *GL, "--log=error"], cwd=REMOTION_DIR)
        final = OUT_DIR / f"{composition}.mp4"
        shutil.copyfile(video, final)
        print(f"✅ {final}")

        print("[2/2] images fixes de contrôle")
        for name, frame_no in stills(composition).items():
            still = work / f"{composition}_{name}.png"
            run(["npx", "remotion", "still", "src/index.experiments.ts", composition,
                 str(still), f"--frame={frame_no}", *GL, "--log=error"],
                cwd=REMOTION_DIR)
            dst = OUT_DIR / f"{composition}_{name}.png"
            shutil.copyfile(still, dst)
            print(f"✅ {dst}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
