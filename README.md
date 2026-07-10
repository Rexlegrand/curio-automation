# curio-automation

Pipeline CLI semi-automatisé de production de Reels Instagram pour @curio.education :
script (Claude API) → 5 images (GPT Image 2, références injectées) → 2 versions audio
(ElevenLabs) → hook animé (Dreamina, manuel) → sous-titres (Whisper local) → montage
(FFmpeg) → description Instagram (Claude API).

**Spec complète et source de vérité absolue : [`CLAUDE.md`](CLAUDE.md).**
En cas de contradiction entre ce README et CLAUDE.md, CLAUDE.md prime.

## Prérequis machine

| Outil | Rôle | Installation |
|---|---|---|
| Python 3.10+ | pipeline | recommandé : [uv](https://docs.astral.sh/uv/) → `uv python install 3.12` |
| FFmpeg | montage vidéo | `brew install ffmpeg` ou build statique |
| openai-whisper (CLI) | sous-titres, 0$ | `pip install openai-whisper` (hors venv, doit être dans le PATH) |

## Installation

```bash
git clone https://github.com/Rexlegrand/curio-automation.git
cd curio-automation

uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -r requirements.txt

cp .env.example .env   # puis remplir les 4 variables (clés API réelles, jamais commitées)
```

Variables requises dans `.env` :
- `OPENAI_API_KEY` — images GPT Image 2
- `ANTHROPIC_API_KEY` — scripts + descriptions (claude-sonnet-5)
- `ELEVENLABS_API_KEY` — voix
- `ELEVENLABS_VOICE_ID` — ID de la voix « Curio 8 » du compte ElevenLabs

Tout le reste (références visuelles PNG, clips MP4 réutilisables, logo, Excel des
compétences) est déjà dans le repo :
- `assets/curio_reference/` — 5 PNG canoniques à la racine (injectés à chaque
  génération d'image) + sous-dossiers = vivier d'exemples validés. Pour changer une
  référence : remplacer le fichier canonique.
- `assets/clips/` — curio_explication.mp4 (4s), curio_explication_2.mp4 (4s),
  curio_cta.mp4 (5s, les 2 premières secondes sont sautées au montage)
- `assets/logo_curio.png` — badge des miniatures
- `data/Competences_Curio.xlsx` — sujets Type B (onglets CP→CM2, 30 maths + 30
  français par niveau)

## Utilisation

```bash
source .venv/bin/activate

# Reel curiosité (Type A)
python main.py --type curiosite --sujet "dilatation des rails"

# Reel compétence (Type B — sujet tiré au hasard dans l'Excel)
python main.py --type competence --niveau CE2 --matiere maths

# Forcer le type de CTA (sinon : alternance automatique abonnement/commentaire)
python main.py --type curiosite --sujet "..." --cta commentaire

# Relances partielles sur un dossier existant
python main.py --only images --output-dir ./output/2026-07-10/mon_sujet/
python main.py --only audio  --output-dir ./output/2026-07-10/mon_sujet/
python main.py --assemble    --output-dir ./output/2026-07-10/mon_sujet/ --audio 1
```

## Déroulé d'un reel (4 checkpoints humains bloquants)

1. **Checkpoint 1** — le script JSON + tous les prompts s'affichent → valider
2. Génération parallèle : 5 images + 2 audios (coût affiché avant, ~0,28$)
3. **Checkpoint 2** — valider visuels et audios
4. Étape manuelle : copier `seedance_prompt.txt` dans Dreamina/Seedance, générer le
   hook animé, déposer le MP4 sous `output/.../hook_video.mp4`
5. **Checkpoint 3** — confirmer le drop + choisir audio v1/v2
6. Whisper → sous-titres (une phrase à l'écran max) ; FFmpeg → `reel_final.mp4`
   (durée = durée de l'audio, clips fixes, illustrations flexibles 5:5:3)
7. **Checkpoint 4** — visionner ; description Instagram générée → publier à la main

Coût constaté : ~0,32-0,56$ par reel (log par reel dans `output/.../api_log.jsonl`).

## Règles non négociables (détail dans CLAUDE.md §16)

- Jamais de génération d'image sans les références de `assets/curio_reference/`
- Coût affiché avant chaque appel API ; aucun fichier régénéré s'il existe déjà
- Exactitude factuelle stricte (média éducatif) — aucune digression dans les scripts
- Toute modification de code = réécriture complète du fichier, zéro patch empilé
- `output/` et `.env` ne sont jamais commités
