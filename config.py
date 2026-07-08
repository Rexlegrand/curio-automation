"""Clés API, constantes globales et helpers partagés du pipeline Curio."""

import datetime
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ASSETS_DIR = ROOT / "assets"
REFERENCE_DIR = ASSETS_DIR / "curio_reference"
CLIPS_DIR = ASSETS_DIR / "clips"
LOGO_PATH = ASSETS_DIR / "logo_curio.png"
DATA_XLSX = ROOT / "data" / "Competences_Curio.xlsx"
OUTPUT_DIR = ROOT / "output"

REFERENCE_FILES = [
    "style_fond_cahier.png",
    "style_illustration_01.png",
    "style_illustration_02.png",
    "curio_character_ref.png",
    "miniature_exemple.png",
]

CLIP_EXPLICATION_A = CLIPS_DIR / "curio_explication.mp4"
CLIP_EXPLICATION_B = CLIPS_DIR / "curio_explication_2.mp4"
CLIP_CTA = CLIPS_DIR / "curio_cta.mp4"

# Modèles
CLAUDE_MODEL = "claude-sonnet-5"
OPENAI_IMAGE_MODEL = "gpt-image-2"
IMAGE_SIZE = "1024x1792"
IMAGE_SIZE_FALLBACK = "1024x1536"  # si l'API refuse la taille du brief
WHISPER_MODEL = "small"

# Coûts estimés (USD)
COST_IMAGE = 0.011
COST_AUDIO_VERSION = 0.11
COST_SCRIPT = 0.02
COST_DESCRIPTION = 0.02

ELEVENLABS_CONFIG = {
    "model_id": "eleven_v3",
    "language": "fr",
    "target_duration_seconds": (28, 35),
    "word_count_target": (85, 100),  # eleven_v3 lit ~180 mots/min mesurés
    "versions_to_generate": 2,
    "output_format": "mp3_44100_128",
}

# Séquence de montage : la durée totale du reel = durée de l'audio choisi (+ AUDIO_TAIL).
# Les clips sont fixes ; les illustrations sont flexibles et se partagent le temps
# restant au prorata de leur poids (5:5:3), pour que le CTA rentre toujours.
# CTA : on saute les 2 premières secondes du clip (inutiles), on garde les 3 dernières.
TIMELINE = [
    ("hook_video.mp4", {"fixed": 4}),
    ("illus_1.png", {"flex": 5}),
    (CLIP_EXPLICATION_A, {"fixed": 4}),
    ("illus_2.png", {"flex": 5}),
    (CLIP_EXPLICATION_B, {"fixed": 4}),
    ("illus_3.png", {"flex": 3}),
    (CLIP_CTA, {"fixed": 3, "trim_start": 2.0}),
]
AUDIO_TAIL = 0.2  # marge après la fin de la voix, en secondes

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_BITRATE = "6M"

# Sous-titres : style aligné sur la référence publiée @curio.education
# (blanc bold, contour noir épais, sans boîte), une seule phrase à l'écran
SUBTITLE_FONT_SIZE = 60
SUBTITLE_MARGIN_V = int(VIDEO_HEIGHT * 0.21)  # baseline ~79% de la hauteur


def load_env():
    """Lit le fichier .env à la racine et retourne un dict clé → valeur."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        sys.exit("Erreur : fichier .env introuvable à la racine du projet.")
    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    required = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "ANTHROPIC_API_KEY", "ELEVENLABS_VOICE_ID"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        sys.exit(f"Erreur : variables manquantes dans .env : {', '.join(missing)}")
    return env


ENV = load_env()


def slugify(text):
    """'Dilatation des rails' → 'dilatation_des_rails'."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = "".join(c if c.isalnum() else "_" for c in text.lower())
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")


def confirm(message):
    """Question bloquante o/n. Retourne True si 'o'."""
    while True:
        answer = input(f"{message} (o/n) : ").strip().lower()
        if answer in ("o", "oui", "y"):
            return True
        if answer in ("n", "non"):
            return False


def confirm_cost(step_label, cost_usd):
    """Affiche le coût estimé et demande confirmation avant un appel API."""
    return confirm(f"{step_label} — cette étape coûtera ~{cost_usd:.3f}$. Confirmer ?")


def log_api_call(output_dir, service, cost_usd, generated_file):
    """Log JSONL de chaque appel API : timestamp, service, coût, fichier."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "service": service,
        "cost_usd": round(cost_usd, 4),
        "file": str(generated_file),
    }
    log_path = Path(output_dir) / "api_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def check_references():
    """Règle 8 : bloque si les références visuelles manquent."""
    missing = [f for f in REFERENCE_FILES if not (REFERENCE_DIR / f).exists()]
    if missing:
        sys.exit(
            "BLOQUÉ — références visuelles manquantes dans assets/curio_reference/ :\n"
            + "\n".join(f"  - {f}" for f in missing)
            + "\nDépose les fichiers puis relance. Aucune image ne sera générée sans référence."
        )


def retry_loop(step_label, func):
    """Exécute func(). En cas d'échec : affiche l'erreur claire, propose retry."""
    while True:
        try:
            return func()
        except Exception as exc:
            print(f"\nERREUR — {step_label} : {exc}")
            if not confirm("Réessayer ?"):
                sys.exit(f"Pipeline arrêté à l'étape : {step_label}")
