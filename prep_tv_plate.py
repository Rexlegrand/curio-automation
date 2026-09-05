"""Prépare les assets « téléviseur d'époque » pour la reconstruction craftedbycm-01.

Sources : `assets/craftedbycm/tv_source_*.png`, cinq postes générés par Benjamin
hors pipeline (abonnement personnel) — poste de face, cadré serré sur fond noir,
écran éteint rempli d'un gris uni. Le short d'origine change de poste à chaque
phrase : c'est le propos même de la vidéo, et ça donne ici un moteur de variation
qui ne coûte rien au montage.

Trois consignes de génération font tout le travail en amont, et le script en
dépend : poste STRICTEMENT de face (aucune perspective à corriger), écran d'un
GRIS UNI (c'est ce qui permet de le détecter), fond NOIR PUR (c'est ce qui
permet de détourer). Un poste de trois quarts ou un écran avec reflet casse les
deux détections.

Pour chaque source, cinq opérations, toutes locales :

  1. détourage du fond noir, par remplissage depuis les quatre coins ;
  2. recadrage sur le boîtier, pour que les contraintes de taille portent sur
     le poste et non sur d'éventuelles marges vides de la source ;
  3. détection de la vitre, par remplissage depuis le centre du boîtier — le
     gris de l'écran est uniforme, sa région se referme d'elle-même ;
  4. perçage de cette vitre à la forme exacte de la région détectée. Un
     rectangle à coins arrondis ne convient pas : un tube cathodique est bombé,
     ses bords ne sont pas droits, et le rayon qu'on en déduit est toujours
     surestimé — il restait un croissant gris dans chaque coin ;
  5. mise en place sur un cadre 9:16, vitre centrée, débordement latéral du
     boîtier admis comme dans le short d'origine.

Le fond noir de studio n'est PAS peint ici : il est peint côté Remotion, ce qui
permet d'en changer sans refaire les assets.

Le perçage épousant la forme du tube, la composition Remotion n'a pas à
reproduire ce contour : elle pose son image dans le rectangle plein donné par
`screenRect` et laisse le boîtier, opaque et posé par-dessus, découper le reste.

Sortie : un tv_plate_<nom>.png par poste et un tv_plates.json commun, qui donne
pour chacun la position exacte de sa vitre dans le cadre final.
"""

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REPO = Path(__file__).parent.resolve()
ASSETS = REPO / "assets/craftedbycm"
OUT_JSON = ASSETS / "tv_plates.json"

CANVAS_W, CANVAS_H = 1080, 1920

# Largeur de vitre visée. Dans le short, la vitre occupe presque toute la
# largeur du cadre et le poste déborde de part et d'autre.
TARGET_SCREEN_W = 940
# Plafond d'agrandissement : au-delà, le boîtier commence à baver. Il ne mord
# que sur le poste officiel, la seule source rendue en 941 px de large ; les
# quatre autres, cadrés serré, restent tous sous 1,1.
MAX_UPSCALE = 1.2
# Hauteur maximale du poste. Le texte vit AU-DESSUS et EN DESSOUS du poste : un
# poste qui remplit la hauteur ne lui laisse plus de place. Dans le short, le
# poste occupe un peu plus de la moitié de la hauteur du cadre.
MAX_TV_H = 1180

MAGENTA = (255, 0, 255)
BG_THRESH = 26  # tolérance du remplissage de fond, sur du noir pur
SCREEN_THRESH = 16  # tolérance du remplissage d'écran, sur un gris uni
SCREEN_BLEED = 5  # MaxFilter : dilate le perçage de 2 px, mange le liseré de bord
ALPHA_ERODE = 5  # MinFilter : mange le liseré de compression du détourage


def region_mask(im: Image.Image, seeds, thresh: int) -> Image.Image:
    """Masque blanc des zones atteintes depuis `seeds` par remplissage."""
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


def prepare(source: Path) -> dict:
    name = source.stem.replace("tv_source_", "")
    im = Image.open(source).convert("RGB")
    W, H = im.size

    # 1 — détourage. Le fond est noir pur et continu : il se remplit depuis les
    # quatre coins sans jamais franchir le boîtier, y compris sur le poste noir
    # mat dont le corps reste nettement plus clair que le fond.
    corners = [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]
    background = region_mask(im, corners, BG_THRESH)
    alpha = background.point(lambda v: 0 if v else 255)
    alpha = alpha.filter(ImageFilter.MinFilter(ALPHA_ERODE))

    # 2 — recadrage sur le poste. Sans lui, une source qui laisse du vide
    # au-dessus et en dessous (c'est le cas du poste officiel, cadré en 9:16)
    # verrait le plafond de hauteur s'appliquer à ce vide plutôt qu'au boîtier,
    # et sortirait un poste deux fois trop petit.
    crop = alpha.point(lambda v: 255 if v > 200 else 0).getbbox()
    if crop is None:
        raise SystemExit(f"{name} : aucun contenu opaque")
    im = im.crop(crop)
    alpha = alpha.crop(crop)
    W, H = im.size

    # 3 — détection de la vitre depuis le centre du boîtier. Sur les cinq
    # postes, ce centre tombe dans l'écran.
    screen = region_mask(im, [(W // 2, H // 2)], SCREEN_THRESH)
    box = screen.getbbox()
    if box is None:
        raise SystemExit(f"{name} : vitre introuvable — écran non uni ?")

    # 4 — perçage à la forme exacte du tube, légèrement dilatée pour manger le
    # dernier liseré du bord, et adoucie pour éviter l'escalier d'aliasing.
    hole = screen.filter(ImageFilter.MaxFilter(SCREEN_BLEED))
    hole = hole.filter(ImageFilter.GaussianBlur(1.2))
    alpha = Image.composite(Image.new("L", im.size, 0), alpha, hole)

    im.putalpha(alpha)

    # 5 — mise à l'échelle et mise en place. C'est la VITRE qu'on centre
    # horizontalement, pas le boîtier : l'écran est décalé à gauche sur la
    # plupart des postes (le haut-parleur occupe la droite), et centrer le
    # boîtier ferait sortir un bord du tube hors du cadre. Le boîtier, lui,
    # déborde librement — c'est exactement ce que fait le short.
    screen_w = box[2] - box[0]
    screen_h = box[3] - box[1]
    scale = min(TARGET_SCREEN_W / screen_w, MAX_UPSCALE, MAX_TV_H / H)
    tv_w, tv_h = round(W * scale), round(H * scale)
    im = im.resize((tv_w, tv_h), Image.LANCZOS)

    tv_x = round(CANVAS_W / 2 - (box[0] + screen_w / 2) * scale)
    # Verticalement, c'est le boîtier qu'on centre : les deux bandes de noir
    # ainsi laissées en haut et en bas sont la place du texte.
    tv_y = (CANVAS_H - tv_h) // 2

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(im, (tv_x, tv_y), im)
    out_png = ASSETS / f"tv_plate_{name}.png"
    canvas.save(out_png)

    meta = {
        "screenRect": {
            "x": round(tv_x + box[0] * scale),
            "y": round(tv_y + box[1] * scale),
            "width": round(screen_w * scale),
            "height": round(screen_h * scale),
        },
        "tvRect": {"x": tv_x, "y": tv_y, "width": tv_w, "height": tv_h},
        "plate": out_png.name,
        "source": source.name,
    }
    r = meta["screenRect"]
    print(
        f"{name:9s} poste {tv_w}×{tv_h} à ({tv_x}, {tv_y})  "
        f"vitre {r['width']}×{r['height']} à ({r['x']}, {r['y']})"
    )
    return name, meta


def main() -> None:
    sources = sorted(ASSETS.glob("tv_source_*.png"))
    if not sources:
        raise SystemExit(f"aucune source dans {ASSETS}")
    plates = dict(prepare(s) for s in sources)
    OUT_JSON.write_text(
        json.dumps(
            {"canvasWidth": CANVAS_W, "canvasHeight": CANVAS_H, "plates": plates},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n{OUT_JSON}")


if __name__ == "__main__":
    main()
