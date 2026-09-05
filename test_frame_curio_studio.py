"""Régénération du frame de départ « Curio studio » (format deux carrés).

Le frame donné à Dreamina le 30/08 (~/Downloads/ChatGPT Image Aug 30...png) a
été fabriqué hors pipeline, à partir d'un prompt texte SANS aucune référence
injectée : le Curio obtenu est hors charte (plumage brillant/plastique au lieu
de mat et duveteux, proportions de tête/bec différentes, ailerons absents) et
ne raccorde pas avec le Curio du hook.

Ce script refait la même image en image-to-image GPT Image 2, avec DEUX entrées :
  1. le frame studio actuel  → décor, enseigne néon, bureau, cadrage, micro
  2. curio_character_ref.png → modèle canonique du personnage

Tout est conservé à l'identique (validé par Benjamin : cadrage, taille de Curio
dans le cadre et taille du micro sont bons). Seul le RENDU du personnage change,
et le micro remonte d'un cheveu.

Qualité "high" et non "medium" (image_generator.QUALITY_STANDARD) : c'est un
asset réutilisé sur tous les reels du format deux carrés, pas une image jetable.

Rien n'est écrit dans output/ : le rendu part dans testing_remotion/.
"""

import base64
import sys
from contextlib import ExitStack
from pathlib import Path

from openai import BadRequestError, OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from config import ENV, IMAGE_SIZE, IMAGE_SIZE_FALLBACK, OPENAI_IMAGE_MODEL, REFERENCE_DIR  # noqa: E402

REPO = Path(__file__).parent.resolve()
FRAME_ACTUEL = Path.home() / "Downloads/ChatGPT Image Aug 30, 2026, 08_52_46 PM.png"
CURIO_REF = REFERENCE_DIR / "curio_character_ref.png"
OUT_DIR = REPO / "testing_remotion" / "frame_curio_studio"

N_VARIANTES = 2
QUALITY = "high"

PROMPT = """\
IMAGE 1 is the scene to preserve. IMAGE 2 is the CANONICAL character model of
Curio the penguin — the single source of truth for how he must look.

Reproduce IMAGE 1 exactly: same lavender-purple studio wall, same glowing warm
neon sign reading "curio.education" with its two hanging cables, same sculpted
3D clouds floating on the wall, same wooden desk in the foreground, same camera
framing and crop, same broadcast microphone on its black boom arm at the same
size and same angle. Raise the microphone very slightly, by roughly 3% of the
image height — nothing more, its size must not change.

Change ONE thing only: render the penguin as the EXACT same character as in
IMAGE 2, not a look-alike.
- Feather texture: matte, soft, ultra detailed, visibly fluffy. Absolutely no
  gloss, no plastic sheen, no shiny specular highlights on the body or the head.
- Head shape, body proportions and silhouette identical to IMAGE 2, including
  the small tuft of feathers on top of the head.
- Eyes identical to IMAGE 2: large round white eyes with bright blue irises,
  thin dark outline, no thick cartoon eyebrows.
- Beak identical to IMAGE 2: small rounded orange beak, open, speaking.
- Colors identical to IMAGE 2: royal blue back and head, clean white face and
  belly, orange beak and feet.
- Red knitted scarf identical to IMAGE 2: same chunky wool knit texture, same
  red, same way it wraps around the neck with the fringed ends hanging down.
- Both blue flippers visible and readable, like in IMAGE 2 — not melted into
  the body.
- Same soft Pixar-quality rendering and same warm soft studio lighting as
  IMAGE 1, without any glossy rim light on the character.

Keep the penguin at exactly the same scale and the same position in the frame
as in IMAGE 1, facing the camera, beak open, speaking into the microphone.
No text other than the existing neon sign. No watermark. Vertical 9:16.
"""


def call_api(client, files, size):
    return client.images.edit(
        model=OPENAI_IMAGE_MODEL,
        image=files,
        prompt=PROMPT,
        size=size,
        quality=QUALITY,
        n=1,
    )


def main():
    for p in (FRAME_ACTUEL, CURIO_REF):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])

    for i in range(1, N_VARIANTES + 1):
        target = OUT_DIR / f"frame_curio_studio_v{i}.png"
        print(f"[{i}/{N_VARIANTES}] génération {target.name} (qualité {QUALITY})…")
        with ExitStack() as stack:
            files = [stack.enter_context(open(p, "rb")) for p in (FRAME_ACTUEL, CURIO_REF)]
            try:
                result = call_api(client, files, IMAGE_SIZE)
            except BadRequestError as exc:
                if "size" not in str(exc).lower():
                    raise
                print(f"    taille {IMAGE_SIZE} refusée, bascule sur {IMAGE_SIZE_FALLBACK}")
                files = [stack.enter_context(open(p, "rb")) for p in (FRAME_ACTUEL, CURIO_REF)]
                result = call_api(client, files, IMAGE_SIZE_FALLBACK)
        target.write_bytes(base64.b64decode(result.data[0].b64_json))
        print(f"    ✅ {target}")


if __name__ == "__main__":
    main()
