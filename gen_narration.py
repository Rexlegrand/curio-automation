"""Narration ElevenLabs d'un reel de série, segment par segment.

    python gen_narration.py mariannes [--yes]

Généralisation de `gen_narration_sahara.py` : le texte vient du spec
(`reels/<slug>.py`), tout le reste est identique et commun aux trois reels.

Segment par segment, et jamais d'une traite, pour deux raisons établies sur le
sahara :

  1. la durée réelle de chaque segment devient mesurable, donc les durées des
     compositions Remotion se calent dessus au lieu d'être posées au jugé —
     c'est la seule façon d'avoir des switches qui tombent sur les mots ;
  2. Whisper devient exploitable. Avec la narration entière en `initial_prompt`
     il recrache le texte du prompt au lieu de transcrire (constaté sur le reel
     « lacs roses »). Segment par segment, chaque prompt est court et le
     problème disparaît.

Voix : « curio 8 v2 », générée, et NON celle du .env. `ELEVENLABS_VOICE_ID`
pointe sur « Curio 8 v3 », une voix clonée que le forfait pay-as-you-go refuse
en 401 subscription_required — constaté les 17/08, 01/09 et 02/09.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from config import ELEVENLABS_CONFIG, ENV
from reels import charger

REPO = Path(__file__).parent.resolve()

VOICE_ID = "iDpRg8Sg5Xh5u2THyfPl"  # curio 8 v2, générée
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "use_speaker_boost": True}

COST_PER_1K_CHARS = 0.11  # ElevenLabs facture au caractère


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
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug> [--yes]")
    reel = charger(sys.argv[1])
    out = REPO / f"assets/{reel.slug}/audio"

    # Un segment déjà sur le disque n'est jamais regénéré : relancer le script
    # ne refacture rien.
    a_faire = [(k, t) for k, t in reel.segments if not (out / f"{k}.mp3").exists()]
    if not a_faire:
        print(f"{reel.slug} : les {len(reel.segments)} segments sont déjà là")
        return

    chars = sum(len(t) for _, t in a_faire)
    mots = sum(len(t.split()) for _, t in a_faire)
    print(f"{reel.titre} — {len(a_faire)} segments, {mots} mots, {chars} caractères")
    print(f"voix : curio 8 v2 ({VOICE_ID}), modèle {ELEVENLABS_CONFIG['model_id']}")
    print(f"coût estimé ~{chars / 1000 * COST_PER_1K_CHARS:.3f}$")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")

    out.mkdir(parents=True, exist_ok=True)
    for name, text in a_faire:
        target = out / f"{name}.mp3"
        target.write_bytes(synth(text))
        print(f"  {name:16s} {target.stat().st_size // 1024} Ko")
    print(f"\n✅ {out}")


if __name__ == "__main__":
    main()
