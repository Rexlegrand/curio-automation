"""Prépare les assets d'un reel de série pour Remotion.

    python prep_assets.py mariannes

Généralisation de `prep_sahara_assets.py`, réduite à ce qui sert dans tous les
reels :

  1. les plans passent en JPEG à l'échelle du canvas 1080×1920. GPT Image 2
     rend en 1024×1792 ou 1024×1536 : agrandis à la volée par le navigateur à
     chaque image de chaque rendu, ils coûtent plus cher que de les mettre à
     l'échelle une fois pour toutes ;
  2. le hook Dreamina et les deux clips de Curio sont copiés à côté. Le clip
     CTA et le clip studio sont des assets FIXES, communs à tous les reels :
     ils ne contiennent aucun élément du sujet, seulement Curio au micro.

Ce que ce script ne fait PAS, à la différence du sahara : aucun détourage,
aucun recalage de ligne de sol. Ces traitements existaient pour des plans
précis (le camion instancié en 3D, les deux coupes de sol) ; un reel qui en a
besoin les ajoute dans son propre script.
"""

import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from reels import charger

REPO = Path(__file__).parent.resolve()
CANVAS_W, CANVAS_H = 1080, 1920

# Détourage. Repris de `prep_sahara_assets.py`, où il servait au camion :
# remplissage par diffusion depuis les quatre coins, puis érosion du masque.
# Le fond doit être BLANC et non noir — sur le camion, le noir du châssis
# touchait le fond noir et partait au détourage avec lui.
MAGENTA = (255, 0, 255)
SEUIL_FOND = 40
EROSION = 5

# Clips de Curio, identiques pour tous les reels de la série.
CLIPS = {
    "curio_studio.mp4": REPO / "assets/sahara_amazonie/curio_studio.mp4",
    "curio_cta.mp4": REPO / "assets/clips/curio_cta.mp4",
}


def masque_fond(im: Image.Image, seuil: int) -> Image.Image:
    """Masque du fond, par diffusion depuis les quatre coins."""
    sonde = im.copy()
    for coin in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
        ImageDraw.floodfill(sonde, coin, MAGENTA, thresh=seuil)
    r, g, b = sonde.split()
    touche = ImageChops.logical_and(
        ImageChops.logical_and(
            r.point(lambda v: 255 if v == 255 else 0).convert("1"),
            g.point(lambda v: 255 if v == 0 else 0).convert("1"),
        ),
        b.point(lambda v: 255 if v == 255 else 0).convert("1"),
    )
    return touche.convert("L")


def detourer(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    alpha = masque_fond(im, SEUIL_FOND).point(lambda v: 0 if v else 255)
    # Érosion : sans elle il reste un liseré du fond autour de l'objet, très
    # visible quand il est instancié des centaines de fois.
    alpha = alpha.filter(ImageFilter.MinFilter(EROSION))
    im = im.convert("RGBA")
    im.putalpha(alpha)
    boite = alpha.point(lambda v: 255 if v > 200 else 0).getbbox()
    if boite:
        im = im.crop(boite)
    im.save(dst)
    print(f"  {dst.name:22s} détouré {im.width}×{im.height}")


def mise_a_echelle(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    # Les plans verticaux remplissent le canvas ; les matières horizontales
    # (un objet isolé sur noir, une couche de particules) sont recadrées par le
    # composant qui les monte, on se contente de les élargir à la largeur du
    # canvas.
    if im.height >= im.width:
        ratio = max(CANVAS_W / im.width, CANVAS_H / im.height)
    else:
        ratio = CANVAS_W / im.width
    taille = (round(im.width * ratio), round(im.height * ratio))
    im = im.resize(taille, Image.LANCZOS)
    im.save(dst, quality=92, optimize=True)
    print(f"  {dst.name:22s} {taille[0]}×{taille[1]}")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug>")
    reel = charger(sys.argv[1])
    src = REPO / f"assets/{reel.slug}"
    out = REPO / f"remotion/public/reels/{reel.slug}"
    out.mkdir(parents=True, exist_ok=True)

    print(f"{reel.titre} — plans")
    for nom in reel.images:
        fichier = src / f"{nom}.png"
        cible = out / (f"{nom}.png" if nom in reel.decoupe else f"{nom}.jpg")
        if not fichier.exists():
            # Sur un clone neuf, les sources brutes de GPT Image 2 sont absentes
            # (58 Mo pour trois reels, non versionnées) mais les plans dérivés
            # sont là, eux, et suffisent à rendre le reel. On passe donc au lieu
            # de s'arrêter — c'est ce qui permet de relancer ce script juste
            # pour remettre les clips de Curio en place.
            if cible.exists():
                print(f"  {cible.name:22s} déjà là, source absente")
                continue
            sys.exit(f"plan manquant : {fichier} (lancer gen_images.py)")
        if nom in reel.decoupe:
            detourer(fichier, out / f"{nom}.png")
        else:
            mise_a_echelle(fichier, out / f"{nom}.jpg")

    print("clips")
    hook = src / "hook_video.mp4"
    if hook.exists():
        shutil.copyfile(hook, out / "hook_video.mp4")
        print(f"  {'hook_video.mp4':22s} {hook.stat().st_size // 1024} Ko")
    else:
        print(f"  hook_video.mp4         ABSENT — à déposer dans {src}")
    for nom, chemin in CLIPS.items():
        shutil.copyfile(chemin, out / nom)
        print(f"  {nom:22s} {chemin.stat().st_size // 1024} Ko")

    print(f"\n✅ {out}")


if __name__ == "__main__":
    main()
