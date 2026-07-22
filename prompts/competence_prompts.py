"""Templates de prompts images Type B — Compétence scolaire (validés prod).

Maths (ADDENDUM v2.6) : les opérations posées passent désormais par
generators/math_renderers/ (code, 0€, 0 hallucination) — PROMPT_COMPETENCE_CONCEPT
ne sert plus que pour les sujets sans calcul exact (image_route=gpt_image),
ex : symétrie, fractions en parts, unités de mesure.
"""

PROMPT_COMPETENCE_CONCEPT = """\
Background: clean white French school notebook page, Seyès grid style,
subtle paper texture, vertical 9:16 format.

STRICT EDUCATIONAL ACCURACY — French Éducation Nationale standards, grade {niveau}.
Concept to illustrate (no exact calculation involved):
{description_visuelle}

Clear, minimalist pedagogical diagram. If arrows or numbers are needed, keep
them simple and accurate — no invented values. No cartoon style, no Curio
character.

Magazine clipping style, fine white border, soft drop shadow.
Empty space at bottom 30% for captions. No watermark.
"""

PROMPT_COMPETENCE_FRANCAIS = """\
Background: clean white French school notebook page, Seyès grid style,
subtle paper texture, vertical 9:16 format.

Main visual, occupying roughly 55% of the page, centered in the upper 2/3:
a single photorealistic photo, like a Wikipedia or magazine photo, no cartoon,
no Curio character: {sujet_photo}
This photo illustrates the key word below — do not substitute any other
subject, do not reuse a generic or unrelated scene.

Below the photo, ONE single short word in large bold black handwritten-style
text, correctly spelled: "{mot_cle}"
Color ONLY the letter "{lettre_cle}" inside that word in a bright contrasting
blue — every other letter of the word stays black.

CRITICAL — DO NOT DRAW ANYTHING ELSE:
- No sentence, no rule, no test, no correct/incorrect comparison, no ✅/❌,
  no paragraph of any kind. The single word above is the ONLY text on this
  image. All pedagogical explanation is spoken in the audio narration only —
  a full paragraph here would be illegible on a phone screen.
- Leave the bottom 30% of the image completely empty (plain notebook
  background, nothing drawn there) — that zone is reserved for video
  captions and must stay clear.

Magazine clipping style, fine white border, soft drop shadow. No watermark.
"""


def build_concept_prompt(description_visuelle, niveau):
    """Sujet maths sans calcul exact (image_route=gpt_image) : data issu du script.json."""
    return PROMPT_COMPETENCE_CONCEPT.format(description_visuelle=description_visuelle, niveau=niveau)


def build_francais_prompt(data):
    """data : dict issu du script.json (exemples exacts fournis par Claude).

    v2.9 : l'image ne dessine plus que sujet_photo + mot_cle/lettre_cle (un mot
    court, une lettre en couleur) — regle_exacte/exemple_*/test_*/conclusion_*
    ne sont plus imprimés sur l'image (illisible sur mobile), ils alimentent
    uniquement la narration audio.
    """
    return PROMPT_COMPETENCE_FRANCAIS.format(
        sujet_photo=data["sujet_photo"],
        mot_cle=data["mot_cle"],
        lettre_cle=data["lettre_cle"],
    )
