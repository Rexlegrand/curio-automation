"""Templates de prompts images Type B — Compétence scolaire (validés prod)."""

PROMPT_COMPETENCE_MATHS = """\
Background: clean white French school notebook page, Seyès grid style,
subtle paper texture, vertical 9:16 format.

STRICT EDUCATIONAL ACCURACY — French Éducation Nationale standards.
Grade: {niveau}
Operation: {type_operation}

Exact operation to represent (copy every digit precisely):
{operation_complete}

Step-by-step annotations:
{etapes_numerotees}

CRITICAL: Every digit must be mathematically correct.
The operation shown is {operation_resume}. Do not invent any number.
French Éducation Nationale method only.

Magazine clipping style, fine white border, soft drop shadow.
Empty space at bottom 30% for captions.
No extra decorations. No watermark.
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


def build_maths_prompt(data):
    """data : dict issu du script.json (clés maths exactes fournies par Claude)."""
    return PROMPT_COMPETENCE_MATHS.format(
        niveau=data["niveau"],
        type_operation=data["type_operation"],
        operation_complete=data["operation_complete"],
        etapes_numerotees=data["etapes_numerotees"],
        operation_resume=data["operation_resume"],
    )


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
