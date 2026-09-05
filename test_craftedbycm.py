"""Aperçus des reconstructions @craftedbycm.

Chaque short analysé de la chaîne donne une composition Remotion qui refait sa
technique à l'identique (remotion/src/craftedbycm/). Ce script rend l'aperçu
d'une composition, pour validation avant de passer à la suivante.

    python test_craftedbycm.py 01                 # LA version officielle
    python test_craftedbycm.py 01 blanc           # un poste précis, seul
    python test_craftedbycm.py 01 tous            # les quatre, un rendu chacun
    python test_craftedbycm.py 01 sequence        # l'enchaînement, un seul rendu

La VERSION OFFICIELLE est le rendu sans argument : un seul poste, `officiel`
— le premier téléviseur généré, retenu par Benjamin comme le plus naturel des
cinq. C'est celle-là qu'on sort quand on demande « le motion design télé ».

Le mode `sequence` reproduit le short d'origine, où le poste change en coupe
sèche pendant que le plan continue. Il est conservé comme variante, pas comme
livrable par défaut. Les rendus poste par poste ne servent qu'à vérifier
qu'aucun modèle ne casse la mise en page.

Le plan source est une photo déjà téléchargée pour le reel « lacs roses » :
le sujet n'a aucune importance ici, seule la technique d'habillage est jugée.

Rien n'est écrit dans output/ : les rendus partent dans testing_remotion/.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.resolve()
REMOTION_DIR = REPO / "remotion"
PUBLIC_DIR = REMOTION_DIR / "public" / "craftedbycm"
ASSETS = REPO / "assets/craftedbycm"
OUT_DIR = REPO / "testing_remotion" / "craftedbycm"
PLATE_SOURCE = REPO / "testing_remotion/curio_reel_local/photos/lac_aerien.jpg"

COMPOSITIONS = {
    "01": "craftedbycm-01",
}
DEFAULT_TV = "officiel"
SOLO_DURATION = 150  # 5 s

# L'enchaînement du short : un premier plan qui laisse le temps du recul et de
# la pose du texte, une salve rapide de postes auditionnés, puis on se repose
# sur le premier. 30 fps — la salve tourne à deux tiers de seconde par poste.
SEQUENCE = [
    ("bois", 84),
    ("blanc", 21),
    ("noir", 18),
    ("portable", 21),
    ("bois", 66),
]

# Images fixes de contrôle : pendant le recul de caméra, puis une fois posé.
STILLS = {"reveal": 34, "final": 110}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def tv_entry(meta: dict) -> dict:
    return {
        "plate": f"craftedbycm/{meta['plate']}",
        "screenRect": meta["screenRect"],
    }


def text_band(metas) -> tuple[int, int]:
    """Enveloppe commune à tous les postes de la séquence : le texte est le
    point fixe, il ne doit pas sauter d'une coupe à l'autre."""
    tops = [m["tvRect"]["y"] for m in metas]
    bottoms = [m["tvRect"]["y"] + m["tvRect"]["height"] for m in metas]
    return min(tops) - 40, max(bottoms) + 50


def build_props(plates: dict, shots) -> dict:
    """`shots` : liste de (nom de poste, durée en images)."""
    ordre = list(dict.fromkeys(name for name, _ in shots))
    metas = [plates[n] for n in ordre]
    top, bottom = text_band(metas)
    return {
        "tvs": [tv_entry(m) for m in metas],
        "shots": [{"tv": ordre.index(n), "duration": d} for n, d in shots],
        "textTop": top,
        "textBottom": bottom,
    }


def render(composition: str, label: str, props: dict, work: Path, stills: bool) -> None:
    props_path = work / f"props_{label}.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))
    props_args = [f"--props={props_path}"]

    total = sum(s["duration"] for s in props["shots"])
    print(f"\n=== {label} — {len(props['shots'])} plan(s), {total} images "
          f"({total / 30:.2f} s)")

    video = work / f"{composition}_{label}.mp4"
    print("[1/2] rendu vidéo")
    run(["npx", "remotion", "render", "src/index.experiments.ts", composition,
         str(video), *props_args, "--log=error"], cwd=REMOTION_DIR)
    final_video = OUT_DIR / f"{composition}_{label}.mp4"
    shutil.copyfile(video, final_video)
    print(f"✅ {final_video}")

    if not stills:
        return
    print("[2/2] images fixes de contrôle")
    for name, frame_no in STILLS.items():
        still = work / f"{composition}_{label}_{name}.png"
        run(["npx", "remotion", "still", "src/index.experiments.ts", composition,
             str(still), *props_args, f"--frame={frame_no}", "--log=error"],
            cwd=REMOTION_DIR)
        final_still = OUT_DIR / f"{composition}_{label}_{name}.png"
        shutil.copyfile(still, final_still)
        print(f"✅ {final_still}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMPOSITIONS:
        sys.exit(f"usage: python {Path(__file__).name} {'|'.join(COMPOSITIONS)} "
                 f"[poste|tous|sequence]")
    composition = COMPOSITIONS[sys.argv[1]]

    plates = json.loads((ASSETS / "tv_plates.json").read_text())["plates"]
    choix = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TV
    if choix == "sequence":
        manquants = [n for n, _ in SEQUENCE if n not in plates]
        if manquants:
            sys.exit(f"postes absents de tv_plates.json : {', '.join(manquants)}")
        travaux = [("sequence", SEQUENCE, False)]
    elif choix == "tous":
        travaux = [(n, [(n, SOLO_DURATION)], True) for n in sorted(plates)]
    elif choix in plates:
        travaux = [(choix, [(choix, SOLO_DURATION)], True)]
    else:
        sys.exit(f"poste inconnu : {choix} — disponibles : "
                 f"{', '.join(sorted(plates))}, tous, sequence")

    if not PLATE_SOURCE.exists():
        sys.exit(f"plan source introuvable : {PLATE_SOURCE}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PLATE_SOURCE, PUBLIC_DIR / "plate.jpg")
    for meta in plates.values():
        shutil.copyfile(ASSETS / meta["plate"], PUBLIC_DIR / meta["plate"])

    # Dossier temp système : son chemin ne contient aucun point. Le CLI Remotion
    # découpe le chemin absolu entier sur les points pour deviner une extension
    # (bug amont, cf. CLAUDE.md v2.19).
    work = Path(tempfile.mkdtemp(prefix="craftedbycm_"))
    try:
        for label, shots, stills in travaux:
            render(composition, label, build_props(plates, shots), work, stills)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
