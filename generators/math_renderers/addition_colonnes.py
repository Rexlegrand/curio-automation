"""Addition posée en colonnes (méthode française), retenues visibles.

Une opération n'a qu'un seul résultat : render() accepte un paramètre `stage`
(1/2/3) pour révéler l'opération progressivement sur 3 illustrations plutôt
que de répéter 3 fois la même image : stage 1 = opérandes posés, stage 2 =
+ retenues, stage 3 = + résultat (comportement complet).
"""

from PIL import Image, ImageDraw

from generators.math_renderers.compose import GREEN_RESULT, INK, NAVY, STEP_RED, draw_col_text, get_font

COL_W = 56
FONT_SIZE = 60
FONT_SIZE_SMALL = 34


def compute_columns(nombre1: int, nombre2: int):
    """Retenues + résultat colonne par colonne, de la droite vers la gauche.

    Retourne (s1, s2, digits_resultat, retenue_finale, largeur).
    """
    s1, s2 = str(nombre1), str(nombre2)
    width = max(len(s1), len(s2))
    s1, s2 = s1.rjust(width, "0"), s2.rjust(width, "0")

    carry = 0
    result_digits = [0] * width
    for i in range(width - 1, -1, -1):
        total = int(s1[i]) + int(s2[i]) + carry
        result_digits[i] = total % 10
        carry = total // 10

    return s1, s2, result_digits, carry, width


def render(nombre1: int, nombre2: int, stage: int = 3) -> Image.Image:
    s1, s2, result_digits, final_carry, width = compute_columns(nombre1, nombre2)
    result_str = (str(final_carry) if final_carry else "") + "".join(str(d) for d in result_digits)

    font = get_font(FONT_SIZE)
    font_small = get_font(FONT_SIZE_SMALL)

    margin = 40
    img_width = margin * 2 + (width + 1) * COL_W
    img_height = 400

    content = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)

    col_centers = [margin + COL_W + i * COL_W for i in range(width)]
    carry_y, line1_y, line2_y, bar_y, result_y = 20, 70, 150, 230, 250

    for i, ch in enumerate(s1):
        draw_col_text(draw, col_centers[i], line1_y, ch, font, INK)

    draw.text((margin - 10, line2_y), "+", font=font, fill=INK)
    for i, ch in enumerate(s2):
        draw_col_text(draw, col_centers[i], line2_y, ch, font, INK)

    bar_left = margin - 20
    bar_right = margin + (width + 1) * COL_W - 20
    draw.line([(bar_left, bar_y), (bar_right, bar_y)], fill=NAVY, width=5)

    if stage >= 2:
        # Retenues : rejoue la boucle colonne par colonne pour positionner chaque
        # petit chiffre rouge au-dessus de la colonne à gauche où il s'ajoute.
        carry = 0
        for i in range(width - 1, -1, -1):
            total = int(s1[i]) + int(s2[i]) + carry
            carry = total // 10
            if carry and i > 0:
                draw_col_text(draw, col_centers[i - 1], carry_y, str(carry), font_small, STEP_RED)

    if stage >= 3:
        result_cols = col_centers if not final_carry else [col_centers[0] - COL_W] + col_centers
        for i, ch in enumerate(result_str):
            draw_col_text(draw, result_cols[i], result_y, ch, font, GREEN_RESULT)

    return content
