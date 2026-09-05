"""Génère le poste de télévision d'époque de la reconstruction craftedbycm-01.

La photo Wikimedia utilisée d'abord montrait un vrai poste, mais vu de trois
quarts et posé sur un meuble dans une pièce : trop loin, trop contextualisé,
rien à voir avec le cadre plein écran de la vidéo d'origine. Celle-ci utilise un
asset Adobe Stock — un poste détouré, de face, sur fond neutre.

On reproduit cet asset avec GPT Image 2 plutôt que de le dessiner : un poste
dessiné en CSS lit comme une illustration, ce qui a déjà été écarté.

L'écran est demandé en VERT UNI, pas en noir. Le vert donne une zone à détourer
sans ambiguïté et, surtout, les quatre coins exacts de la vitre — impossible à
relever de façon fiable sur un écran noir posé dans un caisson noir.

Deux variantes sont produites, pour choisir sur pièce.
"""

import base64
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from config import ENV, IMAGE_SIZE, OPENAI_IMAGE_MODEL  # noqa: E402

OUT_DIR = Path(__file__).parent.resolve() / "assets/craftedbycm"
N_VARIANTS = 2
QUALITY = "high"

PROMPT = """\
A vintage 1960s wooden television set, photographed straight on, perfectly
frontal, no perspective, no angle, perfectly centered in the frame.

The set fills most of the frame width. Warm walnut wood cabinet with a thick
rounded bezel, a narrow speaker grille and two chrome control knobs on the
right side panel, short splayed wooden legs at the bottom.

CRITICAL: the screen area is a completely FLAT, UNIFORM, SOLID BRIGHT GREEN
rectangle with softly rounded corners — pure chroma key green, absolutely no
reflection, no glare, no glass highlight, no gradient, no texture, no image on
it. The green must be perfectly even from edge to edge.

Background: pure solid black, empty, seamless studio backdrop. No floor, no
table, no furniture, no props, no shadow on the background. The television is
the only object.

Soft even studio lighting on the cabinet so the wood grain and the bezel are
clearly readable. Photorealistic product photography. Vertical 9:16 framing.
No text. No watermark. No people.
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])

    for i in range(1, N_VARIANTS + 1):
        target = OUT_DIR / f"tv_generated_v{i}.png"
        print(f"[{i}/{N_VARIANTS}] génération {target.name} ({QUALITY}, {IMAGE_SIZE})…")
        result = client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=PROMPT,
            size=IMAGE_SIZE,
            quality=QUALITY,
            n=1,
        )
        target.write_bytes(base64.b64decode(result.data[0].b64_json))
        print(f"    ✅ {target}")


if __name__ == "__main__":
    main()
