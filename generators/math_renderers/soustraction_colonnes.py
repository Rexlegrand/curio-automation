"""Soustraction posée en colonnes (méthode française), emprunt visible."""

from PIL import Image, ImageDraw

from generators.math_renderers.compose import GREEN_RESULT, INK, NAVY, STEP_RED, draw_col_text, get_font

COL_W = 56
FONT_SIZE = 60
FONT_SIZE_SMALL = 34


def compute_columns(nombre1: int, nombre2: int):
    """Colonne par colonne, de la droite vers la gauche. nombre1 >= nombre2 requis.

    Retourne (minuende, soustrait, digits_resultat, colonnes_avec_emprunt, largeur).
    colonnes_avec_emprunt[i] = True si la colonne i a prêté une dizaine à sa droite.
    """
    if nombre1 < nombre2:
        raise ValueError(f"soustraction_colonnes : {nombre1} < {nombre2}, résultat négatif impossible à poser")

    s1, s2 = str(nombre1), str(nombre2)
    width = max(len(s1), len(s2))
    s1, s2 = s1.rjust(width, "0"), s2.rjust(width, "0")

    borrow = 0
    result_digits = [0] * width
    borrowed_from = [False] * width
    for i in range(width - 1, -1, -1):
        top = int(s1[i]) - borrow
        bottom = int(s2[i])
        if top < bottom:
            top += 10
            borrow = 1
            if i > 0:
                borrowed_from[i - 1] = True
        else:
            borrow = 0
        result_digits[i] = top - bottom

    return s1, s2, result_digits, borrowed_from, width


def render(nombre1: int, nombre2: int) -> Image.Image:
    s1, s2, result_digits, borrowed_from, width = compute_columns(nombre1, nombre2)
    result_str = "".join(str(d) for d in result_digits).lstrip("0") or "0"

    font = get_font(FONT_SIZE)
    font_small = get_font(FONT_SIZE_SMALL)

    margin = 40
    img_width = margin * 2 + width * COL_W
    img_height = 400

    content = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)

    col_centers = [margin + i * COL_W + COL_W / 2 for i in range(width)]
    borrow_y, line1_y, line2_y, bar_y, result_y = 20, 70, 150, 230, 250

    for i in range(width):
        if borrowed_from[i]:
            reduced = int(s1[i]) - 1
            draw_col_text(draw, col_centers[i] + 14, borrow_y, str(reduced), font_small, STEP_RED)

    for i, ch in enumerate(s1):
        draw_col_text(draw, col_centers[i], line1_y, ch, font, INK)

    draw.text((margin - 30, line2_y), "-", font=font, fill=INK)
    for i, ch in enumerate(s2):
        draw_col_text(draw, col_centers[i], line2_y, ch, font, INK)

    bar_left, bar_right = margin - 20, margin + width * COL_W - 10
    draw.line([(bar_left, bar_y), (bar_right, bar_y)], fill=NAVY, width=5)

    result_start_col = width - len(result_str)
    for i, ch in enumerate(result_str):
        draw_col_text(draw, col_centers[result_start_col + i], result_y, ch, font, GREEN_RESULT)

    return content
