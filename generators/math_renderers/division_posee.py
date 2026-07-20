"""Division posée "en potence" (méthode française) — rendu déterministe.

Généralisé depuis le prototype division_potence.py : diviseur à 1 ou 2
chiffres (CE2 à CM2), alignement en colonnes centré (police non monospace).
"""

from PIL import Image, ImageDraw

from generators.math_renderers.compose import GREEN_RESULT, INK, NAVY, STEP_RED, draw_col_text, get_font

COL_W = 52
FONT_SIZE = 60
FONT_SIZE_SMALL = 42


def compute_steps(dividende: int, diviseur: int):
    """Calcule chaque étape de la division en potence, chiffre par chiffre."""
    dividende_str = str(dividende)
    steps = []
    quotient_digits = []
    remainder = 0

    for i, digit_char in enumerate(dividende_str):
        current_number = int(str(remainder) + digit_char) if i > 0 else int(digit_char)
        q_digit = current_number // diviseur
        product = q_digit * diviseur
        new_remainder = current_number - product

        if quotient_digits or q_digit != 0:
            quotient_digits.append(str(q_digit))

        steps.append({
            "current_number": current_number,
            "quotient_digit": q_digit,
            "product": product,
            "remainder": new_remainder,
        })
        remainder = new_remainder

    if not quotient_digits:
        quotient_digits = ["0"]

    return steps, "".join(quotient_digits), remainder


def render(dividende: int, diviseur: int) -> Image.Image:
    """Rend le contenu de la division (fond transparent RGBA)."""
    steps, quotient, remainder = compute_steps(dividende, diviseur)
    dividende_str = str(dividende)

    font = get_font(FONT_SIZE)
    font_small = get_font(FONT_SIZE_SMALL)

    potence_w = 240
    width = 60 + len(dividende_str) * COL_W + potence_w + 40
    height = 90 + len(steps) * 130 + 140

    content = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(content)

    start_x, start_y = 40, 30
    col_centers = [start_x + i * COL_W + COL_W / 2 for i in range(len(dividende_str))]

    for i, ch in enumerate(dividende_str):
        draw_col_text(draw, col_centers[i], start_y, ch, font, INK)

    bar_x = start_x + len(dividende_str) * COL_W + 15
    draw.line([(bar_x, start_y - 15), (bar_x, start_y + 380)], fill=NAVY, width=5)
    draw.line([(bar_x, start_y + 70), (bar_x + potence_w - 30, start_y + 70)], fill=NAVY, width=5)

    diviseur_x = bar_x + (potence_w - 30) / 2
    draw_col_text(draw, diviseur_x, start_y, str(diviseur), font, INK)
    draw_col_text(draw, diviseur_x, start_y + 90, quotient, font, GREEN_RESULT)

    y = start_y + 90
    for i, step in enumerate(steps):
        col = col_centers[i]
        draw_col_text(draw, col - 25, y, f"-{step['product']}", font_small, STEP_RED)
        y += 55
        draw.line([(col - 60, y), (col + 25, y)], fill=STEP_RED, width=3)
        y += 12
        draw_col_text(draw, col, y, str(step["remainder"]), font_small, INK)
        y += 70

    result_text = f"{dividende} ÷ {diviseur} = {quotient}"
    if remainder:
        result_text += f" reste {remainder}"
    draw.text((start_x, y + 30), result_text, font=font_small, fill=NAVY)

    return content
