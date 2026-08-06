"""Templates de prompts images Type A — Curiosité du jour.

v2.17 — fin du fond de hook dérivé d'un theme large (bug : un sujet MMA et un
sujet football partageaient la même famille "sport", un fond générique de
stade s'appliquait à tort à des sujets sans rapport visuel). Le fond du hook
vient désormais d'un unique champ `hook_background`, résolu une fois par
script_generator.py (soit un texte générique fixé pour une sous-catégorie
étroite et vraiment interchangeable — REUSABLE_HOOK_BACKGROUNDS ci-dessous —
soit un texte rédigé par Claude, spécifique au sujet réel de ce reel). Ce même
texte alimente aussi le prompt Seedance (prompts/seedance_prompts.py) : une
seule source, jamais deux descriptions de fond qui divergent.
"""

# Sous-catégories RÉUTILISABLES (v2.17) : le fond reste visuellement cohérent
# quel que soit le sujet précis à l'intérieur de la sous-catégorie. Liste
# volontairement étroite — ne jamais y rattacher un sujet par approximation
# (ex : tennis, athlétisme, escrime restent hors de "football"/"mma_combat").
REUSABLE_HOOK_BACKGROUNDS = {
    "cyclisme_tdf": "Tour de France mountain road at golden hour, cheering crowd waving French flags, blurred peloton of cyclists in the background",
    "football": "football stadium at golden hour, French flags, crowd blurred",
    "mma_combat": "MMA octagon cage arena at night, dramatic spotlight, blurred cheering crowd, professional fight venue ambiance",
    "maths": "giant chalkboard with relevant equation, classroom ambiance",
    "meteo": "scorching cityscape, heat shimmer, orange sky",
    "default": "soft colorful gradient background, neutral and clean",
}

PROMPT_ILLUSTRATION = """\
Background: clean white French school notebook page with discrete light blue
grid lines forming small squares (Seyès grid style), subtle paper texture,
soft shadow at bottom, vertical 9:16 format.

Centered on the page, occupying approximately 65% of visible area:
{description_visuelle}

The image is styled like a magazine clipping with a fine white border
and soft drop shadow, as if pasted on the notebook page.
Leave generous empty space at the bottom (30%) for future captions.
Photorealistic quality, like a photo from Wikipedia or a science magazine.
No text overlays. No subtitles. No watermark.
"""

PROMPT_HOOK_FRAME = """\
Curio character: cute blue and white penguin, large expressive eyes,
red knitted scarf, holding DJI wireless microphone with furry windscreen
close to his beak. Extremely surprised expression, eyes wide open,
beak partially open in shock. Direct eye contact with camera.
Medium shot from waist up. Perfectly centered for vertical 9:16.
Background: {hook_background}
Pixar-quality rendering. Ultra detailed feathers.
No text. No watermark. Vertical 9:16.
"""

PROMPT_MINIATURE = """\
Instagram feed thumbnail for an educational Reel, vertical 9:16 canvas.
The reference thumbnail is a LAYOUT/STYLE example ONLY — copy its notebook
page background, its tilted magazine-clipping photo framing, its logo badge
placement and its handwritten title typography. Do NOT reproduce its specific
photo content (do not draw a wheat field, harvest workers, or a calendar) and
do NOT reuse its title text — those are from a different, unrelated Reel.

CRITICAL FEED-CROP RULE: Instagram feed shows only the CENTRAL 4:3 crop of
this 9:16 canvas. ALL meaningful content (title, photos, Curio logo) must fit
entirely inside the central 4:3 area — keep the top ~20% and bottom ~20% of
the canvas as plain notebook-page background with nothing important in them.
Make the title and photos correspondingly compact.

{visual_instruction}
Add ONLY these two elements, both inside the central 4:3 safe area:
1. The provided Curio penguin logo as a small rounded app-icon badge,
   centered horizontally, at the BOTTOM EDGE of the central safe area.
2. The Reel title at the TOP EDGE of the central safe area, same style as
   the reference: bold rounded handwritten-style lettering, dark blue ink:
"{titre}"
Title must be perfectly legible and correctly spelled, every accent present.
No other text. No watermark.
"""


def resolve_hook_background(hook_subcategory, hook_background_specifique):
    """Source unique du fond de hook (v2.17) : texte générique fixe si la

    sous-catégorie est dans REUSABLE_HOOK_BACKGROUNDS (fond interchangeable
    par construction), sinon le texte spécifique rédigé par Claude pour le
    sujet réel de ce reel. Jamais de fallback approximatif sur une
    sous-catégorie voisine.
    """
    return REUSABLE_HOOK_BACKGROUNDS.get(hook_subcategory, hook_background_specifique)


def build_illustration_prompt(description_visuelle):
    return PROMPT_ILLUSTRATION.format(description_visuelle=description_visuelle)


def build_hook_frame_prompt(hook_background):
    return PROMPT_HOOK_FRAME.format(hook_background=hook_background)


VISUAL_REUSE = "Reuse the provided illustration image as the main visual."
VISUAL_GENERIC_MATHS = (
    "Generate a generic magazine-clipping visual on the theme of maths (pencils, ruler, "
    "notebook page, chalk doodle) in the same photographic/notebook style as the reference — "
    "no exact numbers, no calculation, purely decorative. Do not attempt to reproduce a "
    "mathematical operation."
)


def build_miniature_prompt(titre, reuse_illustration=True):
    """reuse_illustration=False : cas code_render maths — pas de photo à réutiliser en

    entrée (les chiffres du render code ne doivent jamais repasser par une
    génération GPT Image, qui pourrait les halluciner), on demande un visuel
    générique sans chiffre à la place.
    """
    visual_instruction = VISUAL_REUSE if reuse_illustration else VISUAL_GENERIC_MATHS
    return PROMPT_MINIATURE.format(titre=titre, visual_instruction=visual_instruction)
