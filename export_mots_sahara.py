"""Exporte les mots horodatés de la narration pour les sous-titres Remotion.

Whisper donne les temps, pas l'orthographe : il écrit « beau délai » pour
Bodélé, « curieux » pour CURIO, « la pauvrirait » pour l'appauvrirait. Sur un
média éducatif, un sous-titre faux est pire que pas de sous-titre — les temps
sont donc gardés, le texte corrigé.

La correction se fait mot à mot par position et non par recherche : deux mots
Whisper peuvent correspondre à un seul mot dit, auquel cas le premier prend le
mot juste et le second est fusionné dans le précédent.

Sortie : remotion/public/sahara/mots/<segment>.json
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).parent.resolve()
import sys

# Deux montages coexistent : `audio/` pour le premier, `audio2/` pour le second.
VERSION = "2" if "--v2" in sys.argv else ""
SRC = REPO / f"assets/sahara_amazonie/audio{VERSION}/transcripts"
OUT = REPO / f"remotion/public/sahara/mots{VERSION}"

# Erreurs relevées sur la transcription du 2026-09-02. Clé : ce que Whisper
# écrit, en minuscules et sans ponctuation. Valeur : ce qui est réellement dit.
CORRECTIONS = {
    "beau": "Bodélé",
    "baudélé": "Bodélé",
    "délai": None,          # fusionné dans le précédent
    "hautschad": "au Tchad",
    "curieux": "CURIO",
    "curio": "CURIO",
    "pauvrirait": "appauvrirait",
    "sensible": "Son sable",
    "asséchée": "asséché",
}

# Corrections propres à un segment : le même mot peut être juste ailleurs.
# « ne » est correct partout sauf ici, où Whisper avale la contraction, et
# « levant » n'est faux que dans le segment où il entend « le vent ».
CORRECTIONS_SEGMENT = {
    "03-algues": {"ne": "n'est"},
    "04-voyage": {"levant": "Le vent", "arrachent": "arrache", "emportent": "emporte"},
}

# Whisper détache l'apostrophe française (« D 'un côté »). Recoller après coup
# plutôt que dans le rendu : le sous-titre affiche les mots un par un et
# l'apostrophe orpheline compterait pour un mot.
APOSTROPHE = re.compile(r"\s+'")


def nettoyer(mot: str) -> str:
    return re.sub(r"[^\wàâäéèêëîïôöùûüç'-]", "", mot.strip().lower())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for fichier in sorted(SRC.glob("*.json")):
        data = json.load(open(fichier))
        bruts = [w for s in data["segments"] for w in s.get("words", [])]
        mots = []
        locales = CORRECTIONS_SEGMENT.get(fichier.stem, {})
        for w in bruts:
            texte = w["word"].strip()
            cle = nettoyer(texte)
            remplacement = locales.get(cle, CORRECTIONS.get(cle, texte))
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
            mots.append({
                "mot": remplacement,
                "start": round(w["start"], 3),
                "end": round(w["end"], 3),
            })
        # Recollage : « D » + « 'un » deviennent « D'un ».
        fusion = []
        for m in mots:
            if fusion and m["mot"].startswith("'"):
                fusion[-1]["mot"] += m["mot"]
                fusion[-1]["end"] = m["end"]
            else:
                fusion.append(m)
        mots = fusion
        (OUT / f"{fichier.stem}.json").write_text(
            json.dumps(mots, ensure_ascii=False), encoding="utf-8")
        print(f"{fichier.stem:16s} {len(mots):3d} mots  "
              f"{' '.join(m['mot'] for m in mots)[:70]}")
    print(f"\n✅ {OUT}")


if __name__ == "__main__":
    main()
