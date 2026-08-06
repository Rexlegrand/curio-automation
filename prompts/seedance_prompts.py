"""Template du prompt Seedance 2.0 pour le hook animé (copier-coller Dreamina).

v2.17 — le fond vient désormais du même champ hook_background que le hook
frame GPT Image 2 (résolu une fois par script_generator.py), plus jamais
dérivé indépendamment d'un theme large (source du bug fond foot/vélo croisé).
"""

PROMPT_SEEDANCE = """\
cute blue penguin character with red knitted scarf, holding a small DJI
wireless microphone with furry windscreen close to his beak, speaking
directly into the camera in French.
The character says out loud in French: "{phrase_hook}"
Beak and mouth moving naturally in perfect sync with the French phrase,
accurate lip-sync animation for each syllable.
{expression_faciale}: eyes wide open in surprise, then slight head tilt.
Background: {hook_background}
Static locked camera on Curio, no camera movement, no zoom.
9:16 vertical frame, cinematic lighting, Pixar-quality rendering.
Duration: 4 seconds. Generate audio.
"""


def build_seedance_prompt(phrase_hook, hook_background, expression_faciale="Surprised expression"):
    return PROMPT_SEEDANCE.format(
        phrase_hook=phrase_hook,
        expression_faciale=expression_faciale,
        hook_background=hook_background,
    )
