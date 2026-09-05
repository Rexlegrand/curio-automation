"""Prépare les assets dérivés du reel « le Sahara nourrit l'Amazonie ».

Les sources vivent dans `assets/sahara_amazonie/` (générées par Benjamin hors
pipeline, plus trois images en domaine public — voir SOURCES.md). Ce script
produit ce que Remotion consomme, dans `remotion/public/sahara/` :

  1. le camion détouré en PNG alpha, seul asset qui doit vraiment l'être :
     il est instancié des centaines de fois en 3D au beat 4 ;
  2. les deux coupes de sol rognées à leur ligne de sol et ramenées à la même
     hauteur. Générées séparément, leur surface ne tombe pas au même endroit
     (13 % contre 20 %) : empilées telles quelles, la seconde ouvrait sur une
     large bande noire et le passage de l'une à l'autre faisait sauter
     l'image ;
  3. les plans plein cadre et les matières, simplement copiés et remis à
     l'échelle du canvas 1080×1920.

Le globe a sa propre texture (`earth_4096.jpg`, réduite du Blue Marble du
repo) : elle est produite ici aussi pour que tout parte d'un seul script.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REPO = Path(__file__).parent.resolve()
SRC = REPO / "assets/sahara_amazonie"
OUT = REPO / "remotion/public/sahara"

CANVAS_W, CANVAS_H = 1080, 1920

MAGENTA = (255, 0, 255)
# Le camion est sur fond blanc : le noir de son châssis touchait le fond noir
# de la première version et partait au détourage avec lui.
TRUCK_THRESH = 40
ALPHA_ERODE = 5

WORLD_SOURCE = REPO / "remotion/public/desert-sel/map_texture_world.jpg"
GLOBE_TEXTURE_SIZE = (4096, 2048)


def region_mask(im: Image.Image, seeds, thresh: int) -> Image.Image:
    probe = im.copy()
    for seed in seeds:
        ImageDraw.floodfill(probe, seed, MAGENTA, thresh=thresh)
    r, g, b = probe.split()
    hit = ImageChops.logical_and(
        ImageChops.logical_and(
            r.point(lambda v: 255 if v == 255 else 0).convert("1"),
            g.point(lambda v: 255 if v == 0 else 0).convert("1"),
        ),
        b.point(lambda v: 255 if v == 255 else 0).convert("1"),
    )
    return hit.convert("L")


def soil_line(im: Image.Image) -> int:
    """Hauteur de la ligne de sol : première ligne qui sort du noir."""
    grey = im.convert("L")
    for y in range(grey.height):
        row = [grey.getpixel((x, y)) for x in range(0, grey.width, 8)]
        if sum(row) / len(row) > 28:
            return y
    return 0


def cutout_truck() -> None:
    im = Image.open(SRC / "camion.png").convert("RGB")
    w, h = im.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    background = region_mask(im, corners, TRUCK_THRESH)
    alpha = background.point(lambda v: 0 if v else 255)
    alpha = alpha.filter(ImageFilter.MinFilter(ALPHA_ERODE))
    im = im.convert("RGBA")
    im.putalpha(alpha)
    box = alpha.point(lambda v: 255 if v > 200 else 0).getbbox()
    im = im.crop(box)
    im.save(OUT / "camion.png")
    print(f"camion     détouré {im.width}×{im.height}")


def align_soils() -> None:
    """Les deux coupes doivent commencer exactement à leur surface.

    Chacune arrive avec du vide noir au-dessus du sol, et pas la même hauteur
    de vide : 137 px pour la riche, 209 px pour la pauvre. Empilées telles
    quelles dans deux fenêtres, la seconde ouvrait sur une bande noire de plus
    de cent pixels. On rogne donc chaque image à SA ligne de sol, puis à la
    hauteur commune la plus courte — après quoi les deux sont interchangeables
    dans n'importe quel cadre.
    """
    riche = Image.open(SRC / "sol_riche.png").convert("RGB")
    pauvre = Image.open(SRC / "sol_pauvre.png").convert("RGB")
    y_riche, y_pauvre = soil_line(riche), soil_line(pauvre)
    print(f"sols       ligne de sol {y_riche} et {y_pauvre} — rognées à la surface")

    riche = riche.crop((0, y_riche, riche.width, riche.height))
    pauvre = pauvre.crop((0, y_pauvre, pauvre.width, pauvre.height))
    hauteur = min(riche.height, pauvre.height)
    riche = riche.crop((0, 0, riche.width, hauteur))
    pauvre = pauvre.crop((0, 0, pauvre.width, hauteur))
    print(f"           hauteur commune {hauteur} px")

    # En JPEG comme les autres photos : seul le camion a besoin d'un canal
    # alpha, et c'est le seul PNG du dossier.
    riche.save(OUT / "sol_riche.jpg", quality=94)
    pauvre.save(OUT / "sol_pauvre.jpg", quality=94)


def copy_plain() -> None:
    for name in ("dune", "canopee", "lac_asseche", "poussiere", "sable_macro"):
        im = Image.open(SRC / f"{name}.png").convert("RGB")
        im.save(OUT / f"{name}.jpg", quality=94)
        print(f"{name:10s} {im.width}×{im.height}")
    for name, src in (
        ("bodele", "bodele_tempete_nasa.jpg"),
        ("diatomees", "diatomees_noaa.jpg"),
    ):
        im = Image.open(SRC / "sources_libres" / src).convert("RGB")
        im.save(OUT / f"{name}.jpg", quality=94)
        print(f"{name:10s} {im.width}×{im.height}")


def globe_texture() -> None:
    # 8192×4096 = 128 Mo de VRAM non compressée : le rasteriseur logiciel du
    # rendu headless la refuse sans erreur, le globe sort noir.
    im = Image.open(WORLD_SOURCE).resize(GLOBE_TEXTURE_SIZE, Image.LANCZOS)
    im.save(OUT / "earth_4096.jpg", quality=92)
    print(f"globe      {im.width}×{im.height}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cutout_truck()
    align_soils()
    copy_plain()
    globe_texture()
    print(f"\n{OUT}")


if __name__ == "__main__":
    main()
