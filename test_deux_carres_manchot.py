"""Retrofit du reel manchot empereur au format « deux carrés ».

Reprend un reel DÉJÀ terminé (output/2026-08-20/le_manchot_empereur_.../) et
reconstruit uniquement son corps, en gardant le hook et le CTA existants :

    0.000 → 4.096   hook_video.mp4, plein écran (inchangé)
    4.096 → 33.304  corps : 10 blocs de 2.92s, alternance
                    plein écran / deux carrés / plein écran / ...
    33.304 → 37.400 curio_cta.mp4, plein écran (inchangé)

Format « deux carrés » : fond sombre, deux cartes arrondies empilées — Curio
qui parle en haut (clip Dreamina réutilisable, découpé à la volée), illustration
du sujet en bas. Les sous-titres tombent dans la carte du bas.

Rien n'est écrit dans output/ : l'original reste intact, le rendu part dans
testing_remotion/ (règle projet sur les rendus de test).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from config import VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH  # noqa: E402
from generators.video_assembler import _render_captions_overlay  # noqa: E402

# .resolve() obligatoire : _render_captions_overlay() lance Remotion avec
# cwd=remotion/, donc un chemin relatif vers le fichier --props ne serait pas
# retrouvé (« You passed --props but it was neither valid JSON nor a file path »).
REPO = Path(__file__).parent.resolve()
REEL_DIR = REPO / "output/2026-08-20/le_manchot_empereur_qui_jeune_deux_mois_pour_son_uf"
CURIO_TALK = Path.home() / "Downloads/dreamina-2026-08-30-1373-Animate this exact image. Keep the chara....mp4"
CTA_CLIP = REPO / "assets/clips/curio_cta.mp4"
OUT_DIR = REPO / "testing_remotion/manchot_deux_carres"

# ---- Timeline ----
HOOK_D = 4.096
CTA_D = 4.096
TOTAL = 37.400  # audio_v2 (37.20s) + AUDIO_TAIL (0.2s)
BODY_START = HOOK_D
BODY_END = TOTAL - CTA_D
N_BLOCKS = 10
BLOCK_D = (BODY_END - BODY_START) / N_BLOCKS  # ≈ 2.92s

# Illustration affichée par bloc, calée sur les timecodes réels du SRT :
# illus_1 « le papa garde l'œuf » jusqu'à ~16.5s, illus_2 « -60°, les papas se
# serrent » jusqu'à ~24s, illus_3 « la maman nourrit le bébé » ensuite.
BLOCK_ILLUS = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3]
# Bloc pair = plein écran, bloc impair = deux carrés (le corps s'ouvre donc sur
# une illustration plein écran, juste après le hook).
BLOCK_IS_SPLIT = [i % 2 == 1 for i in range(N_BLOCKS)]
# Fenêtres différentes du clip Curio (10.05s) pour les 5 blocs deux carrés,
# afin que la répétition ne se voie pas.
CURIO_OFFSETS = [0.0, 2.4, 4.8, 7.1, 1.2]

# ---- Géométrie des cartes ----
CARD_W, CARD_H, CARD_R = 940, 855, 36
CARD_X = (VIDEO_WIDTH - CARD_W) // 2  # 70
TOP_Y = 80
GAP = 50
BOT_Y = TOP_Y + CARD_H + GAP  # 985 → marge basse 80, symétrique
BG_COLOR = "0x0E1013"


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def make_card_mask(path):
    """Masque niveaux de gris : coins arrondis de la carte (blanc = visible)."""
    img = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(img).rounded_rectangle(
        [0, 0, CARD_W - 1, CARD_H - 1], radius=CARD_R, fill=255
    )
    img.save(path)


def cover(src_w, src_h, dst_w, dst_h, focus=0.5):
    """Crop 'cover' : remplit dst sans déformer. focus = centre vertical visé."""
    if src_w / src_h > dst_w / dst_h:
        # source trop large : on rogne en largeur
        h = src_h
        w = round(src_h * dst_w / dst_h)
        x, y = (src_w - w) // 2, 0
    else:
        # source trop haute : on rogne en hauteur, autour de focus
        w = src_w
        h = round(src_w * dst_h / dst_w)
        x = 0
        y = max(0, min(src_h - h, round(src_h * focus - h / 2)))
    return w, h, x, y


def block_fullscreen(illus, dur, out):
    """Illustration plein écran, image fixe."""
    w, h, x, y = cover(1024, 1792, VIDEO_WIDTH, VIDEO_HEIGHT, focus=0.5)
    run([
        "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.4f}", "-i", str(illus),
        "-vf", f"crop={w}:{h}:{x}:{y},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def block_split(illus, curio_offset, dur, mask, out):
    """Deux cartes arrondies : Curio en haut, illustration en bas."""
    # Curio : 720x1280. Cadrage calé pour garder l'enseigne néon
    # « curio.education » ENTIÈRE en haut (à 0.455 elle était coupée en deux)
    # tout en gardant la tête et le micro dans la carte.
    cw, ch, cx, cy = cover(720, 1280, CARD_W, CARD_H, focus=0.4345)
    # Illustration : le sujet vit dans la moitié haute (les 30% du bas sont
    # volontairement vides côté charte), on cadre donc au-dessus du centre.
    iw, ih, ix, iy = cover(1024, 1792, CARD_W, CARD_H, focus=0.42)

    filt = (
        f"color=c={BG_COLOR}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r={VIDEO_FPS}:d={dur:.4f}[bg];"
        f"[0:v]crop={cw}:{ch}:{cx}:{cy},scale={CARD_W}:{CARD_H},fps={VIDEO_FPS},format=rgba[cu];"
        f"[2:v]format=gray[mk];"
        f"[cu][mk]alphamerge[cua];"
        f"[1:v]crop={iw}:{ih}:{ix}:{iy},scale={CARD_W}:{CARD_H},format=rgba[il];"
        f"[2:v]format=gray[mk2];"
        f"[il][mk2]alphamerge[ila];"
        f"[bg][cua]overlay={CARD_X}:{TOP_Y}[s1];"
        f"[s1][ila]overlay={CARD_X}:{BOT_Y},format=yuv420p[v]"
    )
    run([
        "ffmpeg", "-y",
        "-ss", f"{curio_offset:.3f}", "-t", f"{dur:.4f}", "-i", str(CURIO_TALK),
        "-loop", "1", "-t", f"{dur:.4f}", "-i", str(illus),
        "-loop", "1", "-t", f"{dur:.4f}", "-i", str(mask),
        "-filter_complex", filt, "-map", "[v]",
        "-t", f"{dur:.4f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def block_passthrough(src, dur, out):
    """Hook / CTA : normalisés en 1080x1920 30fps, sans audio."""
    run([
        "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.4f}",
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
               f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def main():
    for p in (REEL_DIR, CURIO_TALK, CTA_CLIP):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="deux_carres_"))
    print(f"[work] {work}")

    mask = work / "mask.png"
    make_card_mask(mask)

    parts = []

    print("[1/5] hook")
    p = work / "000_hook.mp4"
    block_passthrough(REEL_DIR / "hook_video.mp4", HOOK_D, p)
    parts.append(p)

    print(f"[2/5] corps — {N_BLOCKS} blocs de {BLOCK_D:.3f}s")
    for i in range(N_BLOCKS):
        illus = REEL_DIR / f"illus_{BLOCK_ILLUS[i]}.png"
        p = work / f"{i + 1:03d}_body.mp4"
        if BLOCK_IS_SPLIT[i]:
            off = CURIO_OFFSETS[sum(BLOCK_IS_SPLIT[:i])]
            block_split(illus, off, BLOCK_D, mask, p)
            print(f"      bloc {i} deux-carrés  illus_{BLOCK_ILLUS[i]}  curio@{off}s")
        else:
            block_fullscreen(illus, BLOCK_D, p)
            print(f"      bloc {i} plein écran  illus_{BLOCK_ILLUS[i]}")
        parts.append(p)

    print("[3/5] cta")
    p = work / "999_cta.mp4"
    block_passthrough(CTA_CLIP, CTA_D, p)
    parts.append(p)

    print("[4/5] concat + audio")
    listfile = work / "concat.txt"
    listfile.write_text("".join(f"file '{p}'\n" for p in parts))
    silent = work / "montage_silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c", "copy", str(silent)])

    with_audio = work / "montage_audio.mp4"
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(REEL_DIR / "audio_v2.mp3"),
         "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]",
         "-t", f"{TOTAL:.4f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         str(with_audio)])

    print("[5/5] sous-titres (Remotion)")
    seq_dir, pad = _render_captions_overlay(REEL_DIR, TOTAL)
    final = OUT_DIR / "reel_manchot_deux_carres_v1.mp4"
    try:
        run(["ffmpeg", "-y", "-i", str(with_audio),
             "-framerate", str(VIDEO_FPS), "-i", f"{seq_dir}/element-%0{pad}d.png",
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
             "-map", "[v]", "-map", "0:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-c:a", "copy", "-t", f"{TOTAL:.4f}", str(final)])
    finally:
        shutil.rmtree(seq_dir, ignore_errors=True)

    shutil.rmtree(work, ignore_errors=True)
    print(f"\n✅ {final}")


if __name__ == "__main__":
    main()
