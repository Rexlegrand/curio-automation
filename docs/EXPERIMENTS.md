# Chantiers expérimentaux — motion design & format « deux carrés »

> **Ce document décrit une piste OPTIONNELLE.**
> Rien ici n'est nécessaire pour faire tourner le pipeline de production.
> Un clone du repo, un `npm install` dans `remotion/` et un `.env` rempli
> suffisent à générer des reels comme d'habitude — voir `CLAUDE.md`, qui reste
> la source de vérité du pipeline. Ce fichier documente ce qui a été testé
> **à côté**, pour ne pas le perdre, et pour que quelqu'un qui installe le
> projet puisse choisir d'y toucher ou non.

Dernière mise à jour : 2026-08-31.

---

## 1. Séparation production / expérimentations (à lire en premier)

Le projet Remotion a désormais **deux points d'entrée distincts** :

| Entrée | Root | Contenu | Utilisé par |
|---|---|---|---|
| `src/index.ts` | `Root.tsx` | `TikTokCaptions` uniquement | le pipeline (`generators/video_assembler.py`) |
| `src/index.experiments.ts` | `Root.experiments.tsx` | prototypes, techniques de caméra, scènes Vox | personne, uniquement manuel |

```bash
cd remotion

# Production — ce que le pipeline appelle tout seul
npx remotion compositions src/index.ts

# Expérimentations — studio interactif
npx remotion studio src/index.experiments.ts

# Expérimentations — rendu d'une composition précise
npx remotion render src/index.experiments.ts VoxLayeredScene2D-v2 sortie.mp4
```

### Pourquoi cette séparation

Avant, `Root.tsx` enregistrait tous les prototypes et importait
`browser-search-cta/` et les cinq `curio-motion/`, qui sont volontairement
**non versionnés**. Conséquence : sur un clone neuf, le bundle Remotion ne
compilait pas, donc `_render_captions_overlay()` échouait, donc **plus aucun
reel ne pouvait être monté**. Un chantier expérimental cassait la production.

Règle qui en découle, à ne pas enfreindre :

> `Root.tsx` ne doit importer que des modules versionnés et des dépendances
> non optionnelles. Tout nouveau prototype va dans `Root.experiments.tsx`.

### Dépendances 3D optionnelles

`three`, `@react-three/fiber`, `@react-three/drei` et `@remotion/three` sont
déclarés en **`devDependencies`**. Ils ne servent qu'à une seule composition
expérimentale (`VoxLayeredScene3D`) et ne sont jamais chargés par la production.

```bash
npm install               # installe tout, expérimentations comprises
npm install --omit=dev    # installation minimale, production uniquement
```

Après une installation `--omit=dev`, retirer l'import de `VoxLayeredScene3D`
dans `Root.experiments.tsx` — la production, elle, n'est pas concernée.

> **Ne jamais utiliser `npm install --omit=optional` ici.** Remotion est
> configuré sur le bundler rspack (`Config.setRspack(true)`), et rspack livre
> son binaire natif en `optionalDependencies`. L'omettre casse le bundler,
> donc l'incrustation des sous-titres, donc tout le montage — vérifié sur un
> clone neuf. C'est pour cette raison que les libs 3D sont en
> `devDependencies` et non en `optionalDependencies`.

---

## 2. Règle motion design corrigée (v2.21 de `CLAUDE.md`)

Constaté sur le reel désert de sel / Uyuni du 26/08 : un beat entier de 10 s
(silhouette qui marche) n'avait reçu qu'une seule technique de caméra — un
Ken Burns sur une photo plate. Résultat : aucun vrai motion design, juste un
zoom lent sur une image figée.

**Cause racine** : les images sourcées (Pexels / Wikimedia) sont des photos
composites plates, le sujet est déjà fondu dans le décor. Sans couches
séparées, aucune technique de personnage, d'objet ou de reveal n'est possible —
il ne reste que la caméra. D'où la dérive « caméra seule = motion design ».

**Règle corrigée**, appliquée dans `CLAUDE.md` §10 et `motion-catalog.md`
(règles 6 et 7) :

1. Une technique de la catégorie 1 (caméra / cadrage) ne peut **jamais**
   constituer à elle seule l'assignation d'un beat. Elle doit toujours être
   combinée à au moins une technique hors catégorie 1. La caméra est un
   modifier, pas une technique autosuffisante.
2. Quand un beat appelle une technique des catégories 2, 5 ou 6 (reveal,
   personnage, objet), le sourcing d'images doit chercher des **assets
   décomposables** — requête fond seul + requête sujet isolable, puis
   détourage — sur le modèle de `hyperframes-test/assets/backgrounds/` +
   `assets/cutouts/` (PNG alpha), et non une photo composite unique.

### Segmentation du reel Uyuni (exemple de référence)

| Timecode | Beat | Type | Technique |
|---|---|---|---|
| 0,0-1,1 | « Attends... » | HOOK | — (hors règle) |
| 1,1-4,6 | « un désert où le ciel touche le sol » | FAIT | Ken Burns zoom-in |
| 5,1-10,8 | « la pluie transforme le sol en miroir » | CAUSE-EFFET | Before/after slide |
| 11,3-15,5 | « le ciel se reflète parfaitement » | COMPARAISON | Pan vertical |
| 16,0-20,1 | « impossible de dire où finit la terre » | RÉVÉLATION | Dolly zoom (vertigo) |
| 21,0-27,8 | « en Bolivie, le Salar d'Uyuni » | DÉFINITION + STAT | Zoom monde → pays → ville |
| 28,2-32,7 | « un seul jour de pluie suffit » | CONCLUSION | Text mask |

Seul le beat RÉVÉLATION exigeait un asset décomposé qu'on n'avait pas (fond
miroir sans personnage + silhouette détourée). Les autres étaient traitables
avec l'existant.

---

## 3. Direction motion design retenue — `Curio-CameraJourney`

`remotion/src/curio-motion/03-CameraJourney.tsx` (composition
`Curio-CameraJourney`, ~11,3 s) : la caméra se déplace sur une grande surface
quadrillée où des photos sont « collées » façon clip magazine, puis un dézoom
final révèle la fresque entière.

C'est la direction retenue par Benjamin parmi cinq prototypes testés. **Les
quatre autres restent en local, non versionnés** — les enregistrer dans
`Root.experiments.tsx` casserait le build sur un clone neuf.

Dépendances : `curio-motion/shared.tsx` (fond Seyès, photo collée, mascotte) et
quatre photos dans `remotion/public/curio_motion/`. Le sous-dossier
`test_manchot_20260820/` (6 Mo) n'est utilisé par aucune composition et reste
hors du repo.

Durée actuelle ~11,3 s, un peu longue face à la cible de 5-10 s : les
constantes `HOLD` / `TRAVEL` en tête de fichier permettent de la réduire.

---

## 4. Compositions de techniques de caméra

`remotion/src/camera-techniques/` — une composition autonome et paramétrable
par technique du `motion-catalog.md`, pour tester une technique isolément
avant de l'intégrer à un reel.

| Fichier | Composition | Catégorie du catalogue |
|---|---|---|
| `KenBurnsZoomIn.tsx` | `CameraTechnique-KenBurnsZoomIn` | 1 — caméra |
| `PanVertical.tsx` | `CameraTechnique-PanVertical` | 1 — caméra |
| `DollyZoomVertigo.tsx` | `CameraTechnique-DollyZoomVertigo` | 1 — caméra |
| `BeforeAfterSlide.tsx` | `CameraTechnique-BeforeAfterSlide` | 4 — comparaison |
| `TextMaskReveal.tsx` | `CameraTechnique-TextMaskReveal` | 3 — typographie |

Le dolly zoom est une approximation CSS : le sujet grossit pendant que le cadre
englobant rétrécit à l'inverse, plus une vignette qui se creuse. C'est le
déséquilibre entre « le sujet ne change pas de taille » et « tout autour se
déforme » qui donne le vertige — pas une vraie perspective changeante.

---

## 5. Scènes « Vox » en couches

Reproduction de la scène ouvrante de *How I Fully Automated Video Editing with
Claude Opus 5* (Ryan, YouTube). Trois versions, gardées pour comparaison :

| Fichier | Composition | Approche |
|---|---|---|
| `vox-test/VoxLayeredScene.tsx` | `VoxLayeredScene` | 2D CSS/SVG, premier jet 9:16 |
| `vox-test/VoxLayeredScene3D.tsx` | `VoxLayeredScene3D` | vrai 3D Three.js (nécessite les deps optionnelles) |
| `vox-test/VoxLayeredScene2D_v2.tsx` | `VoxLayeredScene2D-v2` | **version retenue**, 2D en couches, recalée sur la référence |

### Enseignement principal

La référence n'est **pas** de la 3D. Son effet « 3D layered » vient uniquement
de l'empilement de couches plates et de leur chevauchement. Le détour par
Three.js s'est éloigné du rendu visé ; la version retenue est revenue au 2D.

Ce que la version retenue reproduit fidèlement :

- scène dans une **card arrondie**, à côté d'une seconde card (le talking head),
  et non en plein cadre ;
- objets du midground **posés sur la balustrade** et tirés du monde réel
  (graphique en barres, écran, éolienne), pas des primitives abstraites
  flottantes ;
- **burst d'étincelles** dorées à chaque apparition d'objet ;
- **tangage latéral** de chaque bande de décor : amplitude croissante vers
  l'avant (rayons 5 px → soleil 8 → nuage 12 → collines 16 et 24 → poutre et
  objets 34 → premier plan 46) et phases alternées (0 / π) d'une bande à
  l'autre. C'est ce décalage qui crée la profondeur. Les bandes pleine largeur
  sont dessinées 90 px plus large de chaque côté pour ne jamais découvrir un
  bord pendant le mouvement.

---

## 6. Format « deux carrés » (chantier ouvert)

Format repéré sur les Shorts de la même chaîne : l'écran est coupé en deux
cartes arrondies empilées — Curio qui parle en haut, illustration ou motion
design du sujet en bas — en alternance avec des plans pleine largeur, avec un
changement de structure toutes les ~3 secondes.

### Structure visée

```
0,0  → 4,1    hook Curio plein écran (inchangé)
4,1  → 33,3   corps : blocs de ~2,9 s, alternance plein écran / deux carrés
33,3 → 37,4   CTA (inchangé)
```

### Preuve de concept

`test_deux_carres_manchot.py` (racine du repo) remonte un reel **déjà terminé**
au nouveau format, sans jamais écrire dans `output/` : l'original reste intact,
le rendu part dans `testing_remotion/`.

```bash
source .venv/bin/activate
python3 test_deux_carres_manchot.py
```

Validé sur `output/2026-08-20/le_manchot_empereur_qui_jeune_deux_mois_pour_son_uf/`.

Géométrie retenue, calée sur la référence : deux cartes de 940×855, rayon 36,
centrées horizontalement (x = 70), la première à y = 80, la seconde à y = 985 —
marges haute et basse symétriques de 80 px. Les sous-titres (baseline 79 %)
tombent naturellement dans la carte du bas, donc **aucun réglage à changer côté
Remotion** : c'est le même composant `TikTokCaptions` que la production.

### Asset Curio réutilisable

Le clip Curio est un asset **générique**, généré une fois et réutilisé sur tous
les reels. Prompts complets (GPT Image 2 pour l'image, Seedance 2.0 pour
l'animation) dans `prompts/curio_talking_head_reusable.md`.

Deux points qui font tout marcher :

- **Le micro couvre le bec.** Le spectateur ne voit pas les mouvements de bec,
  donc l'animation n'a pas besoin d'être synchronisée avec la voix ElevenLabs.
  Un seul clip sert pour n'importe quel script.
- **Caméra verrouillée, lumière constante, pose de repos identique au début et
  à la fin.** Le clip est découpé en segments de 2-3 s remontés dans un ordre
  arbitraire ; tout mouvement directionnel produirait un saut visible à chaque
  raccord.

Le script pioche cinq fenêtres différentes du clip de 10 s (offsets 0 / 2,4 /
4,8 / 7,1 / 1,2 s) plutôt que de boucler, pour que la répétition ne se voie pas.

### Ce qui reste à faire

Le pipeline n'est **pas** modifié : `config.py` (`TIMELINE`) et
`generators/video_assembler.py` produisent toujours l'ancien format. Passer le
format « deux carrés » en production suppose de réécrire ces deux fichiers et
de mettre à jour §3 de `CLAUDE.md`. Décision non prise à ce jour.

---

## 7. Dépendances système (hors repo)

Découvert en installant le plugin `watch` (analyse de vidéos de référence) :

- **`ffprobe` était absent** de la machine alors que `ffmpeg` était présent
  (build statique `/usr/local/bin/ffmpeg`, 8.1.1). Installé via Homebrew et
  exposé dans `/opt/homebrew/bin/ffprobe`. Attention : un `brew link ffmpeg`
  complet remplacerait `ffmpeg` par la 9.0.1, qui a **supprimé l'option
  `-vsync`** — à éviter tant que du code en dépend.
- **`yt-dlp` de 2025 cassé** par un changement d'API YouTube
  (« The page needs to be reloaded »). Remplacé par la version Homebrew.

Ces points ne concernent pas le pipeline de production, qui n'utilise ni
`ffprobe` ni `yt-dlp`.

---

## 8. Fichiers volontairement non versionnés

| Chemin | Raison |
|---|---|
| `references/` | vidéos de référence — voir §9 |
| `remotion/src/curio-motion/` sauf `03-CameraJourney.tsx` + `shared.tsx` | 4 des 5 prototypes restent locaux ; seule la direction retenue est versionnée |
| `remotion/src/browser-search-cta/` | CTA du projet ads Meta, autre projet |
| `hyperframes-test/`, `.agents/`, `agent/` | bacs à sable et caches d'outils externes |
| `testing_remotion/` | tous les rendus de test |

Ces chemins sont dans `.gitignore`. Ne pas les enregistrer dans
`Root.experiments.tsx` : un clone neuf ne compilerait plus.

---

## 9. Vidéos de référence (`references/`, non versionné)

Le dossier `references/motion-examples/` sert de matière de travail : ce sont
les montages dont on s'inspire, analysés image par image via le plugin `watch`.

**Il n'est volontairement pas commité**, pour deux raisons :

- ~250 Mo dont un fichier de 77 Mo. GitHub avertit au-delà de 50 Mo et bloque à
  100 Mo par fichier. Surtout, ces octets entreraient **définitivement dans
  l'historique Git** : même supprimés plus tard, chaque clone continuerait à les
  télécharger.
- Ce sont des contenus tiers (reels d'autres créateurs, vidéos YouTube)
  téléchargés comme référence. Les republier sur un dépôt partagé serait de la
  redistribution.

Les sources sont donc listées ici pour que l'information reste dans le repo,
sans les fichiers. Pour retrouver la matière, retélécharger depuis la source.

### Sources identifiées

| Fichier local | Source |
|---|---|
| `dreamina-…-Animate this exact image….mp4` | généré via Dreamina à partir du prompt de `prompts/curio_talking_head_reusable.md` |
| `Screen Recording 2026-08-28 at 4.46.32 pm.mov` | capture d'écran locale de la scène Vox de la vidéo YouTube ci-dessous |
| `ScreenRecording_08-26-2026 19-*.MP4` | captures d'écran locales (Benjamin) |
| `cartora_reliefs_*.mp4` | reel Instagram — compte `@cartora_reliefs` |
| `cesar_cultureg_*.mp4` | reel Instagram — compte `@cesar_cultureg` |
| `geoglobe_tales_*.mp4` (×2) | reels Instagram — compte `@geoglobe_tales` |
| `laminutegeographie_*.mp4` | reel Instagram — compte `@laminutegeographie` |

Les noms de fichiers Instagram conservent le handle du compte et les
identifiants média d'origine, ce qui permet de les retrouver.

### Références YouTube (URLs stables)

| Vidéo | URL | Ce qu'on en a tiré |
|---|---|---|
| *How I Fully Automated Video Editing with Claude Opus 5* — Ryen, 9 min 15 | https://youtu.be/rjLuHtvrmMo | la scène Vox en couches (§5) et le brief exact lu à 3:08-3:34 |
| *How My AI Agent Gets Leads with Content* — même chaîne, Short 50 s | https://youtube.com/shorts/ZhOIoat5WDU | le format « deux carrés » (§6) et le rail de 3 icônes calées sur les mots |

### Les relire

Le plugin `watch` (marketplace `bradautomates/claude-video`) télécharge,
extrait des images et récupère la transcription :

```
/watch:watch <url>
```

Il a besoin de `ffmpeg`, `ffprobe` et `yt-dlp` — voir §7.
