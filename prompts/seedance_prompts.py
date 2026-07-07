"""Template du prompt Seedance 2.0 pour le hook animé (copier-coller Dreamina)."""

from prompts.curiosity_prompts import get_background

PROMPT_SEEDANCE = """\
cute blue penguin character with red knitted scarf, holding a small DJI
wireless microphone with furry windscreen close to his beak, speaking
directly into the camera in French.
The character says out loud in French: "{phrase_hook}"
Beak and mouth moving naturally in perfect sync with the French phrase,
accurate lip-sync animation for each syllable.
{expression_faciale}: eyes wide open in surprise, then slight head tilt.
Background: {background_thematique}
Static locked camera on Curio, no camera movement, no zoom.
9:16 vertical frame, cinematic lighting, Pixar-quality rendering.
Duration: 4 seconds. Generate audio.
"""


def build_seedance_prompt(phrase_hook, theme, expression_faciale="Surprised expression"):
    return PROMPT_SEEDANCE.format(
        phrase_hook=phrase_hook,
        expression_faciale=expression_faciale,
        background_thematique=get_background(theme),
    )
