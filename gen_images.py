"""Génère les plans d'un reel de série — GPT Image 2, texte vers image.

    python gen_images.py mariannes [--yes]

Le sahara tirait ses huit plans de ChatGPT, à la main, hors pipeline : zéro
appel API mais une étape humaine par image. Ici les prompts vivent dans le
spec du reel et l'appel passe par l'API — c'est le seul changement, le style
demandé est le même (rendu 3D peint, pas photo).

Différence avec `gen_hook_sahara.py` : pas de référence en entrée. Aucun de
ces plans ne contient Curio, il n'y a donc rien à faire ressembler à une
image existante, et `images.generate` coûte le même prix que `images.edit`.

Une image déjà sur le disque n'est jamais regénérée : relancer ne refacture
rien. Effacer le PNG suffit à demander une autre version.
"""

import base64
import sys
from pathlib import Path

from openai import OpenAI

from config import COST_IMAGE, ENV, IMAGE_SIZE, IMAGE_SIZE_FALLBACK, OPENAI_IMAGE_MODEL
from reels import charger

REPO = Path(__file__).parent.resolve()

# `medium` et non `high` : ces plans passent sous un vignettage, un grain et un
# mouvement de caméra permanent, et la plupart sont vus moins de dix secondes.
# Le hook, lui, reste en `high` — c'est le seul plan qui ne se rattrape pas.
QUALITY = "medium"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug> [--yes]")
    reel = charger(sys.argv[1])
    out = REPO / f"assets/{reel.slug}"
    out.mkdir(parents=True, exist_ok=True)

    a_faire = {n: p for n, p in reel.images.items() if not (out / f"{n}.png").exists()}
    if not a_faire:
        print(f"{reel.slug} : les {len(reel.images)} plans sont déjà là")
        return

    print(f"{reel.titre} — GPT Image 2, qualité {QUALITY}, {len(a_faire)} image(s)")
    print(f"coût estimé ~{len(a_faire) * COST_IMAGE:.3f}$")
    for n in a_faire:
        print(f"  {n}")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")

    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])
    for nom, prompt in a_faire.items():
        # Les plans « Horizontal frame » sont des matières composées ensuite
        # dans le cadre : ils n'ont pas besoin du format vertical.
        taille = IMAGE_SIZE_FALLBACK if "Horizontal" in prompt else IMAGE_SIZE
        try:
            r = client.images.generate(model=OPENAI_IMAGE_MODEL, prompt=prompt,
                                       size=taille, quality=QUALITY, n=1)
        except Exception as exc:
            if "size" not in str(exc).lower():
                raise
            print(f"  taille {taille} refusée, bascule sur {IMAGE_SIZE_FALLBACK}")
            r = client.images.generate(model=OPENAI_IMAGE_MODEL, prompt=prompt,
                                       size=IMAGE_SIZE_FALLBACK, quality=QUALITY, n=1)
        (out / f"{nom}.png").write_bytes(base64.b64decode(r.data[0].b64_json))
        print(f"✅ {nom:16s} {(out / f'{nom}.png').stat().st_size // 1024} Ko")

    print(f"\n✅ {out}")


if __name__ == "__main__":
    main()
