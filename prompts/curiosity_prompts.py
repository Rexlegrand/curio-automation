"""Templates de prompts images Type A — Curiosité du jour."""

BACKGROUNDS = {
    "sport": "football stadium at golden hour, French flags, crowd blurred",
    "combat": "MMA octagon cage arena at night, dramatic spotlight, blurred cheering crowd, professional fight venue ambiance",
    "velo": "Tour de France mountain road at golden hour, cheering crowd waving French flags, blurred peloton of cyclists in the background",
    "nature": "relevant natural environment (fjord, ocean, meadow, etc.)",
    "histoire": "relevant historical setting, dramatic lighting",
    "maths": "giant chalkboard with relevant equation, classroom ambiance",
    "science": "scientific laboratory, colorful liquids, dramatic lighting",
    "transport": "train station platform, departure board showing SUPPRIMÉ",
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
Background: {background_thematique}
Pixar-quality rendering. Ultra detailed feathers.
No text. No watermark. Vertical 9:16.
"""

PROMPT_MINIATURE = """\
Instagram feed thumbnail for an educational Reel, vertical 9:16 canvas.
Follow EXACTLY the layout and typography style of the provided reference
thumbnail (notebook page background, tilted magazine-clipping photos).

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


def get_background(theme):
    return BACKGROUNDS.get(theme, BACKGROUNDS["default"])


def build_illustration_prompt(description_visuelle):
    return PROMPT_ILLUSTRATION.format(description_visuelle=description_visuelle)


def build_hook_frame_prompt(theme):
    return PROMPT_HOOK_FRAME.format(background_thematique=get_background(theme))


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
