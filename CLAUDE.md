CURIO AUTOMATION — CLAUDE CODE BRIEF
Version : 2.2 — Durée du reel calée sur l'audio (timeline dynamique, illustrations flexibles, CTA rogné)
Modèle cible : Claude-fable 5 (ou équivalent le plus puissant disponible)
Rédigé par : Benjamin Petry—Hummel — Juillet 2026

RÈGLE ABSOLUE N°1 — STRUCTURE DU CODE
Ne jamais empiler du code sur du code existant. Si une modification est nécessaire, réécrire le fichier complet de A à Z. Zéro patch, zéro commentaire "// TODO", zéro code mort laissé en place. Chaque fichier doit être lisible et autonome à tout moment.

## 1. OBJECTIF DU PROJET

Construire un pipeline CLI Python semi-automatisé qui produit un Reel Instagram complet (25-30 secondes) pour le compte @curio.education en moins de 30 minutes, avec validation humaine à chaque étape critique.

Stack :
* Python 3.10+
* OpenAI API (GPT Image 2 pour les images, Whisper pour les sous-titres)
* ElevenLabs API (audio voix Curio 8)
* Anthropic API (génération de scripts et prompts)
* FFmpeg (montage vidéo local, gratuit)
* Seedance 2.0 / Dreamina (hook animé — manuel, pas d'API)

Coût cible : < 1,10 € par Reel — Temps cible : < 30 minutes par Reel — Fréquence cible : 6 Reels/semaine

## 2. DEUX TYPES DE CONTENUS

Type A — Curiosité du jour
* Fréquence : 4/semaine (lundi, mardi, jeudi, vendredi)
* Durée : 25-30 secondes
* Sujet : fait insolite, anecdote, phénomène scientifique, histoire
* Hook : "Attends... [fait surprenant en question ou affirmation choc]"

Type B — Compétence scolaire
* Fréquence : 2/semaine (mercredi, samedi)
* Durée : 25-30 secondes
* Sujet : règle de maths ou français — niveaux CP, CE1, CE2, CM1, CM2
* Hook : "Attends... tu sais vraiment comment [compétence] ?"
* Source des sujets : data/Competences_Curio.xlsx
    * Colonnes : Matière | Difficulté | Compétence
    * Onglets : CP / CE1 / CE2 / CM1 / CM2

## 3. STRUCTURE D'UN REEL — SÉQUENCE DE MONTAGE EXACTE

```
Hook animé        — Seedance MP4, 4s fixes (généré manuellement, droppé dans output/)
Illustration 1    — PNG GPT Image 2, durée flexible (poids 5)
Clip Curio A      — curio_explication.mp4, 4s fixes
Illustration 2    — PNG GPT Image 2, durée flexible (poids 5)
Clip Curio B      — curio_explication_2.mp4, 4s fixes
Illustration 3    — PNG GPT Image 2, durée flexible (poids 3)
CTA               — curio_cta.mp4, 3s fixes (on saute les 2 premières secondes du clip)
```

Durée totale du reel = durée de l'audio choisi + 0,2s : la vidéo s'arrête quand la voix
s'arrête. Les clips sont fixes (4+4+4+3 = 15s) ; les 3 illustrations se partagent le temps
restant au prorata 5:5:3. Exemple audio 24,3s → illustrations 3,66s / 3,66s / 2,2s.
Le pipeline bloque avec une erreur claire si l'audio est trop court (< ~16,5s).

Règles de montage :
* Format sortie : MP4 1080×1920 (9:16), 30fps, 4-8 Mbps
* Audio : fichier ElevenLabs choisi (v1 ou v2), plaqué sur toute la durée (les clips Curio n'ont pas de piste audio)
* Sous-titres : générés par Whisper depuis le fichier audio, format SRT, rendu ASS : taille police 60px, blanc bold, contour noir épais + ombre légère, sans boîte de fond (aligné sur la référence publiée dans assets/curio_reference/sous titre + safe zone/), position Y = 75% de la hauteur (hors zone UI Instagram — safe zone)
* Transitions : cut sec entre chaque segment (pas de fondu)

## 4. ASSETS À GÉNÉRER PAR REEL

| Asset | Outil | Quantité | Paramètres |
|---|---|---|---|
| Script JSON horodaté | Claude API | 1 | 65-75 mots, segments timecodes, doit correspondre au temps 25-30s |
| Image hook frame | GPT Image 2 | 1 | 1024×1792, standard quality |
| Illustrations structure | GPT Image 2 | 3 | 1024×1792, standard quality |
| Miniature feed | GPT Image 2 | 1 | 1024×1792, high quality |
| Audio voix | ElevenLabs | 2 versions | Curio 8, Eleven v3, ~25-30s |
| Prompt Seedance | Texte généré | 1 | Fichier .txt à copier-coller |
| Sous-titres | Whisper local | 1 | .srt depuis audio validé |
| Montage final | FFmpeg Python | 1 | MP4 9:16 1080p |
| Description Instagram | Claude API | 1 | .txt avec hashtags + mentions |

Total images GPT Image 2 : 5 par Reel (hook + 3 illus + miniature)

## 5. RÈGLES VISUELLES — CHARTE GRAPHIQUE CURIO

Fond obligatoire pour TOUTES les illustrations :

```
Background: clean white French school notebook page, discrete light blue
grid lines forming small squares (Seyès grid style), subtle paper texture,
soft shadow at the bottom of the page, vertical 9:16 social media format.
```

Positionnement de l'illustration sur le fond :

```
Main visual element centered vertically, occupying approximately 65% of
the page surface, styled as a magazine clipping with a fine white border
and soft drop shadow, as if pasted onto the notebook page.
Leave generous empty space at the bottom (30% of height) for future captions.
No text overlays. No subtitles. No watermark.
```

Règle critique sur les illustrations (Type A — Curiosité) :
Les illustrations doivent être 100 % photoréalistes, comme des photos qu'on trouverait sur Wikipédia ou dans un magazine.
* Pas de personnages Curio dans les illustrations (sauf hook et miniature)
* Pas de style cartoon, pas d'illustration stylisée
* Quand une explication nécessite un schéma : flèches + chiffres simples, minimaliste, fond blanc ou transparent — pas de fioritures

Personnage Curio (hook frame uniquement) :

```
Cute blue and white penguin, large expressive eyes, red knitted scarf,
holding a DJI wireless microphone with furry windscreen close to his beak.
Extremely surprised facial expression, eyes wide open, beak partially open.
Direct eye contact with camera. Medium shot from waist up.
Perfectly centered for vertical 9:16 Instagram Reel.
Pixar-quality rendering. Ultra detailed feathers.
Background: [THÉMATIQUE SELON SUJET]
No text. No watermark. Vertical 9:16.
```

Miniature :
La miniature réutilise 1 ou 2 images déjà générées pour le Reel. Elle ajoute uniquement :
* Logo Curio en bas à droite (fichier : assets/logo_curio.png)
* Titre du Reel en texte blanc bold, positionné dans la zone haute (safe zone)
C'est le seul endroit où le logo Curio apparaît dans les visuels.

## 6. RÉFÉRENCE VISUELLE OBLIGATOIRE

Règle non négociable : chaque génération d'image GPT Image 2 doit inclure les images de référence stockées dans assets/curio_reference/.

```
assets/curio_reference/
├── style_fond_cahier.png        — Exemple fond Seyès validé
├── style_illustration_01.png    — Exemple illustration réaliste validé
├── style_illustration_02.png    — Exemple illustration réaliste validé
├── curio_character_ref.png      — Référence personnage Curio
└── miniature_exemple.png        — Exemple miniature validée
```

Ces fichiers sont passés en input_image (image-to-image) à chaque appel GPT Image 2 pour garantir la cohérence visuelle dans le temps. Sans référence injectée = génération refusée par le pipeline.

Les 5 fichiers canoniques ci-dessus sont des copies des "exemples parfaits" choisis dans l'arborescence de travail de Benjamin (sous-dossiers de assets/curio_reference/ : « frame, image = exemple parfait », « fond blanc, feuille à carreaux », « illustrations avec images intégrés », « miniature parfait »). Pour changer une référence : remplacer le fichier canonique à la racine de curio_reference/. Les sous-dossiers servent de vivier (autres exemples valides) et de documentation de la safe zone / du style de sous-titres.

## 7. PROMPTS IMAGES — TEMPLATES

Les templates exacts vivent dans `prompts/curiosity_prompts.py`, `prompts/competence_prompts.py` et `prompts/seedance_prompts.py`. Ils reprennent mot pour mot les templates du brief v2.0 : fond cahier Seyès, clipping magazine, photoréalisme Type A, exactitude pédagogique stricte Type B (chaque chiffre/mot exact, méthode Éducation Nationale), hook frame Curio, prompt Seedance avec lip-sync.

Backgrounds thématiques selon sujet :

```python
BACKGROUNDS = {
    "sport":      "football stadium at golden hour, French flags, crowd blurred",
    "nature":     "relevant natural environment (fjord, ocean, meadow, etc.)",
    "histoire":   "relevant historical setting, dramatic lighting",
    "maths":      "giant chalkboard with relevant equation, classroom ambiance",
    "science":    "scientific laboratory, colorful liquids, dramatic lighting",
    "transport":  "train station platform, departure board showing SUPPRIMÉ",
    "meteo":      "scorching cityscape, heat shimmer, orange sky",
    "default":    "soft colorful gradient background, neutral and clean",
}
```

## 8. PARAMÈTRES ELEVENLABS — FIXES

```python
ELEVENLABS_CONFIG = {
    "voice_id": "depuis .env (ELEVENLABS_VOICE_ID)",
    "model_id": "eleven_v3",
    "language": "fr",
    "target_duration_seconds": (28, 32),
    "word_count_target": (65, 75),   # ~140 mots/min
    "versions_to_generate": 2,       # Toujours générer v1 et v2
    "output_format": "mp3_44100_128",
}
```

## 9. FLUX D'EXÉCUTION — CHECKPOINTS HUMAINS

```
ÉTAPE 0 — INPUT
  Benjamin saisit : sujet + type + niveau (si compétence)
  Pipeline crée le dossier output/[date]/[slug_sujet]/

  CHECKPOINT 1 — Validation sujet ← Benjamin approuve avant de continuer
  Affiche : script JSON complet + tous les prompts images + prompt Seedance

ÉTAPE 1 — GÉNÉRATION PARALLÈLE (si checkpoint 1 validé)
  Thread A : GPT Image 2 → 5 images (hook + 3 illus + miniature)
  Thread B : ElevenLabs → 2 fichiers audio (v1 + v2)
  Affiche : coût estimé avant lancement + demande confirmation

  CHECKPOINT 2 — Validation visuelle + audio ← Benjamin valide
  Affiche : chemins des 5 images + chemins v1/v2 audio + prompt Seedance txt

ÉTAPE 2 — HOOK ANIMÉ (manuel)
  Pipeline génère : seedance_prompt.txt (à copier-coller dans Dreamina)
  Benjamin génère manuellement le hook MP4 dans Dreamina/Seedance 2.0
  Benjamin dépose le fichier MP4 dans : output/[date]/[slug]/hook_video.mp4

  CHECKPOINT 3 — Confirmation drop MP4 hook + choix audio v1/v2 ← Benjamin

ÉTAPE 3 — MONTAGE (si checkpoint 3 validé)
  Whisper local → sous-titres SRT depuis audio choisi
  FFmpeg → assemblage séquence complète → reel_final.mp4

  CHECKPOINT 4 — Visionnage reel final ← Benjamin valide
  Affiche : chemin MP4 final + description Instagram générée

ÉTAPE 4 — DESCRIPTION
  Claude API → description_instagram.txt
  Pipeline affiche le texte dans le terminal pour relecture

PUBLICATION (manuelle)
  Benjamin publie manuellement sur @curio.education
```

## 10. STRUCTURE DE FICHIERS — OBLIGATOIRE

```
curio-automation/
├── CLAUDE.md                          ← Ce fichier (référence absolue)
├── main.py                            ← CLI point d'entrée
├── config.py                          ← Clés API + constantes globales + helpers partagés
├── requirements.txt
│
├── generators/
│   ├── script_generator.py            ← Claude API → script.json horodaté
│   ├── image_generator.py             ← GPT Image 2 → images PNG avec référence
│   ├── audio_generator.py             ← ElevenLabs → v1 + v2 .mp3
│   ├── subtitle_generator.py          ← Whisper local (CLI) → .srt
│   ├── video_assembler.py             ← FFmpeg → montage final .mp4
│   └── instagram_generator.py         ← Claude API → description .txt
│
├── prompts/
│   ├── curiosity_prompts.py           ← Templates prompts Type A
│   ├── competence_prompts.py          ← Templates prompts Type B (validés prod)
│   └── seedance_prompts.py            ← Template prompt hook animé Seedance
│
├── assets/
│   ├── curio_reference/               ← Références visuelles injectées (PNG)
│   ├── clips/                         ← Clips Curio réutilisables (MP4)
│   │   ├── curio_explication.mp4      ← Curio talking head segment 1 (5s)
│   │   ├── curio_explication_2.mp4    ← Curio talking head segment 2 (5s)
│   │   └── curio_cta.mp4              ← Curio CTA final (4s)
│   └── logo_curio.png                 ← Logo Curio pour miniatures
│
├── data/
│   └── Competences_Curio.xlsx         ← Source sujets Type B
│
└── output/
    └── [YYYY-MM-DD]/
        └── [slug_sujet]/
            ├── script.json
            ├── prompts_all.txt
            ├── seedance_prompt.txt
            ├── hook_frame.png
            ├── illus_1.png
            ├── illus_2.png
            ├── illus_3.png
            ├── miniature.png
            ├── audio_v1.mp3
            ├── audio_v2.mp3
            ├── hook_video.mp4         ← Droppé manuellement par Benjamin
            ├── subtitles.srt
            ├── reel_final.mp4
            ├── description_instagram.txt
            └── api_log.jsonl          ← Log de chaque appel API
```

## 11. INTERFACE CLI — COMMANDES

```bash
# Reel curiosité
python main.py --type curiosite --sujet "dilatation des rails" --date 2026-07-07

# Reel compétence (lire depuis Excel)
python main.py --type competence --niveau CE2 --matiere maths

# Relancer uniquement les images (si déjà un output/)
python main.py --only images --output-dir ./output/2026-07-07/dilatation_rails/

# Relancer uniquement l'audio
python main.py --only audio --output-dir ./output/2026-07-07/dilatation_rails/

# Relancer uniquement le montage (assets déjà présents + hook MP4 droppé)
python main.py --assemble --output-dir ./output/2026-07-07/dilatation_rails/
```

## 12. COÛTS API PAR REEL

| Poste | Outil | Coût estimé |
|---|---|---|
| 5 images standard | GPT Image 2 (0,011$/image) | ~0,055$ |
| 2 audios | ElevenLabs API | ~0,22$ |
| Scripts + prompts | Claude API Sonnet | ~0,04$ |
| Sous-titres | Whisper local | 0$ |
| Montage | FFmpeg local | 0$ |
| Hook animé | Dreamina 10€/mois | ~0,42€ |
| TOTAL | | < 0,80$ + 0,42€ ≈ 1,15€ |

Projection juillet-août (48 reels) : ~55€ total. Si capacité à baisser le prix : good, mais surtout ne pas baisser la qualité du rendu.

## 13. VARIABLES D'ENVIRONNEMENT REQUISES

```bash
# .env (ne jamais committer)
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_VOICE_ID=...
```

## 14. DESCRIPTION INSTAGRAM — STRUCTURE FIXE

```
[EMOJI] [ACCROCHE — reformulation du hook]

[DÉVELOPPEMENT — 3 paragraphes courts]

[FAIT CLÉ mis en valeur avec emoji]

👇 [QUESTION D'ENGAGEMENT pour les commentaires]

📩 Envoie CURIO en MP et reçois gratuitement une activité pédagogique
niveau CP-CM2 sur [SUJET].

🔔 Suis Curio pour une nouvelle curiosité chaque jour.

[5 HASHTAGS MAX] - jamais de majuscule
#curio #[SUJET] #curiositédujour #culturegenerale #education
#primaire #apprendreensamusant #[NIVEAU si compétence]

[2-3 MENTIONS STRATÉGIQUES selon sujet]
```

Comptes à mentionner :

```python
MENTIONS = {
    "toujours":   ["@scilabus", "@lumni_off", "@cestpassorcier_off"],
    "science":    ["@cnrsofficial", "@palais_de_la_decouverte"],
    "actualite":  ["@franceinfo", "@bfmtv"],
    "transport":  ["@sncf", "@transilien"],
    "meteo":      ["@meteofrance"],
    "education":  ["@maitressenadege", "@profsdecole"],
    "parents":    ["@parents.fr"],
}
```

## 15. ÉTAT DES PRÉREQUIS (audit du 2026-07-07, soir)

1. Clés API — ✅ testées OK (Anthropic 200, OpenAI 200, ElevenLabs 200)
2. Voice ID ElevenLabs — ✅ voix « Curio 8 » confirmée via API (tier starter)
3. Clips MP4 réutilisables — ✅ copiés dans assets/clips/ (structures 4s, CTA 5s, sans piste audio)
4. Références visuelles — ✅ 5 PNG canoniques copiés depuis les « exemples parfaits »
5. Logo Curio — ✅ assets/logo_curio.png (avatar circulaire détouré, fond transparent)
6. FFmpeg — ✅ 8.1.1 installé (pas de ffprobe sur cette machine)
7. Whisper — ✅ openai-whisper CLI installé (global, Python 3.9 user install)
8. Python — ✅ 3.12.13 via uv, venv dans .venv/
9. Excel compétences — ✅ data/Competences_Curio.xlsx (copié depuis assets/Compétences Curio/, 30 maths + 30 français par niveau)
10. Démarrage — pipeline complet construit, montage validé sur assets synthétiques + clips réels

## 16. RÈGLES DE CODAGE NON NÉGOCIABLES

1. Un fichier = une responsabilité — chaque module fait une seule chose.
2. Coût affiché avant chaque appel API — "Cette étape coûtera ~0,055$. Confirmer ? (o/n)"
3. Checkpoints bloquants — le pipeline s'arrête et attend une saisie à chaque checkpoint.
4. Logging systématique — chaque appel API logué avec : timestamp, coût réel, fichier généré.
5. Gestion d'erreur explicite — si une API échoue, afficher l'erreur claire et proposer retry.
6. Pas de régénération si le fichier existe déjà — vérifier l'existence avant chaque appel.
7. Pas de dépendances inutiles — n'installer que ce qui est strictement nécessaire.
8. Référence visuelle obligatoire — si assets/curio_reference/ est vide, le pipeline bloque et avertit.

Ce fichier est la source de vérité absolue pour Claude Code. En cas de contradiction avec toute autre source, ce fichier prime. Ne pas modifier sans mettre à jour la version en en-tête.
