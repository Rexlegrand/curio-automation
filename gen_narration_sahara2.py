"""Narration du SECOND montage — « le Sahara nourrit l'Amazonie », version 2.

Même matière, autre ordre. La première version suivait la géographie : les deux
mondes, le voyage, le chiffre, l'effet, la révélation. Celle-ci part du CHIFFRE,
remonte à l'origine, puis explique — l'ordre d'une enquête plutôt que celui d'un
exposé, et il donne surtout au montage un rythme d'alternance : chaque bloc
d'explication appelle Curio, chaque preuve appelle le plein écran.

Sept segments au lieu de neuf, plus longs : le switch a besoin de durée pour
s'installer, un plan de cinq secondes ne supporte pas une bascule.

Voix : « curio 8 v2 » (générée). Celle du .env, « Curio 8 v3 », est clonée et
reste refusée en 401 subscription_required sur le forfait pay-as-you-go.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from config import ELEVENLABS_CONFIG, ENV

REPO = Path(__file__).parent.resolve()
OUT = REPO / "assets/sahara_amazonie/audio2"

VOICE_ID = "iDpRg8Sg5Xh5u2THyfPl"
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "use_speaker_boost": True}

SEGMENTS = [
    ("00-hook", "Attends... du sable qui nourrit une forêt ?"),
    ("01-chiffre",
     "Chaque année, vingt-sept millions de tonnes de sable tombent sur "
     "l'Amazonie. L'équivalent... d'un million de camions. "
     "Déversés depuis le ciel."),
    ("02-origine",
     "Et tout ce sable vient d'un seul endroit. La dépression du Bodélé, au "
     "Tchad. Un lac immense... asséché depuis des milliers d'années."),
    ("03-algues",
     "Son sable n'est pas vraiment du sable. Ce sont des squelettes d'algues "
     "microscopiques."),
    ("04-voyage",
     "Le vent les arrache... et les emporte sur cinq mille kilomètres, "
     "au-dessus de l'Atlantique."),
    ("05-phosphore",
     "Ces algues contiennent du phosphore. Un engrais naturel. "
     "Sans lui... la pluie appauvrirait le sol de la forêt."),
    ("06-chute",
     "La forêt la plus vivante de la planète... est nourrie par un lac mort."),
    ("07-cta", "Envoie CURIO en MP pour recevoir une activité gratuite !"),
]

COST_PER_1K_CHARS = 0.11


def synth(text: str) -> bytes:
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        f"?output_format={ELEVENLABS_CONFIG.get('output_format', 'mp3_44100_128')}",
        data=json.dumps({
            "text": text,
            "model_id": ELEVENLABS_CONFIG["model_id"],
            "voice_settings": VOICE_SETTINGS,
        }).encode(),
        headers={"xi-api-key": ENV["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
    )
    try:
        return urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"ElevenLabs {exc.code} : {exc.read()[:300].decode(errors='replace')}")


def main() -> None:
    chars = sum(len(t) for _, t in SEGMENTS)
    mots = sum(len(t.split()) for _, t in SEGMENTS)
    print(f"{len(SEGMENTS)} segments, {mots} mots, {chars} caractères")
    print(f"coût estimé ~{chars / 1000 * COST_PER_1K_CHARS:.3f}$")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in SEGMENTS:
        target = OUT / f"{name}.mp3"
        if target.exists():
            print(f"  {name:14s} déjà là")
            continue
        target.write_bytes(synth(text))
        print(f"  {name:14s} {target.stat().st_size // 1024} Ko")
    print(f"\n✅ {OUT}")


if __name__ == "__main__":
    main()
