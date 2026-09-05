"""Prompts Seedance des trois hooks de la session de massification.

Le hook animé est la seule étape manuelle du pipeline : Dreamina n'a pas
d'API, Benjamin copie-colle le prompt et dépose le MP4. Ce script écrit les
trois fichiers à copier, à côté de leur hook frame.

Le prompt vient de `prompts/seedance_prompts.py`, template de production
inchangé. Le fond décrit ici est le MÊME que celui passé à GPT Image 2 dans
`gen_hooks_massif.py` — c'est la règle v2.17 : un seul champ de fond pour
l'image et pour l'animation, jamais deux dérivations indépendantes (source du
bug fond foot/vélo croisé).

La phrase est reprise mot pour mot par le segment `00-hook` de la narration
ElevenLabs. La piste audio produite par Dreamina n'est jamais montée — une
seule voix porte le reel du premier au dernier cadre (règle v2.15) — mais on
la demande quand même (« Generate audio »), c'est elle qui force Seedance à
articuler chaque syllabe.
"""

from pathlib import Path

from gen_hooks_massif import REELS
from prompts.seedance_prompts import build_seedance_prompt

REPO = Path(__file__).parent.resolve()


def main() -> None:
    for nom, reel in REELS.items():
        cible = REPO / f"assets/{nom}/seedance_prompt.txt"
        cible.parent.mkdir(parents=True, exist_ok=True)
        prompt = build_seedance_prompt(
            phrase_hook=reel["phrase"],
            hook_background=reel["decor"] + ".",
        )
        cible.write_text(prompt, encoding="utf-8")
        print(f"✅ {cible.relative_to(REPO)}")


if __name__ == "__main__":
    main()
