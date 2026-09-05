"""Échantillon de transitions pour le format « deux carrés » (manchot empereur).

Le montage actuel (test_deux_carres_manchot.py) enchaîne les 10 blocs du corps
en cut sec : le passage plein écran ↔ deux carrés est brutal. Le rythme (une
coupe toutes les 2,92s) est bon pour la rétention et ne change pas ; seul le
RACCORD est adouci.

Ce script ne rend PAS le reel entier : il rend un seul enchaînement
    plein écran (illus_1) → deux carrés (illus_1) → plein écran (illus_2)
en 3 styles de transition, pour choisir avant de relancer le montage complet.

Contrainte : la durée totale du reel reste verrouillée sur l'audio (37,4s). Une
transition ne s'ajoute donc jamais au montage — elle consomme les TD premières
secondes du bloc qui arrive. Le bloc entrant vaut TD de transition + le reste en
plan fixe, jamais BLOCK_D + TD.

Styles rendus :
    slide      — les deux cartes glissent (haut/bas), ease-out cubique, et le
                 fond plein écran se fond vers le fond sombre pendant TD.
    overshoot  — même chose avec un léger dépassement/rebond en fin de course
                 (ease-out back), plus vivant, plus « motion design ».
    crossfade  — fondu croisé court entre les deux plans. Le plus doux, le
                 moins dessiné : sert de point de comparaison bas.

Rien n'est écrit dans output/ : les rendus partent dans testing_remotion/.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from config import VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH  # noqa: E402

REPO = Path(__file__).parent.resolve()
REEL_DIR = REPO / "output/2026-08-20/le_manchot_empereur_qui_jeune_deux_mois_pour_son_uf"
CURIO_TALK = Path.home() / "Downloads/dreamina-2026-08-30-1373-Animate this exact image. Keep the chara....mp4"
OUT_DIR = REPO / "testing_remotion" / "deux_carres_transitions"

# ---- Timeline de l'échantillon (mêmes constantes que le montage complet) ----
BLOCK_D = 2.9208          # (37.400 - 2*4.096) / 10
TD = 0.38                 # durée d'une transition, prise SUR le bloc entrant
CURIO_OFFSET = 2.4        # même fenêtre que le bloc deux-carrés n°3 du montage
AUDIO_START = 4.096       # début du corps dans audio_v2.mp3
SAMPLE_D = 3 * BLOCK_D    # ≈ 8,76s

# ---- Géométrie des cartes (identique à test_deux_carres_manchot.py) ----
CARD_W, CARD_H, CARD_R = 940, 855, 36
CARD_X = (VIDEO_WIDTH - CARD_W) // 2  # 70
TOP_Y = 80
GAP = 50
BOT_Y = TOP_Y + CARD_H + GAP  # 985
BG_COLOR = "0x0E1013"

# Cadrages « cover » figés (mesurés dans le montage validé) : Curio garde
# l'enseigne néon entière, l'illustration est cadrée au-dessus de son centre.
CURIO_FOCUS = 0.4345
ILLUS_FOCUS = 0.42


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r


def make_card_mask(path):
    img = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], radius=CARD_R, fill=255)
    img.save(path)


def cover(src_w, src_h, dst_w, dst_h, focus=0.5):
    if src_w / src_h > dst_w / dst_h:
        h = src_h
        w = round(src_h * dst_w / dst_h)
        x, y = (src_w - w) // 2, 0
    else:
        w = src_w
        h = round(src_w * dst_h / dst_w)
        x = 0
        y = max(0, min(src_h - h, round(src_h * focus - h / 2)))
    return w, h, x, y


# ---- Courbes d'accélération, en expressions ffmpeg sur t ----------------------
# Chaque courbe renvoie p ∈ [0,1] : 0 = cartes hors cadre, 1 = cartes en place.

def p_in_cubic():
    """Ease-out cubique : départ rapide, arrivée douce. Pas de dépassement."""
    return f"(1-pow(1-min(t/{TD},1),3))"


def p_in_back():
    """Ease-out back : dépasse la position finale puis revient (petit rebond)."""
    x = f"min(t/{TD},1)"
    return f"(1+2.70158*pow({x}-1,3)+1.70158*pow({x}-1,2))"


def p_out_cubic():
    """Sortie miroir : les cartes tiennent puis s'échappent vite (ease-in)."""
    return f"(1-pow(min(t/{TD},1),3))"


def card_positions(p):
    """y des deux cartes en fonction de p (hors cadre en 0, en place en 1)."""
    top_y = f"{TOP_Y}-(1-{p})*{TOP_Y + CARD_H}"
    bot_y = f"{BOT_Y}+(1-{p})*{VIDEO_HEIGHT - BOT_Y}"
    return top_y, bot_y


# ---- Briques vidéo -----------------------------------------------------------

def block_fullscreen(illus, dur, out):
    w, h, x, y = cover(1024, 1792, VIDEO_WIDTH, VIDEO_HEIGHT, focus=0.5)
    run([
        "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.4f}", "-i", str(illus),
        "-vf", f"crop={w}:{h}:{x}:{y},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def _card_chains():
    """Chaînes de filtres communes : carte Curio [cua] et carte illustration [ila]."""
    cw, ch, cx, cy = cover(720, 1280, CARD_W, CARD_H, focus=CURIO_FOCUS)
    iw, ih, ix, iy = cover(1024, 1792, CARD_W, CARD_H, focus=ILLUS_FOCUS)
    return (
        f"[0:v]crop={cw}:{ch}:{cx}:{cy},scale={CARD_W}:{CARD_H},fps={VIDEO_FPS},format=rgba[cu];"
        f"[2:v]format=gray[mk];[cu][mk]alphamerge[cua];"
        f"[1:v]crop={iw}:{ih}:{ix}:{iy},scale={CARD_W}:{CARD_H},format=rgba[il];"
        f"[2:v]format=gray[mk2];[il][mk2]alphamerge[ila];"
    )


def block_split(illus, curio_offset, dur, mask, out):
    """Plan fixe deux carrés (aucune animation)."""
    filt = (
        f"color=c={BG_COLOR}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r={VIDEO_FPS}:d={dur:.4f}[bg];"
        + _card_chains()
        + f"[bg][cua]overlay={CARD_X}:{TOP_Y}[s1];"
        f"[s1][ila]overlay={CARD_X}:{BOT_Y},format=yuv420p[v]"
    )
    run([
        "ffmpeg", "-y",
        "-ss", f"{curio_offset:.3f}", "-t", f"{dur:.4f}", "-i", str(CURIO_TALK),
        "-loop", "1", "-t", f"{dur:.4f}", "-i", str(illus),
        "-loop", "1", "-t", f"{dur:.4f}", "-i", str(mask),
        "-filter_complex", filt, "-map", "[v]", "-t", f"{dur:.4f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def transition_slide(illus_bg, illus_card, curio_offset, mask, out, curve, entering):
    """Les deux cartes glissent sur le plan plein écran (ou en sortent).

    entering=True  : plein écran → deux carrés (le fond s'assombrit).
    entering=False : deux carrés → plein écran (le fond se dévoile).
    illus_bg   = illustration du plan PLEIN ÉCRAN concerné par la transition.
    illus_card = illustration affichée DANS la carte du bas (celle du bloc
                 deux carrés), qui n'est pas forcément la même.
    """
    bw, bh, bx, by = cover(1024, 1792, VIDEO_WIDTH, VIDEO_HEIGHT, focus=0.5)
    p = curve()
    top_y, bot_y = card_positions(p)
    fade = f"fade=t=in:st=0:d={TD}:alpha=1" if entering else f"fade=t=out:st=0:d={TD}:alpha=1"

    filt = (
        f"[3:v]crop={bw}:{bh}:{bx}:{by},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS}[full];"
        f"color=c={BG_COLOR}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r={VIDEO_FPS}:d={TD}[dark0];"
        f"[dark0]format=rgba,{fade}[dark];"
        f"[full][dark]overlay=0:0[bg];"
        + _card_chains()
        + f"[bg][cua]overlay={CARD_X}:'{top_y}'[s1];"
        f"[s1][ila]overlay={CARD_X}:'{bot_y}',format=yuv420p[v]"
    )
    run([
        "ffmpeg", "-y",
        "-ss", f"{curio_offset:.3f}", "-t", f"{TD:.4f}", "-i", str(CURIO_TALK),
        "-loop", "1", "-t", f"{TD:.4f}", "-i", str(illus_card),
        "-loop", "1", "-t", f"{TD:.4f}", "-i", str(mask),
        "-loop", "1", "-t", f"{TD:.4f}", "-i", str(illus_bg),
        "-filter_complex", filt, "-map", "[v]", "-t", f"{TD:.4f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def concat(parts, out):
    listfile = out.parent / f"{out.stem}_concat.txt"
    listfile.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(out)])
    listfile.unlink()


def add_audio(silent, out):
    run([
        "ffmpeg", "-y", "-i", str(silent),
        "-ss", f"{AUDIO_START:.3f}", "-i", str(REEL_DIR / "audio_v2.mp3"),
        "-map", "0:v", "-map", "1:a", "-t", f"{SAMPLE_D:.4f}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out),
    ])


# ---- Assemblage des 3 styles -------------------------------------------------

def build_slide(work, mask, illus1, illus2, curve, name):
    steady = BLOCK_D - TD
    parts = []

    p = work / f"{name}_0.mp4"
    block_fullscreen(illus1, BLOCK_D, p)
    parts.append(p)

    p = work / f"{name}_1a.mp4"
    transition_slide(illus1, illus1, CURIO_OFFSET, mask, p, curve, entering=True)
    parts.append(p)
    p = work / f"{name}_1b.mp4"
    block_split(illus1, CURIO_OFFSET + TD, steady, mask, p)
    parts.append(p)

    p = work / f"{name}_2a.mp4"
    transition_slide(illus2, illus1, CURIO_OFFSET + BLOCK_D, mask, p, p_out_cubic, entering=False)
    parts.append(p)
    p = work / f"{name}_2b.mp4"
    block_fullscreen(illus2, steady, p)
    parts.append(p)

    silent = work / f"{name}_silent.mp4"
    concat(parts, silent)
    add_audio(silent, OUT_DIR / f"transition_{name}.mp4")


def build_crossfade(work, mask, illus1, illus2):
    """Fondu croisé : les blocs sont rallongés de TD, xfade reprend ce TD."""
    a = work / "xf_0.mp4"
    block_fullscreen(illus1, BLOCK_D, a)
    b = work / "xf_1.mp4"
    block_split(illus1, CURIO_OFFSET, BLOCK_D, mask, b)
    c = work / "xf_2.mp4"
    block_fullscreen(illus2, BLOCK_D, c)

    ab = work / "xf_ab.mp4"
    run(["ffmpeg", "-y", "-i", str(a), "-i", str(b),
         "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration={TD}:offset={BLOCK_D - TD},format=yuv420p[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(ab)])
    silent = work / "xf_silent.mp4"
    off = 2 * BLOCK_D - 2 * TD
    run(["ffmpeg", "-y", "-i", str(ab), "-i", str(c),
         "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration={TD}:offset={off},format=yuv420p[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(silent)])
    add_audio(silent, OUT_DIR / "transition_crossfade.mp4")


def main():
    for p in (REEL_DIR, CURIO_TALK):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="transitions_"))
    print(f"[work] {work}")

    mask = work / "mask.png"
    make_card_mask(mask)
    illus1 = REEL_DIR / "illus_1.png"
    illus2 = REEL_DIR / "illus_2.png"

    print("[1/3] slide (ease-out cubique)")
    build_slide(work, mask, illus1, illus2, p_in_cubic, "slide")
    print("[2/3] overshoot (ease-out back)")
    build_slide(work, mask, illus1, illus2, p_in_back, "overshoot")
    print("[3/3] crossfade (fondu croisé)")
    build_crossfade(work, mask, illus1, illus2)

    shutil.rmtree(work, ignore_errors=True)
    for f in sorted(OUT_DIR.glob("transition_*.mp4")):
        print(f"✅ {f}")


if __name__ == "__main__":
    main()
