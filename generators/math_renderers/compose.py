"""Composition générique fond cahier + contenu render_type (ADDENDUM v2.6 §5-6-8).

Réutilisé par tous les render_type (division_posee, soustraction_colonnes,
addition_colonnes, multiplication_posee, astuce_chaine) : chaque renderer
ne dessine que son contenu (fond transparent), compose_illustration() colle
ce contenu sur le fond cahier avec le style magazine-clip existant.
"""

import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import ASSETS_DIR
from generators.math_renderers.cahier_background import CANVAS, make_cahier_background

FONT_PATH = ASSETS_DIR / "fonts" / "PatrickHand-Regular.ttf"

NAVY = (26, 43, 92)            # bleu marine Curio #1a2b5c
INK = (25, 25, 30)
STEP_RED = (176, 40, 40)
GREEN_RESULT = (0, 120, 70)

# Zone occupée par le contenu : ~65% de la hauteur, espace vide 30% en bas
# (même règle que les illustrations GPT Image 2, CLAUDE.md §5)
MAX_WIDTH_RATIO = 0.80
MAX_HEIGHT_RATIO = 0.55
TOP_MARGIN_RATIO = 0.16
MAX_UPSCALE = 2.0  # les renderers dessinent à taille modeste ; on remplit la zone cible


def get_font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def draw_col_text(draw, col_center_x, y, text, font, fill):
    """Dessine `text` centré horizontalement sur col_center_x.

    Patrick Hand n'est pas une police à chasse fixe (chaque chiffre a une
    largeur différente) : les renderers en colonnes (division, addition,
    soustraction, multiplication) doivent centrer chaque nombre dans sa
    colonne plutôt que le dessiner à un x fixe, sous peine de désalignement.
    """
    width = font.getlength(text)
    draw.text((col_center_x - width / 2, y), text, font=font, fill=fill)


def compose_illustration(content_img: Image.Image, output_path: str, rotation_deg: float = None):
    """Compose le contenu (RGBA, fond transparent) sur le fond cahier Curio.

    rotation_deg : None = tirage aléatoire -2°/+2° ("collé à la main").
    """
    if rotation_deg is None:
        rotation_deg = random.uniform(-2.0, 2.0)

    bg = make_cahier_background().convert("RGBA")

    content_rot = content_img.rotate(rotation_deg, expand=True, resample=Image.BICUBIC)

    max_w = int(CANVAS[0] * MAX_WIDTH_RATIO)
    max_h = int(CANVAS[1] * MAX_HEIGHT_RATIO)
    scale = min(max_w / content_rot.width, max_h / content_rot.height, MAX_UPSCALE)
    if abs(scale - 1.0) > 0.01:
        new_size = (int(content_rot.width * scale), int(content_rot.height * scale))
        content_rot = content_rot.resize(new_size, Image.LANCZOS)

    # Bordure blanche + ombre portée (style coupure de magazine)
    border = 22
    framed = Image.new("RGBA", (content_rot.width + border * 2, content_rot.height + border * 2), (255, 255, 255, 255))
    framed.paste(content_rot, (border, border), content_rot)

    shadow = Image.new("RGBA", framed.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([8, 12, framed.width, framed.height], fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    pos_x = (CANVAS[0] - framed.width) // 2
    pos_y = int(CANVAS[1] * TOP_MARGIN_RATIO)

    bg.alpha_composite(shadow, (pos_x, pos_y))
    bg.alpha_composite(framed, (pos_x, pos_y))

    bg.convert("RGB").save(output_path, quality=95)
    return output_path
