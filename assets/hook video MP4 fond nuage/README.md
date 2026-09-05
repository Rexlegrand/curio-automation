# Hook « Attends » — fond nuage violet

Hook générique réutilisable sur tous les reels : Curio ne dit plus le sujet du
jour, seulement « Attends ». Le décor est FIXE (mur nuage violet), jamais dérivé
de `hook_background` comme le hook Type A du pipeline — donc zéro génération
d'image et zéro passage Dreamina par reel.

Prompts source (frames ChatGPT + les deux animations Seedance) :
`prompts/hook_attends_reutilisable.md`.

## Deux décors

| Décor | Frame | À quoi il ressemble |
|---|---|---|
| `neon` | `hook_attends_frame_neon.png` | mur lavande soutenu, nuages 3D en relief, enseigne néon `curio.education` au-dessus de la tête |
| `soft` | `hook_attends_frame_soft.png` | même personnage, fond rose-lavande plus clair, nuages plus discrets, **sans enseigne** |

Les deux frames sont aussi copiées dans `assets/hook_frames/`
(`hook_attends_neon.png`, `hook_attends_soft.png`), là où le pipeline va
chercher les hook frames fixes.

## Deux animations, pour chaque décor

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

Les quatre MP4 sortent de Dreamina en 720×1280 à 24,15 fps — à agrandir et
recadencer au montage, comme les autres hooks Seedance.

## Contrôles faits à la réception (05/09)

- Les deux versions `silence` sont bien muettes après le mot : RMS −64,6 dB
  (neon) et −64,3 dB (soft) après 1,6 s, contre −20,5 et −23,8 dB sur les
  versions `blabla`. Bec fermé à l'image de 0,5 s jusqu'à la fin. C'était le
  point à risque du prompt.
- Le micro DJI ne remonte jamais devant le bec sur aucun des quatre clips.

## Défaut connu — push-in

Les quatre clips font un léger zoom avant du début à la fin, malgré la consigne
`absolutely locked static camera`. Sans conséquence pour l'usage prévu (on coupe
vers 2 s), mais ces clips ne bouclent pas et ne se remontent pas dans un ordre
arbitraire comme `assets/clips/curio_explication*.mp4`.

## Usage au montage

La piste audio de ces clips n'est jamais mappée (§3 et v2.15 `CLAUDE.md`) : le
« Attends » qu'on entend vient toujours d'ElevenLabs, celui du clip ne sert qu'à
faire bouger les lèvres au bon moment.
