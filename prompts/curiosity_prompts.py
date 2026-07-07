"""Templates de prompts images Type A — Curiosité du jour."""

BACKGROUNDS = {
    "sport": "football stadium at golden hour, French flags, crowd blurred",
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
Instagram feed thumbnail for an educational Reel, vertical 9:16.
Follow EXACTLY the layout and typography style of the provided reference
thumbnail (notebook page background, tilted magazine-clipping photos).
Reuse the provided illustration image as the main visual.
Add ONLY these two elements:
1. The provided Curio penguin logo as a small rounded app-icon badge,
   centered at the bottom of the page (same placement as the reference).
2. The Reel title in the top safe zone, same style as the reference:
   bold rounded handwritten-style lettering, dark blue ink on the paper:
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


def build_miniature_prompt(titre):
    return PROMPT_MINIATURE.format(titre=titre)
