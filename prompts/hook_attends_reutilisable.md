# Hook « Attends » réutilisable — frame + 2 animations Seedance

Asset **générique**, généré une fois, réutilisé sur tous les reels : le hook ne
dit plus le sujet du jour, il ne dit que « Attends ». Le sujet est porté par la
voix ElevenLabs et les sous-titres, jamais par le lip-sync du hook.

Différence avec le hook Type A du pipeline (`prompts/seedance_prompts.py`) :
celui-ci a un fond FIXE (mur lavande à nuages, néon `curio.education`), jamais
dérivé de `hook_background`, et une phrase FIXE. Donc zéro génération d'image
et zéro passage Dreamina par reel une fois les deux MP4 en boîte.

## Décor de référence

`testing_remotion/frame_curio_studio/frame_curio_studio_v2.png` — mur violet
lavande, nuages 3D sculptés en relief, enseigne néon `curio.education` avec ses
deux câbles. Seul changement ici : le micro broadcast sur bras articulé est
remplacé par le petit micro DJI à bonnette fourrure, tenu par Curio (le micro
des hooks Type A), et le bureau en bois disparaît — plan taille, pas assis.

Le micro DJI ne couvre PAS le bec : contrairement au talking head réutilisable
(`curio_talking_head_reusable.md`), on doit ici VOIR les lèvres former
« Attends ». C'est le point clé des deux animations.

---

## 1. Prompt image — GPT Image 2 (`hook_attends_frame.png`)

Joindre en image-to-image : le frame studio ci-dessus (décor) +
`assets/curio_reference/curio_character_ref.png` (personnage canonique).
Format 1024×1792, quality `high` — asset réutilisé partout, pas jetable.

```
IMAGE 1 is the SET to preserve. IMAGE 2 is the CANONICAL character model of
Curio the penguin — the single source of truth for how he must look.

BACKGROUND (from IMAGE 1, keep it exactly): the same lavender-purple studio
wall, the same sculpted 3D clouds floating in relief on the wall, the same
glowing warm neon sign reading "curio.education" with its two hanging cables in
the upper third of the frame. Same soft warm studio lighting, same colour
grading. Do not redesign the wall, do not change the clouds, do not change the
neon text.

REMOVE from IMAGE 1: the wooden desk and the black broadcast microphone on its
boom arm. Nothing replaces the desk — the penguin now stands in front of the
wall, framed from the waist up.

CHARACTER: render the penguin as the EXACT same character as in IMAGE 2, not a
look-alike. Matte, soft, ultra detailed fluffy feathers — no gloss, no plastic
sheen. Royal blue back and head, clean white face and belly, small rounded
orange beak, large round white eyes with bright blue irises, small tuft of
feathers on top of the head, chunky red knitted scarf with fringed ends. Both
blue flippers visible and readable, never melted into the body.

MICROPHONE: a small DJI wireless microphone with a fuzzy grey furry windscreen,
held in his right flipper and raised close to his beak — held BESIDE and
slightly BELOW the beak, at chin height. The microphone must NEVER cover, hide
or overlap the beak: the beak stays fully visible from the camera at all times.

POSE AND EXPRESSION: facing the camera straight on, direct eye contact. Very
surprised expression, eyes wide open, eyebrows raised, beak open mid-word as if
he has just interrupted the viewer to say one word.

FRAMING: vertical 9:16, medium shot from the waist up, penguin centered
horizontally, head in the upper-middle third, the neon sign readable above him.
Nothing important in the bottom 30% of the frame (subtitle safe zone).

Pixar-quality 3D rendering, cinematic soft lighting. No text other than the
existing neon sign. No watermark. No subtitles. Vertical 9:16.
```

---

## 1 bis. Prompt image — variante SANS le néon

Repasser l'image obtenue en section 1 (et elle seule) dans ChatGPT avec :

```
Take this exact image and change ONE thing only: REMOVE the glowing neon sign
reading "curio.education" and REMOVE its two thin hanging cables completely.
The wall behind them becomes plain lavender-purple wall, perfectly clean and
continuous, with the same soft warm lighting and the same subtle vignette — no
leftover glow, no shadow of the sign, no bracket, no cable, no trace of where
it was.

Keep absolutely everything else pixel-identical: the same penguin with the same
pose, the same wide surprised eyes, the same open beak, the same red knitted
scarf, the same DJI microphone with its furry windscreen held in his flipper at
chin height, the same framing and crop, the same sculpted 3D clouds floating in
relief on the wall in the same positions, the same colours and the same
lighting.

The clouds stay exactly where they are — do not move them, do not add new ones,
do not fill the empty upper area with anything.

No text at all in the image. No watermark. No subtitles. Vertical 9:16.
```

Les deux prompts Seedance ci-dessous tournent indifféremment sur la frame avec
ou sans néon : aucun des deux ne mentionne l'enseigne.

---

## 2. Prompt Seedance — VERSION A : « Attends » + blabla

Il dit « Attends », visiblement lisible sur les lèvres, puis continue de parler.
Le reste du texte n'a aucune importance : la piste audio du clip n'est jamais
montée (§3 CLAUDE.md), seule la voix ElevenLabs joue. Ce clip sert quand on veut
garder Curio à l'écran plus longtemps qu'une seconde.

```
Animate this exact image. Keep the character, the DJI microphone, the lavender
cloud wall and the neon sign EXACTLY as they are in the source image — do not
redesign, do not restyle, do not add or remove any object.

SPEECH: the blue penguin speaks directly into the camera in French. He starts
by saying, clearly and with emphasis: "Attends..." — this first word must be
perfectly readable on his beak and lips, wide and articulated, unmistakable.
Then he keeps talking calmly in French for the rest of the clip:
"Attends... tu vas pas me croire, écoute bien ça, franchement c'est fou."
Accurate French lip-sync on every syllable, beak and mouth moving naturally.

EXPRESSION: very surprised on "Attends" — eyes wide open, eyebrows up, head
leaning slightly toward the camera as if interrupting the viewer. Then the
expression softens into a warm, engaged storyteller face, still animated, with
natural eye blinks and small head movements. He always looks straight into the
camera lens.

MICROPHONE: the DJI microphone stays in his flipper next to his beak, at chin
height, and must never rise in front of the beak — the mouth stays fully
visible for the whole clip.

CAMERA: absolutely locked static camera. No zoom, no push-in, no pan, no tilt,
no dolly, no handheld shake. Identical framing from the first to the last frame.

CONSISTENCY: the character stays centered and never drifts out of his starting
position. Lighting, exposure and colours stay perfectly constant — no flicker,
no colour shift. The neon sign stays steadily lit, never blinking. The cloud
wall stays completely static. Nothing enters or leaves the frame. No transition,
no cut, no scene change.

9:16 vertical frame, Pixar-quality 3D rendering, cinematic soft lighting.
Duration: 4 seconds. Generate audio.
```

---

## 3. Prompt Seedance — VERSION B : « Attends » puis silence

Il dit « Attends » sur la première seconde, puis **plus rien** : bec fermé,
idle. C'est la version taillée pour le montage prévu — on garde ~2s à l'image
(le mot + une respiration), on coupe, et le reste du hook se déroule en voix off
sur d'autres plans.

Le point dur côté Seedance : sans consigne explicite, le modèle continue de
faire bouger le bec après le mot. D'où le bloc AFTER THE WORD, volontairement
répétitif.

```
Animate this exact image. Keep the character, the DJI microphone, the lavender
cloud wall and the neon sign EXACTLY as they are in the source image — do not
redesign, do not restyle, do not add or remove any object.

SPEECH — ONE WORD ONLY: during the FIRST SECOND of the clip, the blue penguin
says out loud in French one single word: "Attends". Accurate French lip-sync on
that word only, beak and lips wide and clearly articulated, unmistakably
readable. He says nothing else for the rest of the clip.

AFTER THE WORD (critical): from the second second to the end of the clip, his
beak CLOSES and STAYS CLOSED. No further speech, no mumbling, no talking, no
beak opening, no mouth movement, no lip-sync of any kind. Silence. He simply
holds the pose and looks at the camera, waiting.

IDLE MOTION after the word — subtle only: natural eye blinks at irregular
intervals, very slight breathing, a small head tilt, the red scarf and feathers
reacting slightly to that motion. Nothing else moves.

EXPRESSION: very surprised on "Attends" — eyes wide open, eyebrows up, head
leaning slightly toward the camera. After the word, the surprise stays on his
face, softening only a little, eyes still wide and locked on the camera lens.

MICROPHONE: the DJI microphone stays in his flipper next to his beak, at chin
height, and must never rise in front of the beak — the mouth stays fully
visible for the whole clip.

CAMERA: absolutely locked static camera. No zoom, no push-in, no pan, no tilt,
no dolly, no handheld shake. Identical framing from the first to the last frame.

CONSISTENCY: the character stays centered and never drifts out of his starting
position. Lighting, exposure and colours stay perfectly constant — no flicker,
no colour shift. The neon sign stays steadily lit, never blinking. The cloud
wall stays completely static. Nothing enters or leaves the frame. No transition,
no cut, no scene change.

9:16 vertical frame, Pixar-quality 3D rendering, cinematic soft lighting.
Duration: 4 seconds. Audio: only the single French word "Attends" at the very
beginning, then complete silence. No music, no ambience, no other speech.
```

---

## À la réception des MP4

Tout vit dans `assets/hook video MP4 fond nuage/` (voir le README de ce
dossier) : deux décors (`neon` avec l'enseigne, `soft` sans) × deux animations
(`blabla`, `silence`), soit quatre MP4 de 4,10 s, plus les deux frames.

Contrôle avant de valider : sur les versions `silence`, avancer image par image
après la 1,5 s — si le bec rebouge, régénérer (c'est le seul défaut attendu).
Sur toutes les versions, vérifier que le micro n'est jamais remonté devant le
bec.

Défaut constaté sur les quatre clips du 05/09 : léger push-in malgré
`absolutely locked static camera`. Sans effet sur l'usage prévu (coupe vers
2 s), mais ils ne bouclent pas.

Au montage, la piste audio de ces clips n'est jamais mappée (§3 et v2.15
`CLAUDE.md`) : le « Attends » qu'on entend vient toujours d'ElevenLabs, celui du
clip ne sert qu'à faire bouger les lèvres au bon moment.
