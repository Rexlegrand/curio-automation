"""Transcrit la narration d'un reel et exporte les mots horodatés.

    python export_mots.py mariannes

Deux étapes en une commande, là où le sahara les séparait :

  1. Whisper, SEGMENT PAR SEGMENT, avec le texte du segment en `initial_prompt`.
     Jamais la narration entière : avec elle, Whisper recrache le prompt au
     lieu de transcrire (constaté sur le reel « lacs roses », aucun sous-titre
     avant 18,7 s). Un segment fait une ou deux phrases, le problème disparaît.
  2. Export mot à mot vers `remotion/public/reels/<slug>/mots/`, avec
     l'orthographe corrigée.

Whisper donne les TEMPS, pas l'orthographe : il écrivait « beau délai » pour
Bodélé, « curieux » pour CURIO. Sur un média éducatif un sous-titre faux est
pire que pas de sous-titre — les temps sont gardés, le texte corrigé depuis
`reels/<slug>.py`.

La correction se fait mot à mot par position et non par recherche : deux mots
Whisper peuvent correspondre à un seul mot dit, auquel cas le premier prend le
mot juste et le second est fusionné dans le précédent (valeur None).
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from config import WHISPER_MODEL
from reels import charger

REPO = Path(__file__).parent.resolve()
WHISPER_FALLBACK = Path.home() / "Library/Python/3.9/bin/whisper"

# Whisper détache l'apostrophe française (« D 'un côté »). Recoller après coup
# plutôt que dans le rendu : le sous-titre affiche les mots un par un et
# l'apostrophe orpheline compterait pour un mot.
APOSTROPHE = re.compile(r"\s+'")


def whisper_bin() -> str:
    found = shutil.which("whisper")
    if found:
        return found
    if WHISPER_FALLBACK.exists():
        return str(WHISPER_FALLBACK)
    sys.exit("commande 'whisper' introuvable — pip install openai-whisper")


def nettoyer(mot: str) -> str:
    return re.sub(r"[^\wàâäéèêëîïôöùûüç'-]", "", mot.strip().lower())


# Proportion des mots attendus en dessous de laquelle on considère que Whisper
# a sauté du texte. Relevé sur `polders/05-niveau` le 2026-09-03 : le modèle
# `small` n'avait transcrit que la seconde phrase des deux, soit 6 mots sur 14
# (43 %), en laissant les quatre premières secondes sans le moindre sous-titre.
# L'audio était pourtant à -20 dB de moyenne sur cette portion : ce n'est pas
# un problème de génération, c'est le modèle qui décroche.
SEUIL_MOTS = 0.7

# Modèle de rattrapage. Plus lent, mais il n'est appelé que sur les segments
# qui échouent — jamais sur un reel entier.
MODELE_SECOURS = "medium"


def compte_mots(cible: Path) -> int:
    data = json.load(open(cible))
    return len([w for s in data["segments"] for w in s.get("words", [])])


def lance_whisper(binaire: str, mp3: Path, texte: str, transcripts: Path,
                  modele: str) -> None:
    cmd = [
        binaire, str(mp3),
        "--language", "French",
        "--model", modele,
        "--output_format", "json",
        "--output_dir", str(transcripts),
        "--task", "transcribe",
        "--verbose", "False",
        "--word_timestamps", "True",
        # Sans ce drapeau (défaut CLI : True), un segment à confiance basse
        # fait boucler le modèle sur du texte déjà transcrit au lieu de
        # continuer — observé sur le reel éclipse du 13/08.
        "--condition_on_previous_text", "False",
        "--initial_prompt", texte,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Whisper a échoué sur {mp3.name} : {r.stderr.strip()[-500:]}")


def transcrire(reel, audio: Path, transcripts: Path) -> None:
    transcripts.mkdir(parents=True, exist_ok=True)
    binaire = whisper_bin()
    for cle, texte in reel.segments:
        cible = transcripts / f"{cle}.json"
        attendu = len(texte.split())
        if cible.exists():
            print(f"  {cle:16s} déjà transcrit ({compte_mots(cible)}/{attendu} mots)")
            continue

        lance_whisper(binaire, audio / f"{cle}.mp3", texte, transcripts, WHISPER_MODEL)
        obtenu = compte_mots(cible)

        # Un segment tronqué ne lève aucune erreur : il sort simplement plus
        # court, et le défaut ne se voit qu'à l'œil sur la vidéo finale. On le
        # rattrape ici plutôt que trois étapes plus loin.
        if obtenu < attendu * SEUIL_MOTS:
            print(f"  {cle:16s} {obtenu}/{attendu} mots — trop court, "
                  f"reprise sur « {MODELE_SECOURS} »")
            lance_whisper(binaire, audio / f"{cle}.mp3", texte, transcripts,
                          MODELE_SECOURS)
            obtenu = compte_mots(cible)
            if obtenu < attendu * SEUIL_MOTS:
                print(f"  {cle:16s} ⚠️  toujours {obtenu}/{attendu} mots — "
                      f"À VÉRIFIER À L'ŒIL")
        print(f"  {cle:16s} transcrit ({obtenu}/{attendu} mots)")


def exporter(reel, transcripts: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for cle, _ in reel.segments:
        data = json.load(open(transcripts / f"{cle}.json"))
        bruts = [w for s in data["segments"] for w in s.get("words", [])]
        locales = reel.corrections_segment.get(cle, {})
        mots = []
        for w in bruts:
            texte = w["word"].strip()
            k = nettoyer(texte)
            remplacement = locales.get(k, reel.corrections.get(k, texte))
            if remplacement is None:
                # Mot fantôme : sa durée revient au précédent, qui porte déjà
                # le mot juste.
                if mots:
                    mots[-1]["end"] = w["end"]
                continue
            if remplacement.startswith("'") and mots:
                mots[-1]["mot"] += remplacement
                mots[-1]["end"] = w["end"]
                continue
            mots.append({"mot": remplacement,
                         "start": round(w["start"], 3),
                         "end": round(w["end"], 3)})
        # Recollage : « D » + « 'un » deviennent « D'un ».
        fusion = []
        for m in mots:
            if fusion and m["mot"].startswith("'"):
                fusion[-1]["mot"] += m["mot"]
                fusion[-1]["end"] = m["end"]
            else:
                fusion.append(m)
        (out / f"{cle}.json").write_text(
            json.dumps(fusion, ensure_ascii=False), encoding="utf-8")
        print(f"{cle:16s} {len(fusion):3d} mots  "
              f"{' '.join(m['mot'] for m in fusion)[:64]}")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {Path(__file__).name} <slug>")
    reel = charger(sys.argv[1])
    audio = REPO / f"assets/{reel.slug}/audio"
    transcripts = audio / "transcripts"
    out = REPO / f"remotion/public/reels/{reel.slug}/mots"

    print(f"{reel.titre} — Whisper ({WHISPER_MODEL}), {len(reel.segments)} segments")
    transcrire(reel, audio, transcripts)
    print()
    exporter(reel, transcripts, out)
    print(f"\n✅ {out}")


if __name__ == "__main__":
    main()
