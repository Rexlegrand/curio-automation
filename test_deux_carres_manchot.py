"""Reel manchot empereur au format « deux carrés », corps rendu par Remotion.

Reprend un reel DÉJÀ terminé (output/2026-08-20/le_manchot_empereur_.../) et
reconstruit uniquement son corps, en gardant le hook et le CTA existants :

    0.000 → 4.096   hook_video.mp4, plein écran (inchangé)
    4.096 → 33.296  corps : 10 blocs de ~2.92s, alternance
                    plein écran / deux carrés / plein écran / ...
    33.296 → 37.392 curio_cta.mp4, plein écran (inchangé)

Format « deux carrés » : fond sombre, deux cartes arrondies empilées — Curio
qui parle en haut (clip Dreamina réutilisable, découpé à la volée), illustration
du sujet en bas. Les sous-titres tombent dans la carte du bas.

Le corps n'est plus assemblé bloc par bloc en FFmpeg (cut sec) mais rendu d'un
seul tenant par Remotion (composition CurioDeuxCarres, enregistrée dans
Root.experiments.tsx, JAMAIS dans Root.tsx qui reste la production) : le raccord
plein écran ↔ deux carrés est animé. Le rythme ne change pas — une coupe toutes
les ~2,92s — seul le raccord est adouci. Deux styles sont rendus :

    overshoot — les cartes glissent depuis le haut et le bas, ressort
                légèrement amorti (elles dépassent d'un cheveu puis se posent).
    crossfade — les cartes ne bougent pas, les deux états se fondent.

Une transition ne s'ajoute JAMAIS au montage : elle consomme les premières
images du bloc qui arrive. La durée totale reste verrouillée sur l'audio.

FFmpeg garde le hook, le CTA, l'audio et l'incrustation des sous-titres — ces
derniers sont rendus UNE fois (composition TikTokCaptions du pipeline) puis
incrustés sur les deux versions.

Rien n'est écrit dans output/ : l'original reste intact, les rendus partent
dans testing_remotion/ (règle projet sur les rendus de test).
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH  # noqa: E402
from generators.video_assembler import _render_captions_overlay  # noqa: E402

# .resolve() obligatoire : _render_captions_overlay() lance Remotion avec
# cwd=remotion/, donc un chemin relatif vers le fichier --props ne serait pas
# retrouvé (« You passed --props but it was neither valid JSON nor a file path »).
REPO = Path(__file__).parent.resolve()
REEL_DIR = REPO / "output/2026-08-20/le_manchot_empereur_qui_jeune_deux_mois_pour_son_uf"
CURIO_TALK = Path.home() / "Downloads/dreamina-2026-08-31-3729-Animate this exact image. Keep the pengu....mp4"
CTA_CLIP = REPO / "assets/clips/curio_cta.mp4"
REMOTION_DIR = REPO / "remotion"
PUBLIC_DIR = REMOTION_DIR / "public" / "deux-carres"
OUT_DIR = REPO / "testing_remotion/manchot_deux_carres"

STYLES = ["overshoot", "crossfade"]

# ---- Timeline ----
HOOK_D = 4.096
CTA_D = 4.096
AUDIO_TOTAL = 37.400  # audio_v2 (37.20s) + AUDIO_TAIL (0.2s)
N_BLOCKS = 10
# Le corps est rendu par Remotion, donc compté en images entières : c'est lui
# qui fixe la durée réelle du montage, pas un flottant en secondes.
BODY_FRAMES = round((AUDIO_TOTAL - HOOK_D - CTA_D) * VIDEO_FPS)  # 876 → 29,2s
TRANSITION_FRAMES = 11  # ≈ 0,37s, pris SUR le bloc entrant

# Illustration affichée par bloc, calée sur les timecodes réels du SRT :
# illus_1 « le papa garde l'œuf » jusqu'à ~16.5s, illus_2 « -60°, les papas se
# serrent » jusqu'à ~24s, illus_3 « la maman nourrit le bébé » ensuite.
BLOCK_ILLUS = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2]
# Bloc pair = plein écran, bloc impair = deux carrés (le corps s'ouvre donc sur
# une illustration plein écran, juste après le hook).
BLOCK_IS_SPLIT = [i % 2 == 1 for i in range(N_BLOCKS)]
# Fenêtres différentes du clip Curio (10,08s) pour les 5 blocs deux carrés,
# afin que la répétition ne se voie pas. Plafond : un bloc plein écran qui SUIT
# un bloc deux carrés rejoue la fin de la même fenêtre pendant sa transition de
# sortie, donc offset + durée du bloc + transition doit rester sous 10,08s.
CURIO_OFFSETS = [0.0, 2.3, 4.6, 6.7, 1.15]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def build_blocks():
    """Plan des 10 blocs, en images entières, sans dérive d'arrondi cumulée."""
    bounds = [round(i * BODY_FRAMES / N_BLOCKS) for i in range(N_BLOCKS + 1)]
    blocks = []
    split_seen = 0
    for i in range(N_BLOCKS):
        is_split = BLOCK_IS_SPLIT[i]
        duration = bounds[i + 1] - bounds[i]

        if is_split:
            curio_offset = CURIO_OFFSETS[split_seen]
            split_seen += 1
        elif i == 0:
            curio_offset = 0.0
        else:
            # Bloc plein écran qui suit un bloc deux carrés : sa transition de
            # sortie montre encore les cartes, le clip Curio doit donc continuer
            # là où le bloc précédent s'est arrêté (pas de saut dans le bec).
            prev = blocks[i - 1]
            curio_offset = prev["curioOffset"] + prev["duration"] / VIDEO_FPS

        # Pendant une transition, l'écran montre les DEUX états à la fois : le
        # fond plein écran vient du bloc plein écran concerné, les cartes du
        # bloc deux carrés concerné — jamais la même source pour les deux.
        blocks.append({
            "start": bounds[i],
            "duration": duration,
            "isSplit": is_split,
            "bgIllus": BLOCK_ILLUS[i - 1] if is_split else BLOCK_ILLUS[i],
            "cardIllus": BLOCK_ILLUS[i] if is_split else BLOCK_ILLUS[max(i - 1, 0)],
            "curioOffset": curio_offset,
            "isFirst": i == 0,
        })
    return blocks


def stage_public_assets():
    """Remotion ne lit que remotion/public/ : on y dépose les sources du reel."""
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)
    shutil.copyfile(CURIO_TALK, PUBLIC_DIR / "curio_talk.mp4")
    for i in range(1, 4):
        shutil.copyfile(REEL_DIR / f"illus_{i}.png", PUBLIC_DIR / f"illus_{i}.png")


def render_body(blocks, style, work):
    """Rend le corps (10 blocs + raccords) en un seul MP4 via Remotion."""
    props = {
        "curioSrc": "deux-carres/curio_talk.mp4",
        "illusSrcs": [f"deux-carres/illus_{i}.png" for i in range(1, 4)],
        "blocks": blocks,
        "transitionFrames": TRANSITION_FRAMES,
        "transitionStyle": style,
        "totalFrames": BODY_FRAMES,
    }
    # work est un dossier temp système (/var/folders/...) : son chemin ne
    # contient aucun point. Le CLI Remotion découpe le CHEMIN ABSOLU ENTIER sur
    # les points pour deviner une extension (bug amont, cf. CLAUDE.md v2.19) et
    # "/Users/benjamin.ptryhuml/..." le fait échouer.
    props_path = work / f"props_{style}.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))
    body = work / f"body_{style}.mp4"
    run([
        "npx", "remotion", "render", "src/index.experiments.ts", "CurioDeuxCarres",
        str(body), f"--props={props_path}", "--muted", "--log=error",
    ], cwd=REMOTION_DIR)
    return body


def normalize_clip(src, dur, out):
    """Hook / CTA : normalisés en 1080x1920 30fps, sans audio."""
    run([
        "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.4f}",
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
               f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={VIDEO_FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(out),
    ])


def assemble(hook, body, cta, work, style):
    """hook + corps + CTA, puis voix ElevenLabs seule sur toute la durée."""
    silent = work / f"montage_silent_{style}.mp4"
    run([
        "ffmpeg", "-y", "-i", str(hook), "-i", str(body), "-i", str(cta),
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0,format=yuv420p[v]",
        "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(silent),
    ])
    with_audio = work / f"montage_audio_{style}.mp4"
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(REEL_DIR / "audio_v2.mp3"),
        "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]",
        "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(with_audio),
    ])
    return with_audio


def burn_captions(with_audio, seq_dir, pad, out):
    run([
        "ffmpeg", "-y", "-i", str(with_audio),
        "-framerate", str(VIDEO_FPS), "-i", f"{seq_dir}/element-%0{pad}d.png",
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "copy", str(out),
    ])


def main():
    for p in (REEL_DIR, CURIO_TALK, CTA_CLIP):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="deux_carres_"))
    print(f"[work] {work}")

    blocks = build_blocks()
    print(f"[1/5] plan : {N_BLOCKS} blocs, corps de {BODY_FRAMES} images "
          f"({BODY_FRAMES / VIDEO_FPS:.3f}s), transition {TRANSITION_FRAMES} images")
    for i, b in enumerate(blocks):
        kind = "deux-carrés" if b["isSplit"] else "plein écran "
        print(f"      bloc {i} {kind} {b['duration']:3d}f  "
              f"fond=illus_{b['bgIllus'] + 1}  carte=illus_{b['cardIllus'] + 1}  "
              f"curio@{b['curioOffset']:.2f}s")

    print("[2/5] copie des sources dans remotion/public/deux-carres/")
    stage_public_assets()

    print("[3/5] hook + CTA")
    hook = work / "hook.mp4"
    normalize_clip(REEL_DIR / "hook_video.mp4", HOOK_D, hook)
    cta = work / "cta.mp4"
    normalize_clip(CTA_CLIP, CTA_D, cta)

    print("[4/5] sous-titres animés (Remotion, rendus une fois pour les 2 versions)")
    seq_dir, pad = _render_captions_overlay(REEL_DIR, AUDIO_TOTAL)

    finals = []
    try:
        for n, style in enumerate(STYLES, start=1):
            print(f"[5/5] version {n}/{len(STYLES)} — {style}")
            print("      corps (Remotion)…")
            body = render_body(blocks, style, work)
            print("      montage + audio…")
            with_audio = assemble(hook, body, cta, work, style)
            print("      incrustation des sous-titres…")
            final = OUT_DIR / f"reel_manchot_deux_carres_{style}.mp4"
            burn_captions(with_audio, seq_dir, pad, final)
            finals.append(final)
    finally:
        shutil.rmtree(seq_dir, ignore_errors=True)
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)

    shutil.rmtree(work, ignore_errors=True)
    print()
    for f in finals:
        print(f"✅ {f}")


if __name__ == "__main__":
    main()
