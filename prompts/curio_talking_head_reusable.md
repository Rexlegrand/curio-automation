# Curio talking head réutilisable — prompt GPT Image 2

Asset **générique**, généré UNE fois, réutilisé sur tous les reels curiosité.
Contrairement au hook frame (dont le fond varie selon le sujet, §7 CLAUDE.md),
celui-ci doit rester neutre : il apparaît dans le carré du haut du format
« deux carrés », quel que soit le sujet du jour.

## Pourquoi le micro devant le bec

Le micro est positionné **devant le bec**, qu'il recouvre en partie. C'est le
point clé : le spectateur ne voit pas les mouvements de bec, donc l'animation
n'a pas besoin d'être synchronisée avec la voix ElevenLabs. Une seule vidéo
d'une dizaine de secondes est découpée en segments de 2-3 s, réutilisés dans
n'importe quel ordre sur n'importe quel reel, sans décalage lèvres/son visible.

## Contrainte de cadrage (la plus importante)

L'image est générée en 9:16, mais elle sera **recadrée en carré** pour entrer
dans la zone du haut. Tout ce qui compte — tête, buste, micro — doit donc tenir
dans le carré central de l'image. D'où les consignes de safe zone dans le prompt.

## Génération

- Format : 1024×1792 (9:16), quality `high`
- **Joindre `assets/curio_reference/curio_character_ref.png`** en image de
  référence, sinon le personnage dérive (règle §6 CLAUDE.md).
- Généré manuellement par Benjamin (abonnement GPT perso), pas par le pipeline.

## Prompt

```
Cute chubby penguin character, blue and white feathers, large expressive blue
eyes, small orange beak, a small tuft of feathers on top of his head, wearing a
red knitted scarf. Pixar-quality 3D render, ultra detailed soft feathers,
cinematic soft lighting, shallow depth of field.

POSE: He is SEATED at a wooden studio desk, facing the camera straight on,
framed from the chest up like a podcast host. Both flippers rest relaxed on the
desk in front of him. Calm, warm, friendly expression — NOT surprised, NOT
shouting. Beak slightly open as if speaking mid-sentence. Direct eye contact
with the camera.

MICROPHONE (critical): a large black professional broadcast microphone,
Shure SM7B style, matte black body with a dark foam windscreen, mounted on a
black articulated boom arm entering the frame from the bottom right. The
microphone head is positioned DIRECTLY IN FRONT OF the penguin's beak, at beak
height, clearly overlapping and covering the lower half of his beak from the
camera's point of view. The microphone is the closest object to the camera and
must partially hide the beak.

FRAMING: vertical 9:16 image. The penguin's head, upper body and the microphone
must ALL sit inside the central square region of the frame — the shot must still
read correctly when cropped to a 1:1 square. Keep the head centered horizontally,
with empty headroom above the head and empty blurred desk space below. Nothing
important in the top 15% or the bottom 15% of the image.

BACKGROUND: neutral warm podcast studio, strongly blurred (bokeh) — warm wooden
slat wall, one soft warm lamp glow, one out-of-focus green plant. Deliberately
generic and timeless: no seasonal decoration, no season-specific object, no
topic-specific prop, nothing that ties the shot to a particular subject, so the
same footage can be reused across every video.

No text. No logo. No watermark. No subtitles. No on-screen graphics.
Vertical 9:16.
```

## Variantes à générer dans la foulée

Générer 2-3 poses légèrement différentes (inclinaison de tête, une nageoire qui
se lève) permet d'alterner les segments d'un reel à l'autre sans que ça se voie.
Garder exactement le même cadrage, le même micro et le même fond d'une variante
à l'autre — seule la pose change.

---

# Animation Seedance 2.0 — clip 10 s réutilisable

Image source validée le 30/08/2026 : Curio assis à un bureau en bois, micro
broadcast noir sur bras articulé devant le bec, mur lilas à nuages en relief,
enseigne néon « curio.education ». Fond neutre, aucun élément lié à un sujet.

## Pourquoi ces contraintes

Le clip est découpé en segments de 2-3 s remontés **dans un ordre arbitraire**,
sur des reels différents. Tout ce qui évolue de façon directionnelle sur les
10 s casse le remontage : un mouvement de caméra, une dérive du personnage, une
variation de lumière ou une enseigne qui clignote produisent un saut visible à
chaque raccord. D'où caméra verrouillée, pose de repos identique au début et à
la fin, lumière constante, fond figé.

Pas d'audio demandé : §3 CLAUDE.md — la piste native d'un clip n'est jamais
mappée au montage, seule la voix ElevenLabs joue.

## Prompt

```
Animate this exact image. Keep the character, the microphone, the desk, the
neon sign and the background EXACTLY as they are in the source image — do not
redesign, do not restyle, do not add or remove any object.

MOTION: the blue penguin is talking calmly and warmly to the camera, like a
podcast host mid-episode. Subtle continuous idle motion only:
- small natural head movements and micro head tilts, left and right
- natural eye blinks at irregular intervals, eyes stay warm and engaged,
  always looking straight into the camera lens
- very slight body breathing and shoulder sway
- occasional small relaxed flipper movement resting on the wooden desk
- the red knitted scarf and the soft feathers react slightly to the movement

BEAK: keep beak movement minimal and subtle. The microphone stays directly in
front of the beak and keeps covering it at all times. No exaggerated wide beak
opening, no shouting, no cartoon mouth flapping. No specific lip-sync — this
footage is reused over different voiceovers.

CAMERA: absolutely locked static camera. No zoom, no push-in, no pan, no tilt,
no dolly, no handheld shake, no rack focus. The framing must be identical from
the first frame to the last frame.

CONSISTENCY (critical — this footage is cut into short segments and reused in
any order): the character must stay centered and must never drift out of his
starting position. Lighting, exposure and colours must stay perfectly constant
for the whole duration — no flicker, no light change, no colour shift. The neon
sign stays steadily lit, never blinking. The background stays completely static.
Nothing enters or leaves the frame. No transition, no cut, no scene change.
The final frame must look almost identical to the first frame so the clip can
loop and be re-cut seamlessly.

9:16 vertical frame, Pixar-quality 3D rendering, cinematic soft lighting.
Duration: 10 seconds. No audio, no speech, no music.
```

## À la réception du MP4

Découper en segments de 3 s réutilisables et les déposer dans `assets/clips/`.
Vérifier avant découpe que la première et la dernière frame se ressemblent :
si Seedance a quand même dérivé, ne garder que la portion stable.
