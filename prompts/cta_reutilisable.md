# CTA réutilisables — fond nuage violet

Remplace `assets/clips/curio_cta.mp4`, qui vient d'un décor différent de celui
du hook : le reel changeait de monde à sa dernière seconde. Même personnage,
même micro DJI, même mur nuage que le hook « Attends ».

Frames de départ (déjà générées, `assets/hook video MP4 fond nuage/`) :
`hook_attends_frame_neon.png` et `hook_attends_frame_soft.png`.

Deux CTA × deux décors = **4 vidéos**. Les prompts ci-dessous ne mentionnent
jamais l'enseigne : le même prompt tourne sur les deux frames.

| CTA | Phrase | Fichier attendu |
|---|---|---|
| A — MP | « Envoie CURIO en MP pour recevoir un exercice gratuit ! » | `cta_mp_neon.mp4`, `cta_mp_soft.mp4` |
| B — débloquer | « Fais quelques pages d'exercices pour débloquer une nouvelle vidéo ! » | `cta_debloque_neon.mp4`, `cta_debloque_soft.mp4` |

Deux différences avec les prompts du hook, volontaires :
- **Expression** : la frame de départ montre Curio surpris, bouche ouverte. Un
  CTA se dit en souriant — les prompts demandent explicitement que la surprise
  retombe en sourire chaleureux dans la première demi-seconde.
- **Durée 5 s** : les phrases CTA sont plus longues qu'un mot ; à 4 s le
  lip-sync se fait tronquer en fin de phrase. On coupe au montage, jamais
  l'inverse.

Anti-zoom renforcé (`the distance between the camera and the penguin never
changes`) : les quatre clips du hook du 05/09 ont un push-in malgré la consigne
de caméra verrouillée.

Comme partout ailleurs, la piste audio de ces clips n'est jamais montée (§3 et
v2.15 `CLAUDE.md`) : la voix ElevenLabs redit la phrase, le clip ne sert qu'au
lip-sync.

---

## CTA A — « Envoie CURIO en MP »

```
Animate this exact image. Keep the character, the DJI microphone, the cloud
wall and the background EXACTLY as they are in the source image — do not
redesign, do not restyle, do not add or remove any object.

EXPRESSION — starts surprised, becomes warm: in the first half second his
surprised face relaxes into a big warm friendly smile, eyes still bright and
engaged, looking straight into the camera lens. He stays smiling and inviting
for the whole clip. Not shouting, not over-excited — warm and reassuring, like
a host inviting you to write to him.

SPEECH: the blue penguin speaks directly into the camera in French and says:
"Envoie CURIO en MP pour recevoir un exercice gratuit !"
Accurate French lip-sync on every syllable, beak and mouth moving naturally,
finishing the sentence well before the end of the clip.

GESTURE: his free flipper makes one small friendly inviting gesture toward the
camera, then comes back to rest. Natural eye blinks, small head nods, very
slight breathing. Nothing else moves.

MICROPHONE: the DJI microphone stays in his flipper next to his beak, at chin
height, and must never rise in front of the beak — the mouth stays fully
visible for the whole clip.

CAMERA: absolutely locked static camera. No zoom, no push-in, no pull-back, no
pan, no tilt, no dolly, no handheld shake. The distance between the camera and
the penguin never changes. The penguin must be exactly the same size in the
last frame as in the first frame.

CONSISTENCY: the character stays centered and never drifts out of his starting
position. Lighting, exposure and colours stay perfectly constant — no flicker,
no colour shift. The background stays completely static. Nothing enters or
leaves the frame. No transition, no cut, no scene change.

9:16 vertical frame, Pixar-quality 3D rendering, cinematic soft lighting.
Duration: 5 seconds. Generate audio.
```

---

## CTA B — « Débloque une nouvelle vidéo »

```
Animate this exact image. Keep the character, the DJI microphone, the cloud
wall and the background EXACTLY as they are in the source image — do not
redesign, do not restyle, do not add or remove any object.

EXPRESSION — starts surprised, becomes warm and playful: in the first half
second his surprised face relaxes into a big warm friendly smile with a
mischievous spark, eyes bright and engaged, looking straight into the camera
lens. He stays smiling and encouraging for the whole clip, like someone
offering a deal. Not shouting, not over-excited.

SPEECH: the blue penguin speaks directly into the camera in French and says:
"Fais quelques pages d'exercices pour débloquer une nouvelle vidéo !"
Accurate French lip-sync on every syllable, beak and mouth moving naturally,
finishing the sentence well before the end of the clip.

GESTURE: his free flipper makes one small encouraging gesture — a light tap
forward in the air, as if counting a couple of pages — then comes back to rest.
Natural eye blinks, one small head tilt, very slight breathing. Nothing else
moves.

MICROPHONE: the DJI microphone stays in his flipper next to his beak, at chin
height, and must never rise in front of the beak — the mouth stays fully
visible for the whole clip.

CAMERA: absolutely locked static camera. No zoom, no push-in, no pull-back, no
pan, no tilt, no dolly, no handheld shake. The distance between the camera and
the penguin never changes. The penguin must be exactly the same size in the
last frame as in the first frame.

CONSISTENCY: the character stays centered and never drifts out of his starting
position. Lighting, exposure and colours stay perfectly constant — no flicker,
no colour shift. The background stays completely static. Nothing enters or
leaves the frame. No transition, no cut, no scene change.

9:16 vertical frame, Pixar-quality 3D rendering, cinematic soft lighting.
Duration: 5 seconds. Generate audio.
```

---

## À la réception

Déposer les 4 MP4 dans `assets/hook video MP4 fond nuage/` sous les noms du
tableau ci-dessus. Contrôle : la phrase est finie avant la fin du clip, le micro
n'est jamais remonté devant le bec, et le sourire est en place dès la seconde 1.

Le CTA B change le texte du pipeline : `CTA_TEXTE` (`config.py`) et `LIGNE_CTA`
(`instagram_generator.py`) portent encore la formule MP unique de la v2.11. À
trancher quand les clips sont validés — le script narré, le clip et la
description Instagram doivent dire la même chose.
