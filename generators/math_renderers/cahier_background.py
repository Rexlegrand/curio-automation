"""Fond cahier Seyès partagé par tous les renderers maths (ADDENDUM v2.6 §5)."""

from PIL import Image, ImageDraw

from config import IMAGE_SIZE

_w, _h = IMAGE_SIZE.split("x")
CANVAS = (int(_w), int(_h))

GRID_COLOR = (198, 216, 240)   # bleu clair Seyès
PAPER_COLOR = (253, 253, 250)
MARGIN_COLOR = (230, 140, 140)  # marge rouge verticale (cahier français classique)
GRID_STEP = 34
MARGIN_X = 80


def make_cahier_background():
    """Fond cahier Seyès : quadrillage bleu clair sur papier blanc cassé, marge rouge."""
    img = Image.new("RGB", CANVAS, PAPER_COLOR)
    draw = ImageDraw.Draw(img)
    for x in range(0, CANVAS[0], GRID_STEP):
        draw.line([(x, 0), (x, CANVAS[1])], fill=GRID_COLOR, width=1)
    for y in range(0, CANVAS[1], GRID_STEP):
        draw.line([(0, y), (CANVAS[0], y)], fill=GRID_COLOR, width=1)
    draw.line([(MARGIN_X, 0), (MARGIN_X, CANVAS[1])], fill=MARGIN_COLOR, width=2)
    return img
