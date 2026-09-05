"""Génère les trois hook frames de la session de massification.

Même appel que `gen_hook_sahara.py` — GPT Image 2 en image-to-image sur la
référence canonique du personnage — à une différence près : le sahara passait
AUSSI un fond pastel choisi à la main (`hook_fond_ciel.png`), repris tel quel.
Les trois nouveaux sujets n'ont pas de fond préexistant, le décor est donc
décrit dans le prompt au lieu d'être fourni en entrée.

Ces images ne sont PAS le hook final : ce sont les images de départ que
Benjamin anime sous Dreamina en lip-sync sur la phrase `PHRASE`. C'est la
seule étape humaine de la session, et elle est lancée en premier pour que les
trois animations tournent pendant que le reste se construit.

Le cadrage est identique au sahara — Curio centré, tête dans la moitié haute,
25 % du bas laissés libres pour les sous-titres — pour que les trois reels
ouvrent exactement comme le reel de référence.
"""

import base64
import sys
from pathlib import Path

from openai import OpenAI

from config import COST_IMAGE, ENV, IMAGE_SIZE, IMAGE_SIZE_FALLBACK, OPENAI_IMAGE_MODEL

REPO = Path(__file__).parent.resolve()
CURIO = REPO / "assets/curio_reference/curio_character_ref.png"

QUALITY = "high"  # le hook est le premier plan vu, il ne se rattrape pas au montage

# Le décor de chaque hook, et la phrase que Curio doit dire en lip-sync.
# La phrase est reprise MOT POUR MOT par le segment `00-hook` de la narration
# ElevenLabs : c'est cette voix-là qu'on entend, jamais la piste Dreamina
# (règle v2.15 du brief).
REELS = {
    "mariannes": {
        "decor": "deep ocean underwater scene, dark teal-blue water, soft "
                 "god rays falling from the surface far above and fading into "
                 "black depths at the bottom of the frame, tiny suspended "
                 "particles catching the light",
        "phrase": "Attends... une montagne entière tiendrait là-dedans ?",
    },
    "soleil": {
        "decor": "outer space, deep black starfield, a huge warm orange solar "
                 "glow flooding in from the upper left corner, faint orange "
                 "rim light on everything, no planet visible",
        "phrase": "Attends... toutes les planètes réunies, c'est que des miettes ?",
    },
    "polders": {
        "decor": "wide flat Dutch landscape under a big grey-blue cloudy North "
                 "Sea sky, a long low green dyke crossing the horizon line, "
                 "calm grey water on the left, flat green farmland on the "
                 "right, soft northern daylight",
    "phrase": "Attends... ils ont pris leur pays à la mer ?",
    },
}

PROMPT = """\
Background: {decor}. Render it as a painted 3D environment, not a photo.

Character: the Curio penguin from the attached character reference — cute blue
and white penguin, large expressive eyes, red knitted scarf, holding a DJI
wireless microphone with a furry windscreen close to his beak.
Extremely surprised expression, eyes wide open, beak partially open in shock.
Direct eye contact with the camera. Medium shot from the waist up.
Pixar-quality 3D rendering, ultra detailed feathers, soft contact shadow under
the character so he sits in the scene instead of floating on it.

Composition: character perfectly centered horizontally, head in the upper half,
standing clear of the background elements.
Leave the bottom 25% of the frame free of the character — subtitles go there.
No text. No watermark. Vertical 9:16.
"""


def main() -> None:
    if not CURIO.exists():
        sys.exit(f"référence manquante : {CURIO}")
    cibles = {k: REPO / f"assets/{k}/hook_frame.png" for k in REELS}

    a_faire = {k: v for k, v in REELS.items() if not cibles[k].exists()}
    if not a_faire:
        print("les trois hook frames existent déjà, rien à faire")
        return

    print(f"GPT Image 2, qualité {QUALITY}, {len(a_faire)} image(s) — "
          f"coût estimé ~{len(a_faire) * COST_IMAGE:.3f}$")
    for k in a_faire:
        print(f"  {k:12s} -> {cibles[k].relative_to(REPO)}")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")

    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])
    for nom, reel in a_faire.items():
        cibles[nom].parent.mkdir(parents=True, exist_ok=True)
        prompt = PROMPT.format(decor=reel["decor"])
        with open(CURIO, "rb") as f:
            try:
                result = client.images.edit(
                    model=OPENAI_IMAGE_MODEL, image=[f], prompt=prompt,
                    size=IMAGE_SIZE, quality=QUALITY, n=1,
                )
            except Exception as exc:
                if "size" not in str(exc).lower():
                    raise
                print(f"Taille {IMAGE_SIZE} refusée, bascule sur {IMAGE_SIZE_FALLBACK}.")
                f.seek(0)
                result = client.images.edit(
                    model=OPENAI_IMAGE_MODEL, image=[f], prompt=prompt,
                    size=IMAGE_SIZE_FALLBACK, quality=QUALITY, n=1,
                )
        cibles[nom].write_bytes(base64.b64decode(result.data[0].b64_json))
        print(f"✅ {nom:12s} {cibles[nom]}")


if __name__ == "__main__":
    main()
