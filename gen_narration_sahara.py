"""Narration ElevenLabs du reel « le Sahara nourrit l'Amazonie ».

Générée SEGMENT PAR SEGMENT, un par beat, et non d'une traite. Deux raisons :

  1. la durée réelle de chaque segment devient mesurable, donc les durées des
     compositions Remotion peuvent être calées dessus au lieu d'être posées au
     jugé — c'est la seule façon d'avoir des switches qui tombent sur les mots ;
  2. Whisper devient exploitable. Avec la narration entière en `initial_prompt`,
     il recrache le texte du prompt au lieu de transcrire (constaté sur le reel
     « lacs roses » : aucun sous-titre avant 18,7 s sur une version). Segment
     par segment, chaque prompt est court et le problème disparaît.

Le premier segment reprend MOT POUR MOT la phrase du lip-sync Seedance : la
piste audio native du hook n'est jamais montée (règle v2.15), c'est cette
voix-ci qu'on entend sur le bec de Curio.

Voix : « curio 8 v2 » (générée) et non celle du .env. `ELEVENLABS_VOICE_ID`
pointe sur « Curio 8 v3 », une voix CLONÉE, refusée en 401 subscription_required
par le forfait pay-as-you-go — vérifié à nouveau le 2026-09-02.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from config import ELEVENLABS_CONFIG, ENV

REPO = Path(__file__).parent.resolve()
OUT = REPO / "assets/sahara_amazonie/audio"

VOICE_ID = "iDpRg8Sg5Xh5u2THyfPl"  # curio 8 v2, générée
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "use_speaker_boost": True}

# Un segment par beat, dans l'ordre du montage. La clé sert au nom de fichier
# et au rapprochement avec la composition Remotion correspondante.
# Un segment par beat, dans l'ordre du montage. La clé sert au nom de fichier
# et au rapprochement avec la composition Remotion correspondante.
#
# La ponctuation est délibérément hachée — points de suspension, phrases
# courtes, virgules là où on respire plutôt que là où la grammaire l'exige.
# La première version enchaînait les phrases sans un souffle et le montage
# donnait l'impression de couper sec. eleven_v3 suit la ponctuation de près :
# c'est le seul levier pour faire respirer une voix de synthèse.
SEGMENTS = [
    ("00-hook", "Attends... du sable qui nourrit une forêt ?"),
    ("01-hook-suite",
     "Le plus grand désert du monde... nourrit la plus grande forêt du monde."),
    ("02-deux-mondes",
     "D'un côté, le Sahara. Du sable. Presque rien qui pousse. "
     "De l'autre... l'Amazonie. À plus de cinq mille kilomètres."),
    ("03-route",
     "Chaque année, le vent arrache au Sahara des millions de tonnes de "
     "poussière... et les emporte au-dessus de l'Atlantique."),
    ("04-camions",
     "Vingt-sept millions de tonnes finissent leur voyage en Amazonie. "
     "L'équivalent... d'un million de camions de sable. "
     "Déversés depuis le ciel."),
    ("05-deux-sols",
     "Cette poussière contient du phosphore. Un engrais naturel. "
     "Sans lui... la pluie laverait le sol de la forêt, et l'appauvrirait."),
    ("06-revelation",
     "Et ce phosphore vient d'un endroit précis. "
     "La dépression du Bodélé, au Tchad. "
     "C'était un lac immense... aujourd'hui asséché. "
     "Son sable est fait de squelettes d'algues microscopiques."),
    ("07-chute",
     "La forêt la plus vivante de la planète... "
     "est nourrie par un lac mort il y a des milliers d'années."),
    # Le CTA écrit porte une barre oblique (« une activité/un exercice ») qu'
    # ElevenLabs lit comme une syllabe parasite : ce qui est DIT s'en passe.
    ("08-cta", "Envoie CURIO en MP pour recevoir une activité gratuite !"),
]

# ElevenLabs facture au caractère ; l'ordre de grandeur suffit à décider.
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
    total_chars = sum(len(t) for _, t in SEGMENTS)
    mots = sum(len(t.split()) for _, t in SEGMENTS)
    print(f"{len(SEGMENTS)} segments, {mots} mots, {total_chars} caractères")
    print(f"voix : curio 8 v2 ({VOICE_ID}), modèle {ELEVENLABS_CONFIG['model_id']}")
    print(f"coût estimé ~{total_chars / 1000 * COST_PER_1K_CHARS:.3f}$")
    if "--yes" not in sys.argv and input("Confirmer ? (o/n) ").strip().lower() != "o":
        sys.exit("annulé")

    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in SEGMENTS:
        target = OUT / f"{name}.mp3"
        if target.exists():
            print(f"  {name:16s} déjà là, ignoré")
            continue
        target.write_bytes(synth(text))
        print(f"  {name:16s} {target.stat().st_size // 1024} Ko")
    print(f"\n✅ {OUT}")


if __name__ == "__main__":
    main()
