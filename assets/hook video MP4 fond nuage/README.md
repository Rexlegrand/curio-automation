# Curio fond nuage violet — hooks et CTA

Les deux extrémités d'un reel, en clips fixes réutilisables : le hook « Attends »
et les CTA. Curio ne dit plus le sujet du jour, le décor ne dépend plus du sujet
— donc zéro génération d'image et zéro passage Dreamina par reel.

Prompts source : `prompts/hook_attends_reutilisable.md` (frames + hooks) et
`prompts/cta_reutilisable.md` (CTA).

## Deux décors

| Décor | Frame | À quoi il ressemble |
|---|---|---|
| `neon` | `hook_attends_frame_neon.png` | mur lavande soutenu, nuages 3D en relief, enseigne néon `curio.education` au-dessus de la tête |
| `soft` | `hook_attends_frame_soft.png` | même personnage, fond rose-lavande plus clair, nuages plus discrets, **sans enseigne** |

Les deux frames sont aussi copiées dans `assets/hook_frames/`
(`hook_attends_neon.png`, `hook_attends_soft.png`), là où le pipeline va
chercher les hook frames fixes.

## Hooks — deux animations, pour chaque décor

| Fichier | Durée | Ce qu'il fait |
|---|---|---|
| `hook_attends_neon_blabla.mp4` | 4,10 s | « Attends » puis continue de parler jusqu'au bout |
| `hook_attends_neon_silence.mp4` | 4,10 s | « Attends » sur la 1re seconde, puis bec fermé et silence |
| `hook_attends_soft_blabla.mp4` | 4,10 s | idem blabla, décor sans enseigne |
| `hook_attends_soft_silence.mp4` | 4,10 s | idem silence, décor sans enseigne |

La version `blabla` sert quand on veut garder Curio à l'écran plus d'une
seconde ; la version `silence` est celle taillée pour le montage prévu — garder
~2 s (le mot + une respiration), couper, dérouler le reste du hook en voix off
sur d'autres plans.

## CTA — deux messages, pour chaque décor

| Fichier | Phrase dite |
|---|---|
| `cta_mp_neon.mp4` / `cta_mp_soft.mp4` | « Envoie CURIO en MP pour recevoir un exercice gratuit ! » |
| `cta_debloque_neon.mp4` / `cta_debloque_soft.mp4` | « Fais quelques pages d'exercices pour débloquer une nouvelle vidéo ! » |

Ils remplacent `assets/clips/curio_cta.mp4`, qui venait d'un décor différent de
celui du hook : le reel changeait de monde à sa dernière seconde.

Le CTA « débloquer » est un message nouveau, absent du pipeline : `CTA_TEXTE`
(`config.py`) et `LIGNE_CTA` (`instagram_generator.py`) portent encore la
formule MP unique de la v2.11. À trancher — le script narré, le clip et la
description Instagram doivent dire la même chose.

## Format

Les huit MP4 sortent de Dreamina en 720×1280 à 24,15 fps, 4,10 s — à agrandir et
recadencer au montage, comme les autres clips Seedance. Note : les CTA ont été
demandés en 5 s, Dreamina a rendu 4,10 s comme le reste ; les quatre phrases
tiennent quand même, vérifié à la transcription.

## Contrôles faits à la réception (05/09)

- Les deux versions `silence` sont bien muettes après le mot : RMS −64,6 dB
  (neon) et −64,3 dB (soft) après 1,6 s, contre −20,5 et −23,8 dB sur les
  versions `blabla`. Bec fermé à l'image de 0,5 s jusqu'à la fin. C'était le
  point à risque du prompt.
- Les quatre CTA disent bien la phrase attendue et la finissent avant la fin du
  clip (transcrits à la réception — les fichiers Dreamina sortent avec des noms
  interchangeables, c'est la transcription qui les identifie).
- Le micro DJI ne remonte jamais devant le bec sur aucun des huit clips.

## Défaut connu — push-in

Les huit clips font un léger zoom avant du début à la fin, malgré la consigne
`absolutely locked static camera` — y compris les CTA, dont le prompt ajoutait
pourtant `the distance between the camera and the penguin never changes`.
Seedance ne tient pas cette consigne. Sans conséquence pour l'usage prévu (on coupe
vers 2 s), mais ces clips ne bouclent pas et ne se remontent pas dans un ordre
arbitraire comme `assets/clips/curio_explication*.mp4`.

## Usage au montage

La piste audio de ces clips n'est jamais mappée (§3 et v2.15 `CLAUDE.md`) : le
« Attends » qu'on entend vient toujours d'ElevenLabs, celui du clip ne sert qu'à
faire bouger les lèvres au bon moment.
