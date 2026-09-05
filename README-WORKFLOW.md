# Produire un reel Curio — mode d'emploi

Ce document explique comment fabriquer un reel de bout en bout, du sujet au MP4
final. Il s'adresse à quelqu'un qui arrive sur le projet et qui veut en sortir
un lui-même, pas à quelqu'un qui veut comprendre le code.

**Ce qu'on produit** : une vidéo verticale de 55 à 70 secondes, 1080 × 1920,
30 images par seconde. Curio pose une question étonnante, sept plans y répondent,
un appel à l'action ferme. Format Instagram Reels.

**Ce que ça coûte** : environ **0,19 $ par reel** en API, et **~15 minutes**
quand rien ne coince.

---

## Avant de commencer

Une seule chose à installer, une seule à remplir.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd remotion && npm install && cd ..
```

Puis copier `.env.example` en `.env` et y coller les clés :

| Clé | Sert à | Payant |
|---|---|---|
| `OPENAI_API_KEY` | générer les images des plans | oui, ~0,011 $/image |
| `ELEVENLABS_API_KEY` | générer la voix de Curio | oui, ~0,11 $/1000 caractères |
| `PEXELS_API_KEY` | recherche de photos libres (optionnel) | non |
| `ANTHROPIC_API_KEY` | pipeline historique, pas utilisé ici | oui |

**Le `.env` ne part jamais sur GitHub.** Il est dans `.gitignore` et le dépôt
est public. Aucune clé n'est écrite en dur dans le code : tout passe par ce
fichier.

Il faut aussi **Whisper** (transcription, gratuit, tourne en local) et
**FFmpeg** :

```bash
pip install openai-whisper
brew install ffmpeg
```

---

## Les 8 étapes, dans l'ordre

Chaque commande prend le **slug** du reel — un nom court sans accent ni espace,
`mariannes` par exemple. C'est le même d'un bout à l'autre de la chaîne.

### 1. Écrire le sujet

Créer `reels/<slug>.py`. Le plus simple est de copier `reels/mariannes.py` et
de tout remplacer. Ce fichier contient **tout ce qui change d'un reel à
l'autre** :

- **`segments`** — la narration, découpée en neuf morceaux : le hook, sept
  beats, l'appel à l'action. Un morceau = une phrase ou deux.
- **`images`** — un prompt en anglais par plan à générer.
- **`corrections`** — les mots que Whisper écrit de travers (il entend
  « beau délai » pour « Bodélé »).

Les sujets se piochent dans `assets/Banques curiosités.xlsx`, onglet
`Deck (150)`. Chaque ligne donne le fait et trois éléments vérifiés à réutiliser
dans le script.

> **Deux règles d'écriture à ne pas casser.**
> La ponctuation est volontairement hachée — points de suspension, phrases
> courtes. La voix de synthèse la suit de près, et c'est le seul moyen de la
> faire respirer.
> Le premier segment (`00-hook`) doit reprendre **mot pour mot** la phrase que
> Curio dira dans la vidéo du hook, sinon les lèvres ne suivent pas.

### 2. Générer la voix

```bash
.venv/bin/python gen_narration.py <slug>
```

Le coût s'affiche et demande confirmation avant de facturer quoi que ce soit.
Sortie : `assets/<slug>/audio/*.mp3`, un fichier par segment.

Relancer ne refacture rien : un segment déjà sur le disque est laissé tel quel.
Pour en refaire un, supprimer son MP3.

### 3. Relever les durées

```bash
.venv/bin/python build_reel.py <slug> --timings
```

Ça n'écrit aucune vidéo, ça mesure la voix et imprime la durée de chaque plan
en images. **C'est la voix qui commande la vidéo, jamais l'inverse** : chaque
plan dure exactement son segment de narration. C'est ce qui fait que les
changements d'image tombent sur les phrases.

Noter ces chiffres, ils vont à l'étape 6.

### 4. Générer les plans

```bash
.venv/bin/python gen_images.py <slug>
```

Sortie : `assets/<slug>/<nom>.png`. Là encore, coût affiché et confirmation
demandée, et une image déjà là n'est jamais refaite.

### 5. Transcrire

```bash
.venv/bin/python export_mots.py <slug>
```

Gratuit, tourne en local, compte 2 à 3 minutes. Ça produit les sous-titres mot
à mot avec leurs vrais horodatages, corrigés selon le dictionnaire du sujet.

Le script **vérifie son propre travail** : il compte les mots transcrits et les
compare au texte attendu. Sous 70 %, il recommence tout seul avec un modèle plus
lourd. C'est arrivé une fois sur les trois premiers reels — quatre secondes de
narration étaient purement absentes des sous-titres.

Lire ce que la commande affiche : c'est le seul endroit où les fautes de
transcription se voient. Toute erreur se corrige dans `corrections` du fichier
de l'étape 1, puis on relance.

### 6. Le hook animé — la seule étape manuelle

```bash
.venv/bin/python gen_hooks_massif.py      # l'image de départ
.venv/bin/python gen_seedance_massif.py   # le prompt à copier
```

Puis, dans **Dreamina** (abonnement 10 €/mois, pas d'API) :

1. charger `assets/<slug>/hook_frame.png` ;
2. coller le contenu de `assets/<slug>/seedance_prompt.txt` ;
3. générer, télécharger ;
4. **renommer le fichier `hook_video.mp4`** et le déposer dans
   `assets/<slug>/`.

Compter 4 minutes. Si on produit plusieurs reels, faire les hooks **tous
d'un coup au début** : ils ne servent qu'au montage final, tout le reste peut
avancer pendant que Dreamina tourne.

### 7. Monter les plans

D'abord préparer les fichiers pour Remotion :

```bash
.venv/bin/python prep_assets.py <slug>
```

Puis créer `remotion/src/reels/<slug>/index.tsx` — copier celui de `mariannes`
et adapter. C'est là qu'on pose, pour chaque plan : sa durée (étape 3), ses
images, ses textes, et le moment exact où chaque chose apparaît.

**Ces moments se lisent dans les sous-titres**, jamais à l'œil. Le fichier
`remotion/public/reels/<slug>/mots/<segment>.json` donne l'horodatage de chaque
mot ; l'image à laquelle poser un événement, c'est cet horodatage × 30.

Enregistrer ensuite le reel dans `remotion/src/Root.experiments.tsx` — deux
lignes, un import et une balise. **Ne pas l'oublier** : sans ça, les
compositions n'existent pas.

### 8. Rendre et assembler

```bash
.venv/bin/python render_reel.py <slug>          # les 9 plans, ~10 min
.venv/bin/python build_reel.py <slug>           # le montage final
```

Le rendu sort aussi, pour chaque plan, **trois images fixes** — début, milieu,
fin — dans `testing_remotion/<slug>/`. Les regarder : c'est le moyen le plus
rapide de voir qu'un texte déborde ou qu'un plan est vide, sans ouvrir la vidéo.

Pour reprendre un seul plan après correction :

```bash
.venv/bin/python render_reel.py <slug> 04-chiffre
.venv/bin/python build_reel.py <slug>
```

---

## Où sortent les fichiers

| Quoi | Où |
|---|---|
| **Le reel final** | `testing_remotion/<slug>/reel_<slug>.mp4` |
| Les 9 plans séparés | `testing_remotion/<slug>/<slug>-<beat>.mp4` |
| Les images de contrôle | `testing_remotion/<slug>/*_{debut,milieu,fin}.png` |
| La voix | `assets/<slug>/audio/` |
| Les plans générés | `assets/<slug>/*.png` |
| Ce que Remotion consomme | `remotion/public/reels/<slug>/` |

`testing_remotion/` **n'est pas sur GitHub** — les MP4 pèsent 60 Mo pièce.
Tout ce qui s'y trouve est local.

---

## La structure d'un reel

Sept beats entre le hook et l'appel à l'action. Ce n'est pas une contrainte
technique, c'est ce qui fait tenir une minute d'attention :

| # | Beat | Son rôle |
|---|---|---|
| 0 | **Hook** | Curio pose la question absurde. C'est le seul plan filmé. |
| 1 | Reprise | La question reformulée en affirmation. |
| 2 | Deux mondes | Deux images opposées, l'une après l'autre. |
| 3 | Mécanisme | Comment on passe de l'une à l'autre. |
| 4 | **Le chiffre** | Le pic du reel. Un ordre de grandeur qu'on ne peut pas se représenter, rendu visible. |
| 5 | Conséquence | Pourquoi ça compte. |
| 6 | Révélation | D'où ça vient vraiment. |
| 7 | Chute | Une phrase qui retourne le hook. |
| 8 | **CTA** | Toujours le même clip. |

Le beat 4 est celui qui décide de la réussite du reel. Dans le reel Sahara,
c'est un million de camions qui fuient vers l'horizon ; pour les Mariannes,
l'Everest posé au fond de la fosse ; pour le Soleil, 1,3 million de Terres.
**Un nombre écrit ne veut rien dire à un enfant de dix ans — c'est l'étendue qui
doit se voir.**

---

## Ce qu'on ne réécrit jamais

Les plans sont construits à partir de composants existants qui reçoivent leurs
images et leurs textes en paramètres. **Sur les trois derniers reels, un seul
composant neuf a été nécessaire.** Avant d'en écrire un, regarder si l'un de
ceux-ci ne fait pas déjà le travail :

| Composant | Ce qu'il fait |
|---|---|
| `sahara/01-Hook` | Deux plans, une coupe sèche au milieu d'un mouvement de caméra continu |
| `sahara/02-DeuxMondes` | Deux fenêtres qui entrent l'une après l'autre, une mesure sur la ligne qui les sépare |
| `sahara/04-Camions` | Un champ d'objets identiques qui fuit vers l'horizon. **C'est le beat du chiffre.** |
| `sahara/05-DeuxSols` | Diptyque avant/après, avec ou sans |
| `sahara/06-Revelation` | Zoom continu à travers plusieurs échelles |
| `sahara/07-Chute` | Deux plans et la phrase finale en deux moitiés |
| `reels/commun/Proportion` | Une barre dont la hauteur EST la proportion |

Le composant des camions a servi trois sujets différents — camions, Terres,
fermes néerlandaises — en changeant **une image et quatre couleurs**, sans
toucher à sa logique.

---

## Les pièges connus

**Les durées ne se posent jamais à l'œil.** Toujours `build_reel.py --timings`.
Sur le premier reel produit, les durées estimées à la main s'écartaient jusqu'à
3,1 secondes de la voix.

**Une image manquante ne fait pas d'erreur.** Si un chemin est faux, le plan se
rend quand même, sans sous-titre ou sans image, sans le moindre message. D'où
les images fixes de contrôle : c'est le seul filet.

**Un texte long déborde du cadre.** Un libellé de plus de vingt caractères à
côté d'un élément large sort de l'écran par la droite. Vérifier sur l'image de
contrôle.

**Le rendu 3D exige un drapeau.** `render_reel.py` passe `--gl=angle` tout seul.
Sans lui, aucun plan en trois dimensions ne se rend sur Mac.

**Ne jamais monter la piste audio d'un clip de Curio.** Une seule voix porte le
reel du premier au dernier plan, celle générée à l'étape 2. Les vidéos de
Dreamina ont leur propre bande-son : elle est systématiquement jetée au montage.

---

## Produire plusieurs reels à la suite

L'ordre qui fait gagner le plus de temps :

1. écrire les trois sujets (étape 1) ;
2. générer les trois images de hook et les trois prompts, **lancer les trois
   Dreamina d'un coup** (étape 6) ;
3. dérouler les étapes 2 à 8 sur chaque reel pendant que Dreamina travaille.

Le hook ne sert qu'au tout dernier montage : rien n'attend après lui.

**Repère de temps**, mesuré sur les trois reels du 3 septembre 2026 :

| | Durée | Pourquoi |
|---|---|---|
| Premier reel d'une série | 34 min | il porte l'outillage et les composants neufs |
| Reel suivant, tout réutilisé | **15 min** | c'est le régime de croisière |
| Reel avec un incident à corriger | 28 min | une transcription ratée, un texte qui déborde |

Sur ces 15 minutes, une dizaine est du rendu qui tourne sans surveillance. C'est
le poste le plus lourd et le seul qui ne dépende plus de l'écriture.

---

## Coût détaillé

Relevé sur trois reels complets, le 3 septembre 2026.

| Poste | Par reel | Payant |
|---|---|---|
| Voix (ElevenLabs) | ~0,09 $ | oui |
| Plans, 7 à 8 images (GPT Image 2) | ~0,08 $ | oui |
| Image de départ du hook | ~0,011 $ | oui |
| Sous-titres (Whisper) | 0 $ | non, tourne en local |
| Rendu vidéo (Remotion, FFmpeg) | 0 $ | non, tourne en local |
| Photos libres (Pexels, Wikimedia) | 0 $ | non |
| Hook animé (Dreamina) | ~0,42 € | abonnement 10 €/mois |

**Total : ~0,19 $ + ~0,42 € par reel.**

Un reel qu'on reprend ne recoûte rien : voix et images déjà sur le disque ne
sont jamais regénérées. Seuls les rendus sont refaits, et ils sont gratuits.

---

## Si un clone ne rend rien

Les fichiers lourds ne sont pas tous sur GitHub. Pour remettre un reel en état :

```bash
.venv/bin/python prep_assets.py <slug>   # remet les clips de Curio en place
```

Si des plans manquent aussi, `gen_images.py <slug>` les refait pour ~0,08 $.
Les sources brutes de GPT Image 2 (58 Mo pour trois reels) sont volontairement
absentes du dépôt ; les versions dont Remotion se sert, elles, y sont.
