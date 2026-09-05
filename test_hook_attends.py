"""Frame de départ du hook « Attends » réutilisable (GPT Image 2, image-to-image).

Le hook réutilisable ne dit plus le sujet du jour, seulement « Attends » : son
décor est donc FIXE (mur lavande à nuages + néon curio.education du frame studio
validé le 31/08) et non plus dérivé de hook_background comme le hook Type A.

Deux entrées image, comme test_frame_curio_studio.py :
  1. le frame studio validé   → mur, nuages, néon, lumière, colorimétrie
  2. curio_character_ref.png  → modèle canonique du personnage

Deux différences avec le frame studio : le bureau et le micro broadcast sur bras
articulé disparaissent (remplacés par le petit micro DJI tenu à hauteur de
menton), et le micro ne doit JAMAIS couvrir le bec — le hook repose sur le fait
qu'on lise « Attends » sur les lèvres.

Prompt : prompts/hook_attends_reutilisable.md, section 1 (source unique, copié
ici mot pour mot).

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
FRAME_STUDIO = REPO / "testing_remotion" / "frame_curio_studio" / "frame_curio_studio_v2.png"
CURIO_REF = REFERENCE_DIR / "curio_character_ref.png"
OUT_DIR = REPO / "testing_remotion" / "hook_attends"

N_VARIANTES = 2
QUALITY = "high"

PROMPT = """\
IMAGE 1 is the SET to preserve. IMAGE 2 is the CANONICAL character model of
Curio the penguin — the single source of truth for how he must look.

BACKGROUND (from IMAGE 1, keep it exactly): the same lavender-purple studio
wall, the same sculpted 3D clouds floating in relief on the wall, the same
glowing warm neon sign reading "curio.education" with its two hanging cables in
the upper third of the frame. Same soft warm studio lighting, same colour
grading. Do not redesign the wall, do not change the clouds, do not change the
neon text.

REMOVE from IMAGE 1: the wooden desk and the black broadcast microphone on its
boom arm. Nothing replaces the desk — the penguin now stands in front of the
wall, framed from the waist up.

CHARACTER: render the penguin as the EXACT same character as in IMAGE 2, not a
look-alike. Matte, soft, ultra detailed fluffy feathers — no gloss, no plastic
sheen. Royal blue back and head, clean white face and belly, small rounded
orange beak, large round white eyes with bright blue irises, small tuft of
feathers on top of the head, chunky red knitted scarf with fringed ends. Both
blue flippers visible and readable, never melted into the body.

MICROPHONE: a small DJI wireless microphone with a fuzzy grey furry windscreen,
held in his right flipper and raised close to his beak — held BESIDE and
slightly BELOW the beak, at chin height. The microphone must NEVER cover, hide
or overlap the beak: the beak stays fully visible from the camera at all times.

POSE AND EXPRESSION: facing the camera straight on, direct eye contact. Very
surprised expression, eyes wide open, eyebrows raised, beak open mid-word as if
he has just interrupted the viewer to say one word.

FRAMING: vertical 9:16, medium shot from the waist up, penguin centered
horizontally, head in the upper-middle third, the neon sign readable above him.
Nothing important in the bottom 30% of the frame (subtitle safe zone).

Pixar-quality 3D rendering, cinematic soft lighting. No text other than the
existing neon sign. No watermark. No subtitles. Vertical 9:16.
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
    for p in (FRAME_STUDIO, CURIO_REF):
        if not p.exists():
            sys.exit(f"introuvable : {p}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])

    for i in range(1, N_VARIANTES + 1):
        out = OUT_DIR / f"hook_attends_frame_v{i}.png"
        if out.exists():
            print(f"déjà généré, ignoré : {out}")
            continue

        with ExitStack() as stack:
            files = [stack.enter_context(open(p, "rb")) for p in (FRAME_STUDIO, CURIO_REF)]
            try:
                res = call_api(client, files, IMAGE_SIZE)
            except BadRequestError:
                for f in files:
                    f.seek(0)
                res = call_api(client, files, IMAGE_SIZE_FALLBACK)

        out.write_bytes(base64.b64decode(res.data[0].b64_json))
        print(f"écrit : {out}")


if __name__ == "__main__":
    main()
