"""Astuce de calcul mental — chaîne d'égalités alignées.

Une astuce se prouve avec 2 exemples chiffrés différents, pas le même nombre
répété : operation_data porte 3 frames (principe / exemple 1 / exemple 2),
render() sélectionne celui de `stage` (1/2/3) — une image différente par
illustration au lieu de la même chaîne répétée 3 fois.
"""

from PIL import Image, ImageDraw

from generators.math_renderers.compose import GREEN_RESULT, INK, NAVY, get_font

FONT_SIZE_TITRE = 46
FONT_SIZE_LIGNE = 54
LINE_GAP = 90
ARROW_COLOR = NAVY


def _render_frame(titre: str, etapes: list) -> Image.Image:
    """titre : ex "Multiplier par 5". etapes : lignes successives, dernière = résultat (vert)."""
    font_titre = get_font(FONT_SIZE_TITRE)
    font_ligne = get_font(FONT_SIZE_LIGNE)

    widths = [font_ligne.getlength(l) for l in etapes]
    title_w = font_titre.getlength(titre)
    content_w = int(max(widths + [title_w]) + 80)
    content_h = 100 + len(etapes) * LINE_GAP + 40

    content = Image.new("RGBA", (content_w, content_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)

    cx = content_w / 2
    draw.text((cx - title_w / 2, 20), titre, font=font_titre, fill=NAVY)

    y = 100
    for i, ligne in enumerate(etapes):
        # Vert réservé au résultat vérifié d'une chaîne à 2+ lignes — un frame
        # à une seule ligne (principe en mots) reste en encre neutre.
        color = GREEN_RESULT if len(etapes) > 1 and i == len(etapes) - 1 else INK
        w = widths[i]
        draw.text((cx - w / 2, y), ligne, font=font_ligne, fill=color)
        if i < len(etapes) - 1:
            arrow_y = y + LINE_GAP - 26
            draw.line([(cx, arrow_y), (cx, arrow_y + 18)], fill=ARROW_COLOR, width=3)
            draw.polygon(
                [(cx - 7, arrow_y + 12), (cx + 7, arrow_y + 12), (cx, arrow_y + 22)],
                fill=ARROW_COLOR,
            )
        y += LINE_GAP

    return content


def render(titre: str, frames: list, stage: int = 1) -> Image.Image:
    """frames : [{"etapes": [...]}, {"etapes": [...]}, {"etapes": [...]}] — principe/exemple1/exemple2.

    stage (1/2/3) sélectionne le frame correspondant.
    """
    frame = frames[stage - 1]
    return _render_frame(titre, frame["etapes"])
