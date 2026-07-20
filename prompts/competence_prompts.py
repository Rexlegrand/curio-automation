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

STRICT EDUCATIONAL ACCURACY — French {niveau} grammar.
Grammar rule: {regle_exacte}

Show EXACTLY these examples (copy every word, accent, punctuation):
✅ Correct: "{exemple_correct}"
   Test: "{test_substitution_ok}" → ça marche → {conclusion_ok}

❌ Incorrect: "{exemple_incorrect}"
   Test: "{test_substitution_ko}" → ça ne marche pas → {conclusion_ko}

CRITICAL: Every word correctly spelled in French. All accents present.
Do not modify the examples above.

Magazine clipping style, fine white border, soft drop shadow.
Empty space at bottom 30% for captions. No watermark.
"""


def build_concept_prompt(description_visuelle, niveau):
    """Sujet maths sans calcul exact (image_route=gpt_image) : data issu du script.json."""
    return PROMPT_COMPETENCE_CONCEPT.format(description_visuelle=description_visuelle, niveau=niveau)


def build_francais_prompt(data):
    """data : dict issu du script.json (exemples exacts fournis par Claude)."""
    return PROMPT_COMPETENCE_FRANCAIS.format(
        niveau=data["niveau"],
        regle_exacte=data["regle_exacte"],
        exemple_correct=data["exemple_correct"],
        test_substitution_ok=data["test_substitution_ok"],
        conclusion_ok=data["conclusion_ok"],
        exemple_incorrect=data["exemple_incorrect"],
        test_substitution_ko=data["test_substitution_ko"],
        conclusion_ko=data["conclusion_ko"],
    )
