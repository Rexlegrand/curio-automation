CURIO AUTOMATION — CLAUDE CODE BRIEF
Version : 2.19 — Fix bug Remotion bloquant TOUT montage : le CLI Remotion
(remotion/node_modules/@remotion/renderer/dist/get-extension-of-filename.js)
détecte une extension de fichier en découpant le CHEMIN ABSOLU ENTIER sur les
points (split('.') sur toute la string, pas juste le nom de fichier final) —
bug amont, pas dans notre code. Le home Mac (/Users/benjamin.ptryhuml/...)
contient un point dans "benjamin.ptryhuml" : toute sortie de séquence PNG
Remotion placée sous output_dir (chemin absolu) ou même en chemin relatif via
".." (qui contient aussi des points) faisait planter le render avec "The
output directory of the image sequence cannot have an extension". Ce bug
existe depuis toujours sur cette machine — indépendant du sujet/slug du reel
— et n'avait simplement jamais été déclenché avant le premier reel réel
généré après v2.18 (éclipse du 12/08, reel du 13/08). Fix : generators/video_assembler.py,
`_render_captions_overlay()` rend désormais la séquence PNG dans un dossier
temporaire système (tempfile.mkdtemp(), ex. /var/folders/.../T/...) au lieu
d'un sous-dossier de output_dir — un chemin temp système ne contient jamais
de point. Le dossier temp est toujours nettoyé (shutil.rmtree) après
incrustation sur la vidéo finale, comme avant. Aucun autre comportement du
montage changé. Validé bout en bout sur le reel réel éclipse du 13/08
(output/2026-08-13/l_eclipse_solaire_du_12_aout_2026_vue_de_france_.../).
Hérite v2.18 — Sous-titres : remplacement du burn-in ASS/FFmpeg par un rendu
Remotion dédié (dossier remotion/, projet Node/TypeScript autonome, Remotion
4.0.507). Montage en 3 passes désormais (generators/video_assembler.py) : (1)
FFmpeg concatène clips + illustrations + audio ElevenLabs SANS sous-titres →
fichier intermédiaire _tmp_no_subtitles.mp4 ; (2) Remotion (composition
TikTokCaptions, remotion/src/tiktok-captions/) rend les sous-titres en séquence
PNG transparente, calée sur le subtitles.srt du reel et la durée EXACTE du
montage (audio + AUDIO_TAIL) — jamais sur le seul dernier timestamp du SRT ;
(3) FFmpeg incruste cette séquence sur la vidéo de l'étape 1, réencode
reel_final.mp4. Le reste du montage (TIMELINE, compute_segments, concat
clips/illustrations, voix ElevenLabs seule en continu hook+CTA compris) reste
100 % FFmpeg, strictement inchangé — seule l'étape sous-titres change de moteur.
srtText et totalSeconds sont passés à Remotion via un fichier --props temporaire
(_remotion_props.json, supprimé après usage), jamais en JSON inline sur la
ligne de commande : les apostrophes françaises du script ("qu'il", "l'appelle")
cassent l'échappement shell.
Règle sous-titres RESSERRÉE : UNE SEULE LIGNE affichée à la fois, jamais de
wrap multi-ligne — l'ancien rendu ASS tolérait 2 lignes empilées simultanément
pour une même phrase (ex. "un ours se cache dans le" / "logo du Toblerone !") ;
en Remotion, un même bloc du SRT trop long pour une ligne de 28 caractères
devient plusieurs FENÊTRES D'AFFICHAGE SÉQUENTIELLES, jamais deux lignes en
même temps. Regroupement toujours phrase par phrase (jamais à cheval sur deux
blocs du SRT). Nouveauté visuelle : mot en cours de prononciation surligné en
bleu (effet "pop" TikTok), absent de l'ancien ASS — timing mot à mot approximé
par répartition proportionnelle à la longueur des mots à l'intérieur de chaque
bloc de phrase (remotion/src/tiktok-captions/words.ts), PAS les vrais
timestamps Whisper : subtitle_generator.py les lit puis les jette
(json.unlink()) et ne les persiste jamais — limite connue, à lever un jour en
faisant persister ce JSON si la précision mot à mot devient insuffisante.
Nettoyage code mort : srt_to_ass(), ASS_HEADER, _ass_time() supprimés de
video_assembler.py (remplacés) ; SUBTITLE_FONT_SIZE et SUBTITLE_MARGIN_V
supprimés de config.py (taille de police et position gérées côté Remotion
désormais, mêmes valeurs visuelles : 60px, baseline ~79%). subtitles_styled.ass
n'est plus généré. Validé bout en bout sur le reel réel du 03/08 (toblerone,
copie sandboxée, original jamais touché) avant bascule définitive. Coût : 0€
additionnel (Remotion tourne en local, comme FFmpeg/Whisper).
Hérite v2.17 — Fond du hook (curiosité) : fin du theme large, source unique
hook_background. Bug constaté : le theme "sport" mélangeait football et MMA
(pas le même décor visuellement), et plus généralement un theme large
(histoire, nature...) ne garantit AUCUNE cohérence visuelle entre deux sujets
différents — un fond "historique générique" pouvait tomber à côté du sujet
réel (ex : Vikings). Root cause plus profonde : le hook_frame (GPT Image 2)
ET le prompt Seedance dérivaient chacun le fond indépendamment à partir du
même theme large — aucune garantie qu'ils restent identiques, et aucun des
deux n'était spécifique au sujet réel.
Fix : script_generator.py fait désormais classifier Claude sur un champ
`hook_subcategory` (identifiant précis, ex "mma_combat", "histoire_vikings",
jamais une famille large comme "sport"/"histoire") + un champ `hook_background`
(texte photoréaliste toujours rédigé, spécifique au sujet réel). Une seule
fonction (`resolve_hook_background`, prompts/curiosity_prompts.py) tranche :
texte fixe si hook_subcategory est dans REUSABLE_HOOK_BACKGROUNDS (liste
étroite ci-dessous, fond réellement interchangeable dans la sous-catégorie),
sinon le texte spécifique de Claude. Le résultat est stocké dans
script["hook_background"] — SOURCE UNIQUE ensuite consommée identiquement par
curiosity_prompts.build_hook_frame_prompt() ET seedance_prompts.build_seedance_prompt()
(main.py, image_generator.py) : impossible que les deux prompts divergent
désormais. Sous-catégories réutilisables (fond fixe, cohérent quel que soit
le sujet précis à l'intérieur) : cyclisme_tdf, football, mma_combat, maths,
meteo, default. Tout le reste (histoire, nature/animaux, tennis, science,
transport, et toute nouvelle sous-catégorie que Claude invente) reçoit un
fond spécifique au sujet réel à chaque reel, jamais de générique par famille.
"science" a été explicitement retiré du groupe réutilisable après audit des
reels déjà générés (le seul sujet réel — dinosaures à plumes — ne correspond
pas à un fond labo/éprouvettes).
Cas du reel 13/08 (Vikings) : script.json corrigé manuellement avec
hook_subcategory="histoire_vikings" et un hook_background Vikings (drakkar,
fjord norvégien) ; seedance_prompt.txt régénéré en conséquence (aucun appel
API — write_prompt_files() est pure côté Python). Benjamin dépose lui-même le
hook_frame.png de ce reel (généré manuellement hors pipeline, abonnement GPT
personnel) — non touché par le pipeline.
Hérite v2.16 — Tolérance de durée assouplie : cible 28-35s inchangée, mais
un dépassement jusqu'à 40s n'est plus un problème (Benjamin, constaté sur les
reels du 07/08 à 36,84s et 08/08 à 35,88s — aucune des deux versions audio
ElevenLabs ne rentrait sous 35s malgré un word_count dans la cible 78-88,
juste un débit de voix plus lent ce jour-là). Le pipeline ne bloquait déjà
rien au-delà de 35s (aucun check de durée maximale dans le code, seulement un
seuil minimum ~16,5s dans video_assembler.py) — ce changement est purement
éditorial : script_generator.py continue de viser 78-88 mots comme avant,
mais un reel entre 35 et 40s n'a plus besoin d'être régénéré ou signalé.
Au-delà de 40s, revoir la narration.
Hérite v2.15 — Retour arrière sur l'audio natif du clip CTA (v2.14).
Constaté en prod sur le reel du 05/08 : la voix lip-sync Seedance du clip
curio_cta.mp4 sonne différemment de la voix ElevenLabs qui porte tout le
reste du reel — le changement de voix en toute fin casse le rythme, le
spectateur ne comprend pas la rupture. RÈGLE CORRIGÉE : le CTA doit suivre
EXACTEMENT la même règle que le hook — la piste audio native d'un clip vidéo
n'est jamais utilisée dans le montage, même quand le fichier en porte une ;
seule la voix ElevenLabs choisie (v1/v2) joue, en continu, du tout premier
au tout dernier cadre du reel. generators/video_assembler.py : suppression
du split amain/acta + concat audio introduit en v2.14, retour à
`[audio_index:a]apad[aout]` unique sur toute la durée. Ce qui RESTE de v2.14
et reste correct : le clip curio_cta.mp4 est toujours utilisé tel quel côté
VIDÉO (plus de trim_start, plein cadrage du lip-sync visuel — seul l'audio
est ignoré) et sa durée réelle reste mesurée dynamiquement sur le fichier
(TIMELINE "dynamic", config.py) plutôt que codée en dur. Le reel du 05/08
(output/2026-08-05/multiplier_un_nombre_a_virgule_par_5_version_rapide/)
avait été assemblé avec le montage v2.14 buggé — reel_final.mp4 supprimé et
réassemblé avec le code corrigé.
Hérite v2.14 — CTA final 100% fixe (texte, vidéo ET audio). Benjamin a
déposé un nouveau assets/clips/curio_cta.mp4 avec sa propre piste audio
(vidéo + voix lip-sync Seedance, ~4,1s mesurés). Ce clip est désormais
utilisé tel quel — plus de trim_start (l'ancien clip sautait ses 2 premières
secondes, gardait les 3 dernières, silencieux ; le nouveau est utilisé en
entier). config.py : TIMELINE bascule l'entrée CLIP_CTA de {"fixed": 3,
"trim_start": 2.0} à {"dynamic": True} — sa durée réelle est mesurée sur le
fichier à chaque montage (video_assembler.compute_segments) plutôt que codée
en dur, pour ne jamais se désynchroniser si Benjamin dépose un clip d'une
durée légèrement différente. video_assembler.py : l'audio final concatène la
voix ElevenLabs (segments hook → illustration_3) puis la piste audio native
du clip CTA — plus aucun appel ElevenLabs ni aucune piste ElevenLabs jouée
sur ce segment (le script narré continue d'inclure la phrase CTA en texte,
utile aux sous-titres et à la cohérence du word_count, mais cette portion de
l'audio ElevenLabs n'est plus mappée dans la vidéo finale, remplacée par la
voix native du clip). Vérifié : aucune ancienne référence à un clip CTA
audio/vidéo séparé dans le code (le CTA a toujours été un seul fichier
assets/clips/curio_cta.mp4, un seul point à corriger). Coût : zéro par reel
sur cette étape, comme avant — asset fixe unique réutilisé sur tous les
reels, jamais régénéré (mêmes régime que curio_explication.mp4/2). Testé de
bout en bout (montage réel sur un reel existant, filtre audio concat validé,
durée finale exacte = durée totale calculée).
Hérite v2.13 — Langue de travail resserrée : français exclusivement avec
Benjamin, jamais anglais ni portugais ni aucune autre langue, sauf demande
explicite contraire. Remplace v2.12 (qui tolérait l'anglais par défaut).
Ajouté aussi en §17 règle 10 (règles de codage non négociables), pour éviter
d'avoir à le répéter à chaque session. Voir §0.
Hérite v2.12 — Langue de travail de Claude Code sur ce repo : anglais ou
français uniquement, jamais portugais (ni aucune autre langue). S'applique à
toute réponse, tout commentaire ajouté, tout message de commit généré pour
ce projet.
Hérite v2.11 — Deux changements systémiques.
(1) CTA unique fixe : suppression de l'alternance abonnement/commentaire (v2.3).
Un seul CTA désormais, partout, sans variation : "Envoie CURIO en MP pour
recevoir une activité/un exercice gratuit !" (constante CTA_TEXTE, config.py).
Appliqué au script narré (dernier segment, role cta, mot pour mot), au CTA
visuel (déjà un asset fixe unique, assets/clips/curio_cta.mp4, inchangé côté
code) et à la description Instagram (LIGNE_CTA, instagram_generator.py).
generators/script_generator.py : cta_type, CTA_INSTRUCTIONS et la sélection
alternée supprimés (générateur devenu déterministe sur ce point) ; main.py :
--cta et next_cta() supprimés ; script.json n'a plus de champ cta_type.
(2) Hook frame réutilisable pour les compétences : pour type=competence
(français ET maths), hook_frame.png n'est plus jamais généré par GPT Image 2.
Deux assets fixes déposés (assets/hook_frames/hook_frame_francais.png,
hook_frame_maths.png) — image_generator.py copie simplement le fichier
correspondant à la matière dans output/[date]/[slug]/hook_frame.png (route
"asset_copy", 0€, 0 appel API, log_api_call quand même tracé pour audit). Le
prompt Seedance continue de se générer normalement à partir de cette image
fixe et du hook textuel du jour — seule l'animation change. Ne s'applique PAS
aux curiosités (Type A) : leur hook_frame reste généré à chaque reel via GPT
Image 2 car le fond thématique doit varier selon le sujet (BACKGROUNDS,
curiosity_prompts.py).
Coût économisé par reel compétence : 1 image GPT Image 2 (0,011$) en moins —
reel compétence français/maths concept passe de 5 à 4 GPT Image 2 (0,044$ au
lieu de 0,055$) ; reel compétence maths opération posée/astuce (déjà en
rendu code depuis v2.6, hook+miniature seulement) passe de 2 à 1 GPT Image 2
(0,011$ au lieu de 0,022$) — la moitié du poste images sur ces reels.
Hérite v2.10 — Ajout niveau 6e (main.py --niveau accepte CP/CE1/CE2/CM1/CM2/6e,
en plus des 5 niveaux CP→CM2 d'origine). Le calendrier éditorial prévoyait déjà des reels
6e (grammaire/pourcentages) que le pipeline rejetait faute de ce niveau dans les choix
argparse. Fonctionne uniquement avec --sujet fourni explicitement : data/Competences_Curio.xlsx
n'a toujours que 5 onglets CP→CM2, donc la sélection aléatoire pick_competence() reste
impossible pour 6e (onglet absent) — un reel 6e sans --sujet explicite échoue encore.
Hérite v2.9 — Fix v2.8 : le template compétence français demandait encore à GPT Image 2
de dessiner un paragraphe entier (bloc ✅ Correct/Test/❌ Incorrect/Test complet) sur
l'illustration — illisible sur mobile, et cette masse de texte débordait de la zone de
sécurité 30% réservée aux sous-titres (le débordement venait du CONTENU de l'illustration,
pas d'un mauvais calcul de position des sous-titres : SUBTITLE_MARGIN_V est un réglage
unique correct pour tout le reel, qui suppose que l'illustration respecte elle-même sa
zone basse vide). Remplacé par mot_cle/lettre_cle (ex: "tamBOUR", un mot court, une lettre
en couleur) — toute l'explication pédagogique (règle, test de substitution, comparaison
correct/incorrect) reste dans la narration audio uniquement, jamais imprimée sur l'image.
Voir §5/§7.
Hérite v2.8 — 3 bugs systémiques corrigés après retour terrain sur les reels des 21-22/07 :
(1) Durée montage désynchronisée : les illustrations utilisaient des poids fixes codés en
dur (5:5:3) déconnectés du contenu réel du reel. video_assembler.py cale désormais leur
durée sur les timecodes réels du script.json (proportionnel à la durée finale de l'audio),
plus de poids statique — voir §3. Chemin unique (main.py appelle video_assembler.assemble_reel
aussi bien en pipeline complet qu'en --assemble), pas un fix isolé à un cas de test.
(2) Durée audio hors cible 28-35s (jusqu'à 40s observés) : la cible de 85-100 mots
supposait ~180 mots/min ; mesuré en prod, la voix Curio 8 lit 141-160 mots/min réels.
Cible recalibrée à 78-88 mots, revérifiée automatiquement par script_generator.py (jusqu'à
3 régénérations) AVANT le Checkpoint 1 — jamais de script hors cible qui compte sur le
montage pour compenser après coup. Voir §2.
(3) Illustrations français/curiosité polluées par du contenu d'anciens reels (canicule,
drakkar viking) : les fichiers canoniques style_illustration_01/02.png n'étaient pas des
exemples de style neutres mais des visuels réels d'anciens sujets, injectés en
image-to-image à chaque génération. Retirés des références d'illustration (§6). Le
template français n'avait par ailleurs aucune consigne de sujet photo — ajout du champ
sujet_photo (un par illustration, concret et distinct) — voir §7.
Hérite v2.7 (révélation progressive stage 1/2/3, astuce_chaine 3 frames distincts, une
ligne = un calcul), v2.6 (moteur de rendu code maths, 0€, 0 hallucination) et v2.5 (thèmes
"velo"/"combat", sous-titres 1 phrase/écran, miniature safe-zone 4:3, durée 28-35s, CTA
alterné 50-50, anti-digression).
Modèle cible : Claude-fable 5 (ou équivalent le plus puissant disponible)
Rédigé par : Benjamin Petry—Hummel — Juillet 2026

## 0. LANGUE DE TRAVAIL

Claude Code répond exclusivement en français à Benjamin sur ce projet — jamais
en anglais, jamais en portugais, jamais dans une autre langue — sauf demande
explicite contraire de sa part (v2.13, resserre v2.12 : l'anglais n'est plus
toléré par défaut). Voir aussi §17 règle 10.

RÈGLE ABSOLUE N°1 — STRUCTURE DU CODE
Ne jamais empiler du code sur du code existant. Si une modification est nécessaire, réécrire le fichier complet de A à Z. Zéro patch, zéro commentaire "// TODO", zéro code mort laissé en place. Chaque fichier doit être lisible et autonome à tout moment.

## 1. OBJECTIF DU PROJET

Construire un pipeline CLI Python semi-automatisé qui produit un Reel Instagram complet (28-35 secondes visées, toléré jusqu'à 40s — v2.16) pour le compte @curio.education en moins de 30 minutes, avec validation humaine à chaque étape critique.

Stack :
* Python 3.10+
* OpenAI API (GPT Image 2 pour les images, Whisper pour les sous-titres)
* ElevenLabs API (audio voix Curio 8)
* Anthropic API (génération de scripts et prompts)
* FFmpeg (montage vidéo local, gratuit)
* Pillow (rendu code des opérations posées maths, gratuit — v2.6)
* Remotion (rendu des sous-titres TikTok-style, local, gratuit — v2.18)
* Seedance 2.0 / Dreamina (hook animé — manuel, pas d'API)

Coût cible : < 1,10 € par Reel — Temps cible : < 30 minutes par Reel — Fréquence cible : 6 Reels/semaine

## 2. DEUX TYPES DE CONTENUS

Type A — Curiosité du jour
* Fréquence : 4/semaine (lundi, mardi, jeudi, vendredi)
* Durée : 28-35 secondes visées, toléré jusqu'à 40s (v2.16 — la voix ElevenLabs peut lire plus lentement que prévu même avec un word_count dans la cible ; au-delà de 40s, revoir la narration)
* Sujet : fait insolite, anecdote, phénomène scientifique, histoire
* Hook : "Attends... [fait surprenant en question ou affirmation choc]"

Type B — Compétence scolaire
* Fréquence : 2/semaine (mercredi, samedi)
* Durée : 28-35 secondes visées, toléré jusqu'à 40s (v2.16 — la voix ElevenLabs peut lire plus lentement que prévu même avec un word_count dans la cible ; au-delà de 40s, revoir la narration)
* Sujet : règle de maths ou français — niveaux CP, CE1, CE2, CM1, CM2
* Hook : "Attends... tu sais vraiment comment [compétence] ?"
* Source des sujets : data/Competences_Curio.xlsx
    * Colonnes : Matière | Difficulté | Compétence
    * Onglets : CP / CE1 / CE2 / CM1 / CM2

Règles éditoriales du script (tous types) :
* AUCUNE DIGRESSION : chaque phrase sert le sujet principal. Une info « cousine » du sujet
  (autre règle, autre récompense, anecdote annexe) est exclue — média éducatif, exactitude
  factuelle non négociable (leçon du reel #20 : dossard rouge hors sujet des sanctions).
* Narration : 78-88 mots (v2.8 — la voix eleven_v3 « Curio 8 » lit 141-160 mots/min
  RÉELLEMENT mesurés en production, jamais les ~180 mots/min supposés en v2.7 ; cette
  fourchette reste dans 28-35s même au débit le plus lent observé). script_generator.py
  revérifie automatiquement le word_count après chaque génération et régénère (jusqu'à 3
  tentatives) AVANT de présenter le script au Checkpoint 1 — un script hors cible ne doit
  jamais être découvert au montage.
* CTA unique fixe (v2.11 — plus d'alternance) : « Envoie CURIO en MP pour recevoir
  une activité/un exercice gratuit ! » (constante CTA_TEXTE, config.py). Identique
  dans le script narré (dernier segment), le CTA visuel (asset fixe unique,
  assets/clips/curio_cta.mp4) et la description Instagram (LIGNE_CTA).

## 3. STRUCTURE D'UN REEL — SÉQUENCE DE MONTAGE EXACTE

```
Hook animé        — Seedance MP4, 4s fixes (généré manuellement, droppé dans output/)
Illustration 1    — PNG GPT Image 2 ou rendu code (maths posé), durée flexible
Clip Curio A      — curio_explication.mp4, 4s fixes
Illustration 2    — PNG GPT Image 2 ou rendu code, durée flexible
Clip Curio B      — curio_explication_2.mp4, 4s fixes
Illustration 3    — PNG GPT Image 2 ou rendu code, durée flexible
CTA               — curio_cta.mp4, utilisé tel quel côté vidéo (durée réelle mesurée
                    sur le fichier, ~4s) — sa piste audio native n'est jamais utilisée (v2.15)
```

Durée totale du reel = durée de l'audio choisi + 0,2s : la vidéo s'arrête quand la voix
s'arrête. Les clips Curio A/B (hook_video.mp4, curio_explication.mp4/2) restent fixes à
4s chacun (assets physiques à longueur imposée) ; le clip CTA est fixe lui aussi mais sa
durée est mesurée dynamiquement (v2.14, ~4s, jamais recodée en dur) ; les 3 illustrations
se partagent le temps restant au prorata des TIMECODES RÉELS du script.json de ce reel
(segments correspondant, dans l'ordre, aux 3 slots illustration — v2.8, plus de poids
statique 5:5:3 codé en dur : un poids fixe désynchronisait l'affichage dès que l'audio
final s'éloignait de la durée nominale visée par le script). Le pipeline bloque avec une
erreur claire si l'audio est trop court (< ~16,5s).

Règles de montage :
* Format sortie : MP4 1080×1920 (9:16), 30fps, 4-8 Mbps
* Audio : fichier ElevenLabs choisi (v1 ou v2), SEUL, en continu du premier au dernier
  cadre du reel — hook compris ET CTA compris (v2.15). Aucun clip vidéo n'apporte sa
  propre piste audio dans le montage, même quand le fichier physique en porte une (le clip
  curio_cta.mp4 a une piste native lip-sync Seedance, jamais mappée) : deux voix
  différentes sur le CTA cassaient le rythme du reel (retour arrière sur v2.14).
* Sous-titres : Whisper avec timestamps mot à mot → subtitles.srt. Rendu par Remotion (v2.18, remplace le burn-in ASS/FFmpeg) : 60px, blanc bold, contour noir épais + ombre légère, sans boîte de fond, baseline ~79% de la hauteur — mêmes réglages visuels que l'ancien ASS. UNE SEULE LIGNE à l'écran à la fois, jamais de wrap multi-ligne (resserré : l'ancien ASS empilait jusqu'à 2 lignes simultanées) — un bloc de phrase trop long pour une ligne de 28 caractères devient plusieurs fenêtres d'affichage séquentielles, jamais deux lignes en même temps. « Attends... » s'affiche seul, le reste du hook n'apparaît que quand il est prononcé. Mot en cours de prononciation surligné en bleu (effet pop TikTok, timing approximé — voir en-tête v2.18). Contractions et typographie françaises respectées (qu'il, Abonne-toi, espace avant ? et !)
* Transitions : cut sec entre chaque segment (pas de fondu)

## 4. ASSETS À GÉNÉRER PAR REEL

| Asset | Outil | Quantité | Paramètres |
|---|---|---|---|
| Script JSON horodaté | Claude API | 1 | 85-100 mots, segments timecodes, doit correspondre au temps 28-35s |
| Image hook frame | GPT Image 2 (Type A) **ou asset fixe copié (Type B, v2.11)** | 1 | 1024×1792, standard quality — Type B : copie assets/hook_frames/hook_frame_francais.png ou hook_frame_maths.png, 0€, 0 appel API |
| Illustrations structure | GPT Image 2 **ou rendu code (v2.6)** | 3 | 1024×1792 — code_render si compétence maths avec opération posée/astuce (§7 bis), sinon GPT Image 2 standard quality |
| Miniature feed | GPT Image 2 | 1 | 1024×1792, high quality |
| Audio voix | ElevenLabs | 2 versions | Curio 8, Eleven v3, ~28-35s |
| Prompt Seedance | Texte généré | 1 | Fichier .txt à copier-coller |
| Sous-titres | Whisper local | 1 | .srt depuis audio validé |
| Montage final | FFmpeg Python | 1 | MP4 9:16 1080p |
| Description Instagram | Claude API | 1 | .txt avec hashtags + mentions |

Total images GPT Image 2 : 5 par Reel curiosité (hook + 3 illus + miniature) ;
4 par Reel compétence français/maths-concept (hook asset fixe, v2.11 + 3 illus
+ miniature) ; 1 par Reel compétence maths opération posée/astuce (hook asset
fixe + miniature seulement — 3 illustrations en rendu code, 0€, §7 bis).

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

**Bug v2.8 — pollution des illustrations** : style_illustration_01.png et
style_illustration_02.png se sont révélés être des visuels RÉELS d'anciens reels
(une carte canicule France, un drakkar viking), pas des exemples de style neutres.
Injectés en image-to-image à chaque illustration, leur contenu se recopiait tel
quel dans des reels sans rapport (ex : un reel sur "m devant m/b/p" affichant un
bateau viking). image_generator.py ne les injecte plus pour les illustrations —
seul style_fond_cahier.png (fond Seyès pur, sans sujet) reste utilisé pour cette
route. Les deux fichiers restent listés ci-dessus (existence encore vérifiée par
check_references) mais ne sont plus consommés pour les illustrations tant qu'ils
n'ont pas été remplacés par de vrais exemples neutres.

## 7. PROMPTS IMAGES — TEMPLATES

Les templates exacts vivent dans `prompts/curiosity_prompts.py`, `prompts/competence_prompts.py` et `prompts/seedance_prompts.py`. Ils reprennent mot pour mot les templates du brief v2.0 : fond cahier Seyès, clipping magazine, photoréalisme Type A, exactitude pédagogique stricte Type B (chaque chiffre/mot exact, méthode Éducation Nationale), hook frame Curio, prompt Seedance avec lip-sync.

Depuis v2.6, `prompts/competence_prompts.py` ne sert plus de template maths à
chiffres exacts (`build_maths_prompt` supprimé, remplacé par le rendu code,
§7 bis) : il ne reste que `build_concept_prompt` (sujets maths sans calcul,
ex. symétrie) et `build_francais_prompt` (français, toujours GPT Image 2).

Depuis v2.8, chaque illustration du schéma Type B français porte un champ
`sujet_photo` : description photoréaliste CONCRÈTE et DISTINCTE du mot-exemple
de cette illustration (ex : "un tambour en bois, gros plan, lumière naturelle"
pour "tambour"). Sans ce champ, le prompt français ne contenait aucune consigne
de sujet visuel — GPT Image 2 comblait le vide en piochant dans les références
(cause du bug de pollution ci-dessus, §6).

Depuis v2.9, deux champs supplémentaires remplacent le paragraphe complet
autrefois dessiné sur l'image : `mot_cle` (le mot-exemple seul, ex. "tambour")
et `lettre_cle` (UNE lettre de ce mot à colorer, ex. "b" → "tamBOUR"). L'image
ne contient plus QUE la photo (sujet_photo) + ce mot court — jamais la règle,
les tests de substitution ni la comparaison correct/incorrect, qui restent
uniquement dans la narration audio. Le prompt (`PROMPT_COMPETENCE_FRANCAIS`)
demande aussi explicitement de laisser les 30% du bas de l'image entièrement
vides (zone réservée aux sous-titres) : un paragraphe entier y débordait
systématiquement, ce n'était pas un bug de calcul de position des sous-titres
mais un débordement du contenu de l'illustration dans sa propre zone de
sécurité. `script_generator.py` vérifie que les 3 `sujet_photo` sont renseignés
et distincts, et que chaque `lettre_cle` est une seule lettre présente dans son
`mot_cle`, avant Checkpoint 1 (régénère sinon, jusqu'à 3 tentatives, même
mécanisme que la classification maths).

Fond du hook (curiosité) — v2.17, remplace l'ancien mapping par `theme` large
(BACKGROUNDS keyé par sport/combat/velo/nature/histoire/maths/science/
transport/meteo/default, abandonné : un theme large ne garantit aucune
cohérence visuelle entre deux sujets différents — voir en-tête v2.17).
Claude classe chaque reel curiosité sur `hook_subcategory` (identifiant
précis, jamais une famille large) + rédige toujours `hook_background` (texte
spécifique au sujet réel). `resolve_hook_background()` (prompts/curiosity_prompts.py)
retourne le texte fixe ci-dessous si `hook_subcategory` y figure, sinon le
texte spécifique de Claude — jamais de rattachement approximatif à la
sous-catégorie la plus proche :

```python
REUSABLE_HOOK_BACKGROUNDS = {
    "cyclisme_tdf": "Tour de France mountain road at golden hour, cheering crowd waving French flags, blurred peloton of cyclists in the background",
    "football":     "football stadium at golden hour, French flags, crowd blurred",
    "mma_combat":   "MMA octagon cage arena at night, dramatic spotlight, blurred cheering crowd, professional fight venue ambiance",
    "maths":        "giant chalkboard with relevant equation, classroom ambiance",
    "meteo":        "scorching cityscape, heat shimmer, orange sky",
    "default":      "soft colorful gradient background, neutral and clean",
}
```

Tout sujet historique, animalier/nature, tennis, science, transport ou tout
autre sujet à décor réel précis reçoit un `hook_background` rédigé par Claude
pour CE sujet exact — jamais un des 6 textes fixes ci-dessus. Ce même champ
`hook_background` alimente identiquement le hook_frame (GPT Image 2) ET le
prompt Seedance (main.py, image_generator.py) : une seule source, jamais deux
descriptions de fond qui divergent entre l'image et l'animation.

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

## 9. COÛT — IMPACT DU RENDU CODE (v2.6) ET DU HOOK FRAME FIXE (v2.11)

| Reel | Type A curiosité | Type B compétence (concept/français) | Type B compétence maths opération posée/astuce |
|---|---|---|---|
| Images | 5 GPT Image 2 × 0,011$ = 0,055$ | 4 GPT Image 2 (hook asset fixe, v2.11) × 0,011$ = 0,044$ | 1 GPT Image 2 (hook asset fixe + miniature seulement) × 0,011$ = 0,011$ |
| Risque hallucination chiffre | — | — | nul sur les illustrations (code_render) |

Hook frame Type B (français ET maths) : asset fixe copié depuis
assets/hook_frames/ (v2.11), jamais régénéré, 0€. Hook frame Type A : GPT
Image 2 à chaque reel, le fond thématique doit varier selon le sujet.

## 10. FLUX D'EXÉCUTION — CHECKPOINTS HUMAINS

```
ÉTAPE 0 — INPUT
  Benjamin saisit : sujet + type + niveau (si compétence)
  Pipeline crée le dossier output/[date]/[slug_sujet]/

  CHECKPOINT 1 — Validation sujet ← Benjamin approuve avant de continuer
  Affiche : script JSON complet + image_route/render_type/operation_data
  (Type B maths) + tous les prompts images + prompt Seedance

ÉTAPE 1 — GÉNÉRATION PARALLÈLE (si checkpoint 1 validé)
  Thread A : GPT Image 2 et/ou rendu code maths (0€) et/ou hook frame asset
    fixe copié (0€, Type B, v2.11) → 5 images (hook + 3 illus + miniature)
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
│   ├── video_assembler.py             ← FFmpeg (montage) + Remotion (sous-titres, v2.18) → montage final .mp4
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
├── remotion/                           ← NOUVEAU v2.18 — rendu sous-titres (remplace ASS/FFmpeg)
│   ├── package.json                    ← Projet Node/TypeScript autonome, Remotion 4.0.507
│   ├── public/sample-captions.srt      ← Exemple SRT pour prévisualisation Studio (npm run dev)
│   └── src/
│       ├── Root.tsx                    ← Enregistre la composition TikTokCaptions
│       └── tiktok-captions/
│           ├── TikTokCaptions.tsx      ← Composition : une ligne à la fois, mot actif surligné
│           └── words.ts                ← Approximation mots + regroupement ≤28 caractères/ligne
│
├── assets/
│   ├── curio_reference/               ← Références visuelles injectées (PNG)
│   ├── clips/                         ← Clips Curio réutilisables (MP4)
│   │   ├── curio_explication.mp4      ← Curio talking head segment 1 (5s)
│   │   ├── curio_explication_2.mp4    ← Curio talking head segment 2 (5s)
│   │   └── curio_cta.mp4              ← Curio CTA final, vidéo (~4,1s, mesuré dynamiquement) — piste audio native jamais utilisée (v2.15)
│   ├── fonts/
│   │   └── PatrickHand-Regular.ttf    ← NOUVEAU v2.6 — police manuscrite rendu code (Google Fonts)
│   ├── hook_frames/                   ← NOUVEAU v2.11 — hook frames fixes Type B (0 régénération)
│   │   ├── hook_frame_francais.png    ← Copié tel quel dans hook_frame.png (Type B français)
│   │   └── hook_frame_maths.png       ← Copié tel quel dans hook_frame.png (Type B maths)
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
            ├── subtitles.srt          ← Whisper — consommé par Remotion (v2.18), plus de .ass intermédiaire
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
| Images (curiosité) | GPT Image 2 (0,011$/image × 5, hook regénéré à chaque reel) | ~0,055$ |
| Images (compétence français / maths concept, v2.11) | GPT Image 2 (0,011$/image × 4, hook asset fixe) | ~0,044$ |
| Images (maths opération posée/astuce, v2.6+v2.11) | GPT Image 2 (miniature seulement, hook asset fixe) + rendu code (3 illus, 0€) | ~0,011$ |
| 2 audios | ElevenLabs API | ~0,22$ |
| Scripts + prompts | Claude API Sonnet | ~0,04$ |
| Sous-titres | Whisper local (transcription) + Remotion local (rendu, v2.18) | 0$ |
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

📩 Envoie CURIO en MP pour recevoir une activité/un exercice gratuit !
(v2.11 — ligne CTA fixe, LIGNE_CTA dans instagram_generator.py, plus de variante commentaire/abonnement)

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
12. Hook frames fixes Type B — ✅ assets/hook_frames/hook_frame_francais.png + hook_frame_maths.png (v2.11, copiés depuis le vivier « Compétences Curio »)
13. Démarrage — pipeline complet construit, montage validé sur assets synthétiques + clips réels, moteur de rendu code maths validé sur division/soustraction/addition/multiplication/astuce
14. Remotion — ✅ projet remotion/ installé (v4.0.507), composition TikTokCaptions validée bout en bout sur un reel réel (v2.18)

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
10. Toute communication avec Benjamin se fait en français exclusivement, jamais en anglais ni dans aucune autre langue, sauf demande explicite contraire (v2.13, remplace v2.12 §0).

Ce fichier est la source de vérité absolue pour Claude Code. En cas de contradiction avec toute autre source, ce fichier prime. Ne pas modifier sans mettre à jour la version en en-tête.
