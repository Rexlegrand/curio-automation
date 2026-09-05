"""Génère le hook frame du reel « le Sahara nourrit l'Amazonie ».

Appel unique à GPT Image 2, en image-to-image, avec deux références :
le fond pastel choisi par Benjamin et la référence canonique du personnage
Curio. Le fond doit être repris TEL QUEL — c'est tout l'objet de le passer en
entrée plutôt que de le décrire.

Hors pipeline : ce reel a sept beats montés à la main, il ne passe pas par
main.py. Le coût est affiché et confirmé avant l'appel, règle §17.2 du brief.
"""

import base64
import sys
from contextlib import ExitStack
from pathlib import Path

from openai import OpenAI

from config import (
    COST_IMAGE,
    ENV,
    IMAGE_SIZE,
    IMAGE_SIZE_FALLBACK,
    OPENAI_IMAGE_MODEL,
)

REPO = Path(__file__).parent.resolve()
FOND = REPO / "assets/sahara_amazonie/hook_fond_ciel.png"
CURIO = REPO / "assets/curio_reference/curio_character_ref.png"
TARGET = REPO / "assets/sahara_amazonie/hook_frame.png"

QUALITY = "high"  # le hook est le premier plan vu, il ne se rattrape pas au montage

PROMPT = """\
Use the attached pastel sky image EXACTLY as the background — same colours,
same clouds, same positions. Do not redraw it, do not restyle it, do not add
or move any cloud. Composite the character onto it.

Character: the Curio penguin from the attached character reference — cute blue
and white penguin, large expressive eyes, red knitted scarf, holding a DJI
wireless microphone with a furry windscreen close to his beak.
Extremely surprised expression, eyes wide open, beak partially open in shock.
Direct eye contact with the camera. Medium shot from the waist up.
Pixar-quality 3D rendering, ultra detailed feathers, soft contact shadow under
the character so he sits in the scene instead of floating on it.

Composition: character perfectly centered horizontally, head in the upper half,
standing clear of the clouds already present in the background.
Leave the bottom 25% of the frame free of the character — subtitles go there.
No text. No watermark. Vertical 9:16.
"""


def main() -> None:
    for p in (FOND, CURIO):
        if not p.exists():
            sys.exit(f"référence manquante : {p}")

    print(f"GPT Image 2, qualité {QUALITY}, 1 image — coût estimé ~{COST_IMAGE:.3f}$")
    print(f"références : {FOND.name}, {CURIO.name}")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")

    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])
    with ExitStack() as stack:
        files = [stack.enter_context(open(p, "rb")) for p in (FOND, CURIO)]
        try:
            result = client.images.edit(
                model=OPENAI_IMAGE_MODEL, image=files, prompt=PROMPT,
                size=IMAGE_SIZE, quality=QUALITY, n=1,
            )
        except Exception as exc:
            if "size" not in str(exc).lower():
                raise
            print(f"Taille {IMAGE_SIZE} refusée, bascule sur {IMAGE_SIZE_FALLBACK}.")
            for f in files:
                f.seek(0)
            result = client.images.edit(
                model=OPENAI_IMAGE_MODEL, image=files, prompt=PROMPT,
                size=IMAGE_SIZE_FALLBACK, quality=QUALITY, n=1,
            )

    TARGET.write_bytes(base64.b64decode(result.data[0].b64_json))
    print(f"\n✅ {TARGET}")


if __name__ == "__main__":
    main()
