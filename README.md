# curio-automation

Pipeline CLI semi-automatisé de production de Reels Instagram pour @curio.education.
Spec complète : `CLAUDE.md` (source de vérité absolue).

## Installation

```bash
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -r requirements.txt
```

Prérequis hors venv : FFmpeg, openai-whisper (CLI), fichier `.env` rempli.

Avant le premier Reel, déposer :
- `assets/curio_reference/` — les 5 PNG de référence (voir CLAUDE.md §6)
- `assets/clips/` — curio_explication.mp4, curio_explication_2.mp4, curio_cta.mp4
- `assets/logo_curio.png`
- `data/Competences_Curio.xlsx` (Type B uniquement)

## Utilisation

```bash
source .venv/bin/activate

# Reel curiosité
python main.py --type curiosite --sujet "dilatation des rails"

# Reel compétence (sujet tiré du Excel)
python main.py --type competence --niveau CE2 --matiere maths

# Relances partielles
python main.py --only images --output-dir ./output/2026-07-07/dilatation_des_rails/
python main.py --only audio  --output-dir ./output/2026-07-07/dilatation_des_rails/
python main.py --assemble    --output-dir ./output/2026-07-07/dilatation_des_rails/
```

Le pipeline s'arrête à 4 checkpoints humains (script, visuels/audio, drop du hook
Dreamina, visionnage final) et affiche le coût estimé avant chaque appel API.
