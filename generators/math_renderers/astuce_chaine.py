"""Astuce de calcul mental — chaîne d'égalités alignées (ADDENDUM v2.6 §7)."""

from PIL import Image, ImageDraw

from generators.math_renderers.compose import GREEN_RESULT, INK, NAVY, get_font

FONT_SIZE_TITRE = 46
FONT_SIZE_LIGNE = 54
LINE_GAP = 90
ARROW_COLOR = NAVY


def render(titre: str, etapes: list) -> Image.Image:
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
        color = GREEN_RESULT if i == len(etapes) - 1 else INK
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
