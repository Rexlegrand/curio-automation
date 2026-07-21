CURIO AUTOMATION — CLAUDE CODE BRIEF
Version : 2.7 — Fix v2.6 : une opération n'a qu'un seul résultat, donc 3 illustrations identiques par reel étaient un bug. Opérations posées : révélation progressive (stage 1/2/3 par renderer). Astuce_chaine : operation_data devient 3 frames (principe + 2 exemples chiffrés différents), une image par frame. Hérite v2.6 (moteur de rendu code maths, 0€, 0 hallucination) et v2.5 (thèmes "velo"/"combat", sous-titres 1 phrase/écran, miniature safe-zone 4:3, durée 28-35s, CTA alterné 50-50, anti-digression).
Modèle cible : Claude-fable 5 (ou équivalent le plus puissant disponible)
Rédigé par : Benjamin Petry—Hummel — Juillet 2026

RÈGLE ABSOLUE N°1 — STRUCTURE DU CODE
Ne jamais empiler du code sur du code existant. Si une modification est nécessaire, réécrire le fichier complet de A à Z. Zéro patch, zéro commentaire "// TODO", zéro code mort laissé en place. Chaque fichier doit être lisible et autonome à tout moment.

## 1. OBJECTIF DU PROJET

Construire un pipeline CLI Python semi-automatisé qui produit un Reel Instagram complet (28-35 secondes) pour le compte @curio.education en moins de 30 minutes, avec validation humaine à chaque étape critique.

Stack :
* Python 3.10+
* OpenAI API (GPT Image 2 pour les images, Whisper pour les sous-titres)
* ElevenLabs API (audio voix Curio 8)
* Anthropic API (génération de scripts et prompts)
* FFmpeg (montage vidéo local, gratuit)
* Pillow (rendu code des opérations posées maths, gratuit — v2.6)
* Seedance 2.0 / Dreamina (hook animé — manuel, pas d'API)

Coût cible : < 1,10 € par Reel — Temps cible : < 30 minutes par Reel — Fréquence cible : 6 Reels/semaine

## 2. DEUX TYPES DE CONTENUS

Type A — Curiosité du jour
* Fréquence : 4/semaine (lundi, mardi, jeudi, vendredi)
* Durée : 28-35 secondes (jamais plus de 35)
* Sujet : fait insolite, anecdote, phénomène scientifique, histoire
* Hook : "Attends... [fait surprenant en question ou affirmation choc]"

Type B — Compétence scolaire
* Fréquence : 2/semaine (mercredi, samedi)
* Durée : 28-35 secondes (jamais plus de 35)
* Sujet : règle de maths ou français — niveaux CP, CE1, CE2, CM1, CM2
* Hook : "Attends... tu sais vraiment comment [compétence] ?"
* Source des sujets : data/Competences_Curio.xlsx
    * Colonnes : Matière | Difficulté | Compétence
    * Onglets : CP / CE1 / CE2 / CM1 / CM2

Règles éditoriales du script (tous types) :
* AUCUNE DIGRESSION : chaque phrase sert le sujet principal. Une info « cousine » du sujet
  (autre règle, autre récompense, anecdote annexe) est exclue — média éducatif, exactitude
  factuelle non négociable (leçon du reel #20 : dossard rouge hors sujet des sanctions).
* Narration : 85-100 mots (la voix eleven_v3 lit ~180 mots/min mesurés → 28-35 secondes).
* CTA alterné 50-50, automatique (l'opposé du dernier reel, forçable via --cta) :
  - « abonnement » : Abonne-toi pour une nouvelle curiosité chaque jour !
  - « commentaire » : Commente CURIO et reçois une activité pédagogique gratuite !
    Le mot-clé est TOUJOURS « CURIO » (jamais un mot lié au sujet), repris dans la description.

## 3. STRUCTURE D'UN REEL — SÉQUENCE DE MONTAGE EXACTE

```
Hook animé        — Seedance MP4, 4s fixes (généré manuellement, droppé dans output/)
Illustration 1    — PNG GPT Image 2 ou rendu code (maths posé), durée flexible (poids 5)
Clip Curio A      — curio_explication.mp4, 4s fixes
Illustration 2    — PNG GPT Image 2 ou rendu code, durée flexible (poids 5)
Clip Curio B      — curio_explication_2.mp4, 4s fixes
Illustration 3    — PNG GPT Image 2 ou rendu code, durée flexible (poids 3)
CTA               — curio_cta.mp4, 3s fixes (on saute les 2 premières secondes du clip)
```

Durée totale du reel = durée de l'audio choisi + 0,2s : la vidéo s'arrête quand la voix
s'arrête. Les clips sont fixes (4+4+4+3 = 15s) ; les 3 illustrations se partagent le temps
restant au prorata 5:5:3. Exemple audio 24,3s → illustrations 3,66s / 3,66s / 2,2s.
Le pipeline bloque avec une erreur claire si l'audio est trop court (< ~16,5s).

Règles de montage :
* Format sortie : MP4 1080×1920 (9:16), 30fps, 4-8 Mbps
* Audio : fichier ElevenLabs choisi (v1 ou v2), plaqué sur toute la durée (les clips Curio n'ont pas de piste audio)
* Sous-titres : Whisper avec timestamps mot à mot, format SRT, rendu ASS : 60px, blanc bold, contour noir épais + ombre légère, sans boîte de fond, baseline ~79% de la hauteur. UNE SEULE PHRASE à l'écran à la fois — « Attends... » s'affiche seul, le reste du hook n'apparaît que quand il est prononcé. Phrases longues coupées en blocs équilibrés de 2 lignes max (28 caractères/ligne), contractions et typographie françaises respectées (qu'il, Abonne-toi, espace avant ? et !)
* Transitions : cut sec entre chaque segment (pas de fondu)

## 4. ASSETS À GÉNÉRER PAR REEL

| Asset | Outil | Quantité | Paramètres |
|---|---|---|---|
| Script JSON horodaté | Claude API | 1 | 85-100 mots, segments timecodes, doit correspondre au temps 28-35s |
| Image hook frame | GPT Image 2 | 1 | 1024×1792, standard quality |
| Illustrations structure | GPT Image 2 **ou rendu code (v2.6)** | 3 | 1024×1792 — code_render si compétence maths avec opération posée/astuce (§7 bis), sinon GPT Image 2 standard quality |
| Miniature feed | GPT Image 2 | 1 | 1024×1792, high quality |
| Audio voix | ElevenLabs | 2 versions | Curio 8, Eleven v3, ~28-35s |
| Prompt Seedance | Texte généré | 1 | Fichier .txt à copier-coller |
| Sous-titres | Whisper local | 1 | .srt depuis audio validé |
| Montage final | FFmpeg Python | 1 | MP4 9:16 1080p |
| Description Instagram | Claude API | 1 | .txt avec hashtags + mentions |

Total images GPT Image 2 : 5 par Reel (hook + 3 illus + miniature), ou 2 par Reel
(hook + miniature) quand les 3 illustrations passent par le rendu code (§7 bis).

## 5. RÈGLES VISUELLES — CHARTE GRAPHIQUE CURIO

Fond obligatoire pour TOUTES les illustrations (GPT Image 2 et rendu code) :

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
La miniature réutilise 1 ou 2 images déjà générées pour le Reel — SAUF si les
illustrations viennent du rendu code (v2.6, §7 bis) : dans ce cas, la miniature
ne réutilise jamais l'illustration à chiffres exacts (risque de chiffre
halluciné par une repasse GPT Image), elle génère un visuel générique maths
sans calcul (voir §7 bis). Elle ajoute uniquement :
* Logo Curio en badge arrondi centré en bas (fichier : assets/logo_curio.png)
* Titre du Reel en lettrage manuscrit bleu foncé, zone haute
C'est le seul endroit où le logo Curio apparaît dans les visuels — y compris
pour les illustrations en rendu code, qui n'ont pas de logo (cohérence avec
le comportement existant des illustrations GPT Image 2, qui n'en ont jamais eu).

RÈGLE FEED 4:3 : le feed Instagram n'affiche que le crop central 4:3 du canvas 9:16.
Titre, photos et logo doivent tenir ENTIÈREMENT dans la zone 4:3 centrale ; les ~20%
haut et bas du canvas restent du fond cahier sans rien d'important.

## 6. RÉFÉRENCE VISUELLE OBLIGATOIRE

Règle non négociable : chaque génération d'image GPT Image 2 doit inclure les images de référence stockées dans assets/curio_reference/. Cette règle ne s'applique qu'aux images GPT Image 2 — le rendu code (§7 bis) ne fait aucun appel API et ne consomme donc aucune référence.

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

Depuis v2.6, `prompts/competence_prompts.py` ne sert plus de template maths à
chiffres exacts (`build_maths_prompt` supprimé, remplacé par le rendu code,
§7 bis) : il ne reste que `build_concept_prompt` (sujets maths sans calcul,
ex. symétrie) et `build_francais_prompt` (inchangé, français toujours GPT Image 2).

Backgrounds thématiques selon sujet :

```python
BACKGROUNDS = {
    "sport":      "football stadium at golden hour, French flags, crowd blurred",
    "combat":     "MMA octagon cage arena at night, dramatic spotlight, blurred cheering crowd",
    "velo":       "Tour de France mountain road at golden hour, cheering crowd waving French flags, blurred peloton",
    "nature":     "relevant natural environment (fjord, ocean, meadow, etc.)",
    "histoire":   "relevant historical setting, dramatic lighting",
    "maths":      "giant chalkboard with relevant equation, classroom ambiance",
    "science":    "scientific laboratory, colorful liquids, dramatic lighting",
    "transport":  "train station platform, departure board showing SUPPRIMÉ",
    "meteo":      "scorching cityscape, heat shimmer, orange sky",
    "default":    "soft colorful gradient background, neutral and clean",
}
```

## 7 bis. MOTEUR DE RENDU CODE — COMPÉTENCES MATHS (v2.6, fix illustrations v2.7)

GPT Image 2 est un modèle génératif : il imite un style, il ne calcule pas.
Pour un contenu pédagogique où l'exactitude du chiffre est non négociable
(division, soustraction avec emprunt, addition avec retenue, multiplication
posée), le risque d'hallucination augmente avec la complexité de l'opération.
**Règle : router selon le type de contenu, pas tout traiter pareil.**

### Trois catégories

| Catégorie | `render_type` | Moteur |
|---|---|---|
| Opération posée classique | `division_posee`, `soustraction_colonnes`, `addition_colonnes`, `multiplication_posee` | Code (0€) |
| Astuce de calcul mental (chaîne d'égalités) | `astuce_chaine` | Code (0€) |
| Concept sans calcul exact (symétrie, fractions en parts, unités) | — | GPT Image 2 |

Le français n'est pas concerné (reste toujours GPT Image 2, prompt inchangé).

### Classification — faite par Claude, dans l'appel script existant

Aucun appel API supplémentaire : `generators/script_generator.py` enrichit le
prompt système Claude (Type B maths uniquement) pour qu'il sorte, dans le même
`script.json`, les champs `image_route` (`code_render`|`gpt_image`),
`render_type` et `operation_data`. Règle de classification donnée à Claude :
opération posée avec retenue/emprunt/potence → `code_render` + le render_type
correspondant ; astuce de calcul mental présentable en chaîne d'égalités →
`code_render` + `astuce_chaine` ; sinon (notion sans calcul chiffré) →
`gpt_image`, `illustrations` rempli avec 3 `description_visuelle`.

`operation_data` selon `render_type` :
* `division_posee` : `{"dividende": int, "diviseur": int}` (diviseur 2 chiffres autorisé seulement niveau CM2)
* `soustraction_colonnes` / `addition_colonnes` : `{"nombre1": int, "nombre2": int}` (nombre1 ≥ nombre2 pour la soustraction)
* `multiplication_posee` : `{"multiplicande": int, "multiplicateur": int}` (multiplicateur à 1 chiffre)
* `astuce_chaine` : `{"titre": str, "frames": [frame_principe, frame_exemple1, frame_exemple2]}`
  — chaque frame = `{"etapes": [str, ...]}`. Le principe peut être en mots
  (pas de chiffre obligatoire) ; les deux exemples doivent être entièrement
  chiffrés et porter sur des nombres DIFFÉRENTS (c'est ce qui prouve que
  l'astuce marche à chaque fois — jamais le même exemple répété).

`generators/script_generator.py` revérifie lui-même chaque `operation_data`
avant d'écrire le script.json : types/contraintes pour les opérations posées
(le résultat est de toute façon recalculé par le renderer, jamais celui de
Claude), et pour `astuce_chaine` — exactitude arithmétique de chaque ligne
chiffrée des frames exemple 1/2 (le principe, en mots, n'est pas vérifiable
et n'a donc rien à vérifier) + contrôle que les deux exemples diffèrent. Si
invalide, le script est régénéré automatiquement (jusqu'à 3 tentatives) avant
tout appel image ou audio.

**Pourquoi 3 illustrations différentes, pas 3 fois la même image (v2.7)** :
une opération posée n'a qu'un seul résultat — `operation_data` reste un seul
jeu de valeurs, jamais 3 opérations différentes (ça augmenterait la surface
d'hallucination). À la place, chaque renderer accepte un paramètre `stage`
(1/2/3) qui révèle l'opération progressivement : stage 1 = opérande posée
seule, stage 2 = étapes/retenues/emprunts intermédiaires, stage 3 = résultat
complet. Pour `astuce_chaine`, le paramètre `stage` sélectionne le frame
(1=principe, 2=exemple 1, 3=exemple 2) — 3 images réellement différentes,
cohérentes avec les 3 segments narratifs du reel (principe / exemple 1 /
exemple 2). `image_generator.py` appelle `renderer(**operation_data, stage=i)`
pour i=1,2,3 lors de la génération des 3 illustrations.

### Checkpoint 1 — veto conservé

Le Checkpoint 1 existant (validation du sujet) affiche désormais aussi, en
clair, `image_route` / `render_type` / `operation_data` — Benjamin voit
« 847 ÷ 4 » écrit noir sur blanc avant que quoi que ce soit ne soit généré.
Zéro friction ajoutée.

### Routage — image_generator.py

```python
if script["image_route"] == "code_render":
    renderer = MATH_RENDERERS[script["render_type"]]          # generators/math_renderers/
    content_img = renderer(**script["operation_data"], stage=i)  # i=1,2,3 : révélation progressive / frame
    compose_illustration(content_img, output_path)              # colle sur le fond cahier Curio
    # coût loggé à 0.0 — zéro appel API
else:
    ...  # comportement GPT Image 2 existant, inchangé
```

Le hook frame et la miniature restent TOUJOURS GPT Image 2 (Curio y apparaît,
pas de calcul à représenter). Quand les illustrations sont en `code_render`,
la miniature ne réutilise jamais l'illustration à chiffres (risque de
hallucination si elle repasse par une génération GPT Image) : elle génère un
visuel générique maths (crayons, règle, ardoise) sans aucun chiffre.

### Rendu visuel

Chaque renderer (`generators/math_renderers/division_posee.py`,
`soustraction_colonnes.py`, `addition_colonnes.py`, `multiplication_posee.py`,
`astuce_chaine.py`) dessine uniquement son contenu (fond transparent) ; les
étapes de calcul (soustractions intermédiaires, retenues, emprunts) sont en
rouge, le résultat final en vert. `generators/math_renderers/compose.py`
colle ce contenu sur `cahier_background.py` (même fond Seyès que GPT Image 2)
avec bordure blanche + ombre portée (style magazine-clip) et une légère
rotation aléatoire -2°/+2° ("collé à la main"). Police : `Patrick Hand`
(assets/fonts/PatrickHand-Regular.ttf, Google Fonts, gratuite) — n'étant pas
une police à chasse fixe, l'alignement en colonnes centre chaque nombre sur
sa colonne plutôt que de le positionner à un x fixe (`draw_col_text`).

## 8. AMÉLIORATION VISUELLE — HÉRITÉ v2.4/v2.6

1. Police manuscrite Patrick Hand intégrée pour le rendu code maths (§7 bis) — DejaVuSansMono abandonné.
2. Pas de logo Curio sur les illustrations en rendu code, cohérent avec les illustrations GPT Image 2 (jamais eu de logo, §5).
3. Légère rotation aléatoire (-2° à +2°) sur toutes les illustrations en rendu code — effet "collé à la main" cohérent avec le style magazine-clip existant.

## 9. COÛT — IMPACT DU RENDU CODE (v2.6)

| Reel | Avant v2.6 | Depuis v2.6 (maths avec opération posée/astuce) |
|---|---|---|
| Images | 5 GPT Image 2 × 0,011$ = 0,055$ | 2 GPT Image 2 (hook + miniature) × 0,011$ = 0,022$ |
| Risque hallucination chiffre | réel | nul sur les illustrations (code_render) |

Reels curiosité, compétence français, et compétence maths "concept sans
calcul" : coût images inchangé (5 × GPT Image 2).

## 10. FLUX D'EXÉCUTION — CHECKPOINTS HUMAINS

```
ÉTAPE 0 — INPUT
  Benjamin saisit : sujet + type + niveau (si compétence)
  Pipeline crée le dossier output/[date]/[slug_sujet]/

  CHECKPOINT 1 — Validation sujet ← Benjamin approuve avant de continuer
  Affiche : script JSON complet + image_route/render_type/operation_data
  (Type B maths) + tous les prompts images + prompt Seedance

ÉTAPE 1 — GÉNÉRATION PARALLÈLE (si checkpoint 1 validé)
  Thread A : GPT Image 2 (et/ou rendu code maths, 0€) → 5 images (hook + 3 illus + miniature)
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

## 11. STRUCTURE DE FICHIERS — OBLIGATOIRE

```
curio-automation/
├── CLAUDE.md                          ← Ce fichier (référence absolue)
├── main.py                            ← CLI point d'entrée
├── config.py                          ← Clés API + constantes globales + helpers partagés
├── requirements.txt
│
├── generators/
│   ├── script_generator.py            ← Claude API → script.json horodaté (+ classification maths v2.6)
│   ├── image_generator.py             ← Routage GPT Image 2 / rendu code (v2.6) → images PNG
│   ├── audio_generator.py             ← ElevenLabs → v1 + v2 .mp3
│   ├── subtitle_generator.py          ← Whisper local (CLI) → .srt
│   ├── video_assembler.py             ← FFmpeg → montage final .mp4
│   ├── instagram_generator.py         ← Claude API → description .txt
│   └── math_renderers/                ← NOUVEAU v2.6 — rendu code opérations maths
│       ├── __init__.py
│       ├── cahier_background.py       ← make_cahier_background(), fond Seyès partagé
│       ├── compose.py                 ← compose_illustration() générique + draw_col_text()
│       ├── division_posee.py          ← potence, diviseur 1-2 chiffres
│       ├── soustraction_colonnes.py   ← emprunt visible
│       ├── addition_colonnes.py       ← retenue visible
│       ├── multiplication_posee.py    ← multiplicande × 1 chiffre
│       └── astuce_chaine.py           ← chaîne d'égalités alignées
│
├── prompts/
│   ├── curiosity_prompts.py           ← Templates prompts Type A (+ variante miniature générique v2.6)
│   ├── competence_prompts.py          ← Type B : concept maths sans calcul + français (validés prod)
│   └── seedance_prompts.py            ← Template prompt hook animé Seedance
│
├── assets/
│   ├── curio_reference/               ← Références visuelles injectées (PNG)
│   ├── clips/                         ← Clips Curio réutilisables (MP4)
│   │   ├── curio_explication.mp4      ← Curio talking head segment 1 (5s)
│   │   ├── curio_explication_2.mp4    ← Curio talking head segment 2 (5s)
│   │   └── curio_cta.mp4              ← Curio CTA final (4s)
│   ├── fonts/
│   │   └── PatrickHand-Regular.ttf    ← NOUVEAU v2.6 — police manuscrite rendu code (Google Fonts)
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
            └── api_log.jsonl          ← Log de chaque appel API (0.0 pour code_render)
```

## 12. INTERFACE CLI — COMMANDES

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

## 13. COÛTS API PAR REEL

| Poste | Outil | Coût estimé |
|---|---|---|
| Images (curiosité / français / maths concept) | GPT Image 2 (0,011$/image × 5) | ~0,055$ |
| Images (maths opération posée/astuce, v2.6) | GPT Image 2 (hook+miniature) + rendu code (3 illus, 0€) | ~0,022$ |
| 2 audios | ElevenLabs API | ~0,22$ |
| Scripts + prompts | Claude API Sonnet | ~0,04$ |
| Sous-titres | Whisper local | 0$ |
| Montage | FFmpeg local | 0$ |
| Hook animé | Dreamina 10€/mois | ~0,42€ |
| TOTAL | | < 0,80$ + 0,42€ ≈ 1,15€ (≤ 0,75€ pour un reel maths opération posée) |

Projection juillet-août (48 reels) : ~55€ total. Si capacité à baisser le prix : good, mais surtout ne pas baisser la qualité du rendu.

## 14. VARIABLES D'ENVIRONNEMENT REQUISES

```bash
# .env (ne jamais committer)
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_VOICE_ID=...
```

## 15. DESCRIPTION INSTAGRAM — STRUCTURE FIXE

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

## 16. ÉTAT DES PRÉREQUIS (audit du 2026-07-21, v2.7)

1. Clés API — ✅ testées OK (Anthropic 200, OpenAI 200, ElevenLabs 200)
2. Voice ID ElevenLabs — ✅ voix « Curio 8 » confirmée via API (tier starter)
3. Clips MP4 réutilisables — ✅ copiés dans assets/clips/ (structures 4s, CTA 5s, sans piste audio)
4. Références visuelles — ✅ 5 PNG canoniques copiés depuis les « exemples parfaits »
5. Logo Curio — ✅ assets/logo_curio.png (avatar circulaire détouré, fond transparent)
6. Police Patrick Hand — ✅ assets/fonts/PatrickHand-Regular.ttf (v2.6)
7. FFmpeg — ✅ 8.1.1 installé (pas de ffprobe sur cette machine)
8. Whisper — ✅ openai-whisper CLI installé (global, Python 3.9 user install)
9. Pillow — ✅ installé dans .venv (v2.6, requis par generators/math_renderers/)
10. Python — ✅ 3.12.13 via uv, venv dans .venv/
11. Excel compétences — ✅ data/Competences_Curio.xlsx (30 maths + 30 français par niveau)
12. Démarrage — pipeline complet construit, montage validé sur assets synthétiques + clips réels, moteur de rendu code maths validé sur division/soustraction/addition/multiplication/astuce

## 17. RÈGLES DE CODAGE NON NÉGOCIABLES

1. Un fichier = une responsabilité — chaque module fait une seule chose.
2. Coût affiché avant chaque appel API — "Cette étape coûtera ~0,055$. Confirmer ? (o/n)"
3. Checkpoints bloquants — le pipeline s'arrête et attend une saisie à chaque checkpoint.
4. Logging systématique — chaque appel API logué avec : timestamp, coût réel, fichier généré (0.0 pour le rendu code).
5. Gestion d'erreur explicite — si une API échoue, afficher l'erreur claire et proposer retry.
6. Pas de régénération si le fichier existe déjà — vérifier l'existence avant chaque appel.
7. Pas de dépendances inutiles — n'installer que ce qui est strictement nécessaire.
8. Référence visuelle obligatoire — si assets/curio_reference/ est vide, le pipeline bloque et avertit (illustrations GPT Image 2 uniquement — sans objet pour le rendu code).
9. Aucun chiffre de compétence maths sans vérification — un render_type d'opération posée ne fait jamais confiance au résultat de Claude, il est recalculé par le code (§7 bis).

Ce fichier est la source de vérité absolue pour Claude Code. En cas de contradiction avec toute autre source, ce fichier prime. Ne pas modifier sans mettre à jour la version en en-tête.
