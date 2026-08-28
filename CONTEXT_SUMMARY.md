# CONTEXT_SUMMARY.md — curio-automation
# Généré le 18/08/2026 — résumé complet pour reprise de session sans perte de contexte
# À lire en complément de CLAUDE.md (source de vérité du code, toujours prioritaire en cas de divergence)
# Ce fichier couvre les évolutions depuis le dernier résumé (06/08/2026) : intégration Remotion
# (sous-titres + prototype carte), recherche d'images stock (Pexels/Wikimedia), et deux créatives
# Meta Ads séparées.

---

## 0. PÉRIMÈTRE DE CE DOCUMENT

Deux chantiers distincts vivent en parallèle, dans deux emplacements différents :

1. **curio-automation** (repo git, `~/Desktop/curio-automation/`) — pipeline de production des
   Reels quotidiens (curiosité + compétences français/maths). Évolutions récentes : sous-titres
   Remotion, recherche d'images stock, prototype d'animation carte.
2. **Ads Meta** (`~/Desktop/Curio /ads_reportage_vs_pixar/` — attention à l'espace après "Curio"
   dans le nom du dossier réel, à vérifier). **N'est PAS un repo git.** Deux créatives distinctes :
   - Créatif 1 "reportage" (format flash info)
   - Créatif 2 "méchant cahier / gentil cahier" (split-screen horreur vs Curio)

Ne pas confondre les deux : le premier est le pipeline de contenu organique quotidien, le second
est de la production ponctuelle de publicités.

---

## 1. ARCHITECTURE DU PIPELINE curio-automation (mise à jour)

```
INPUT (sujet + type + niveau + date, depuis Calendrier_videos_Curio_2026.xlsx)
  ↓
1. SCRIPT — Claude API (Sonnet)
   → script.json : hook, narration, segments, classification image_route,
     ET DÉSORMAIS : stock_query_en (traduction anglaise courte du sujet,
     ajoutée dans le MÊME appel Claude, zéro coût/latence supplémentaire)
  ↓
2. IMAGES — logique de décision enrichie :
   a) Vérifie d'abord si le sujet est "stock_eligible" (pas de texte requis,
      pas le personnage Curio, sujet identifiable) — voir §2 pour les règles
   b) Si éligible : tente Pexels (stock_query_en) → filtre pertinence
      (titre/description doit contenir un terme clé) → si échec, tente
      Wikimedia avec même filtre → si échec, fallback GPT Image 2
   c) Si non éligible (texte requis, Curio, schéma) : GPT Image 2 direct,
      comme avant
   d) Photos stock récupérées passent par le MÊME compositing que les
      illustrations générées (fond cahier Seyès + bordure magazine-clip +
      zone basse vide) — pas de photo brute non habillée
   e) Hook_frame et miniature : TOUJOURS GPT Image 2, jamais de stock
  ↓
3. AUDIO — ElevenLabs, voix "Curio 8", eleven_v3, inchangé
  ↓
4. HOOK ANIMÉ — Seedance 2.0 via Dreamina, manuel, inchangé
  ↓
5. MONTAGE — FFmpeg, EN 3 PASSES (changement majeur vs avant) :
   a) FFmpeg concatène clips/illustrations + audio, SANS sous-titres →
      fichier intermédiaire _tmp_no_subtitles.mp4
   b) Remotion rend les sous-titres (une ligne à la fois, mot actif
      surligné) en séquence PNG transparente, via npx remotion render
      TikTokCaptions --props=<fichier JSON temporaire>
   c) FFmpeg incruste la séquence PNG sur la vidéo de l'étape (a) et
      réencode → reel_final.mp4
   Remotion NE FAIT QUE le rendu des sous-titres. FFmpeg garde tout le
   reste du montage (concat, audio, structure). Ce n'est PAS "full
   Remotion".
  ↓
6. SOUS-TITRES — pipeline en deux temps :
   - Whisper local transcrit → subtitles.srt (segments par phrase)
   - Remotion (@remotion/captions : parseSrt + composant custom
     TikTokCaptions) transforme ça en affichage une-ligne-à-la-fois,
     mot actif surligné en bleu, effet "pop"
   - LIMITE CONNUE : le timing mot-par-mot est approximé (proportionnel
     à la longueur des mots dans le segment), PAS les vrais timestamps
     Whisper — car subtitle_generator.py supprime (unlink()) les
     timestamps mot-à-mot après génération du SRT. Accepté comme
     suffisant après validation visuelle, pas corrigé (voir §5).
  ↓
7. DESCRIPTION INSTAGRAM — Claude API, inchangé
  ↓
PUBLICATION — manuelle sur @curio.education
```

---

## 2. RÈGLES ET CONVENTIONS (EXHAUSTIF — mises à jour + rappel des anciennes clés)

### Règles fondatrices (rappel, toujours actives)
- **CLAUDE.md = source de vérité absolue.**
- **Réécriture complète du fichier concerné à chaque modification, zéro patch empilé.**
- Un fichier = une responsabilité.
- Coût affiché avant tout appel API payant, confirmation demandée.
- Ne jamais régénérer un asset déjà validé DU MÊME reel ; ne jamais réutiliser un asset d'un
  reel sans rapport comme illustration générique.
- Toute optimisation de coût non explicitement demandée doit être proposée et validée avant
  implémentation, jamais appliquée silencieusement.
- Logging systématique : timestamp, coût réel, fichier généré.
- Illustrations curiosité = 100% photoréalistes, jamais de Curio dedans, jamais de cartoon.
- Curio (pingouin) apparaît UNIQUEMENT dans hook_frame, animation hook, CTA, logo miniature.
- CTA fixe : "Envoie CURIO en MP pour recevoir une activité/un exercice gratuit !", clip figé
  `assets/clips/curio_cta.mp4`.
- Hook frames compétences (français/maths) : FIXES, jamais régénérées. Hook frames curiosités :
  jamais de réutilisation par catégorie large, spécifiques au sujet réel.
- **Communication exclusivement en français.** Règle réaffirmée et renforcée cette session :
  ajoutée en tête de CLAUDE.md pour être lue au tout début de chaque session Claude Code
  (récidives observées en portugais à plusieurs reprises malgré correction en cours de session ;
  correction en tête de fichier censée limiter ça plus durablement).
- À ~40% de contexte : commit + push obligatoire, confirmation explicite "local et remote
  synchronisés" avant de fermer un terminal.

### Nouvelles règles — recherche d'images stock (Pexels/Wikimedia)
- **Portée éligible strictement limitée** : seules les illustrations Type A (curiosité, route
  `gpt_image` de base) sont candidates au stock. Hook_frame, miniature, et tout Type B
  (contenu avec texte/schéma/mot-clé imprimé) restent TOUJOURS GPT Image 2, jamais de stock.
- Liste de désqualification (`STOCK_DISQUALIFY_TERMS`) : texte, légende, chiffre, nombre,
  flèche, schéma, diagramme, annotation, étiquette, encadré, curio — si la description
  visuelle contient un de ces termes, pas de tentative stock, GPT Image direct.
- Query envoyée aux APIs : **anglais** (`stock_query_en`, 2-5 mots, sujet concret et
  identifiable), généré dans le MÊME appel Claude que le reste du script (zéro coût/latence
  ajoutés). Pas de traduction locale, pas de 4e appel API séparé.
- Fallback dans l'ordre : Pexels → Wikimedia → GPT Image 2.
- **Filtre de pertinence** : le titre/la description renvoyé par l'API doit contenir un terme
  clé de la requête pour être accepté (pas juste "premier résultat non vide" — option testée
  et rejetée après un cas raté en test réel, voir §3).
- **Limite acceptée et documentée, pas corrigée** : le filtre ne distingue pas un mot générique
  (ex: "penguin") d'un mot spécifique attendu (ex: "emperor") — un résultat peut passer le
  filtre sans être la bonne espèce/sujet précis. Rattrapé par le checkpoint de validation
  humaine existant (CLAUDE.md §10), pas par un filtre plus strict (qui ferait chuter le taux
  de succès stock et annulerait le gain de coût recherché).
- Photos stock téléchargées doivent passer par le même compositing que les illustrations
  générées (fond cahier Seyès obligatoire) — oubli initial dans le premier design, corrigé.

### Nouvelles règles — sous-titres Remotion
- Une seule ligne de texte affichée à l'écran à la fois, jamais de wrap multi-lignes — règle
  stricte confirmée plusieurs fois (y compris quand ça change le rythme de lecture par rapport
  à l'ancien système ASS qui affichait parfois 2 lignes empilées).
- Position : ~30-33% de la hauteur depuis le bas (remonté depuis ~21%/25% initial, jugé trop
  bas). Taille de police augmentée notablement (60px → 76px, +27%) sans déborder du cadre de
  sécurité mobile.
- Mot actif surligné (effet "pop"), couleur distincte du reste du texte.
- Cut sec uniquement entre les plans (jamais de fondu), y compris à l'intérieur d'un même
  segment audio continu splitté en plusieurs sous-plans visuels.

### Nouvelles règles — chantier motion design carte (prototype, pas en prod)
- Outil principal : **Remotion** (motion design, gratuit pour Ben AI — licence gratuite jusqu'à
  3 employés, largement dans le cadre d'une micro-entreprise en usage commercial).
- **HyperFrames** (par HeyGen, PAS "Higgsfield" — confusion de nom initiale corrigée) : filet de
  sécurité SEULEMENT si Remotion ne peut pas faire quelque chose de précis. Pas un deuxième
  système parallèle. Statut d'installation à vérifier (pas confirmé installé dans ce repo).
- Structure prévue : zoom pays → pin → nom du lieu → transition, en remplacement des clips
  Curio "structure" (clips où Curio parle sans son synchronisé, ~3-5s chacun, actuellement
  friction identifiée avec Tony) — objectif : augmenter la qualité perçue sans complexifier le
  pipeline principal.
- **Higgsfield (le vrai outil, différent de HyperFrames)** : abonnement résilié, **ne plus
  jamais appeler les tools Higgsfield**. Donner des prompts prêts à l'emploi (GPT Image 2,
  Seedance 2.0) pour que l'utilisateur génère lui-même.

### Nouvelles règles — process Git (rappel renforcé cette session)
- **Commits séparés et atomiques, jamais mélangés** : un chantier = un commit, même quand
  plusieurs chantiers sont traités dans la même session/le même terminal.
- Ne jamais committer du code expérimental/POC sans validation explicite fichier par fichier.
- Prototypes de test (motion design, outputs de rendu) : gardés en local, PAS committés tant
  qu'une direction n'est pas choisie et validée — ajoutés au `.gitignore` (`test_outputs/`,
  comme `testing_remotion/` déjà en place).
- Avant tout commit sur une session reprise après coupure de contexte : demander l'état git
  actuel (`git status` + `git diff --stat HEAD` + mtimes) plutôt que de supposer — un fix
  antérieur non commité (v2.19) a été retrouvé de cette façon, mélangé par erreur avec du
  travail plus récent si non vérifié.

### Règle — production de créatives Ads (nouveau chantier, distinct du pipeline Reels)
- **Contrainte de sécurité posée d'emblée** : pas de clonage de voix de personnes réelles
  identifiables (ex: journaliste TF1) pour un contenu publicitaire présenté comme un vrai
  reportage — refusé, remplacé par une présentatrice fictive avec codes visuels "flash info"
  assumés comme publicité.
- Distinction stricte **montage vs production** : reprendre une créative existante pour la
  raccourcir/recadrer = du montage (couper des plans MP4 existants, remplacer l'audio) — ne
  JAMAIS générer de nouveau contenu visuel dans ce cas, même partiellement. Confusion survenue
  cette session (Claude Code a généré des images et animations non demandées au lieu de
  simplement monter les plans existants) — voir §3.

---

## 3. BUGS RENCONTRÉS ET RÉSOLUTIONS (EXHAUSTIF, session en cours incluse)

**a-l)** Voir résumé précédent (06/08/2026) pour les bugs du chantier initial (duplication
illustrations maths, désynchro montage/audio, sous-titres superposés, dépassement durée
script, hallucination chiffres, etc.) — tous restés résolus et stables depuis.

**m) Cadrage carte animée trop serré à la fin (chantier motion design, prototype).**
Sur le test Lac Hillier, le zoom final laissait ~70% de l'écran vide (océan), le pin+nom
flottant dans une zone vide, la côte n'occupant que le haut du cadre. Cause : mauvais calcul
du point d'ancrage/l'échelle du zoom final (SCREEN_TARGET Y=0.42 de la hauteur, mal choisi).
Corrigé en remontant l'ancrage à Y=0.58 (le pin étant sur la côte SUD de l'Australie, la terre
est toujours au-dessus du point d'ancrage — remonter le point à l'écran fait mécaniquement
remonter la proportion de terre visible). Validé visuellement après correction. **Reste un
prototype non intégré au pipeline**, pas branché en prod.

**n) Pertinence stock insuffisante sur un vrai test (chantier stock images).**
Sujet "manchot empereur" : Pexels a renvoyé une image de manchot à crête/rockhopper (mauvaise
espèce) en utilisant le filtre "premier résultat non vide". Cause précise : le titre Pexels
retourné contenait le mot générique "penguins" qui matchait la requête, sans distinguer
l'espèce précise attendue (emperor). Deux options proposées (accepter tel quel avec
checkpoint humain existant, vs exiger tous les mots-clés stricte) — la première choisie (voir
§2, limite acceptée et documentée). Compositing cahier Seyès manquant sur les photos stock
identifié et corrigé au même moment (oubli du design initial, la fonction `_try_stock_search`
téléchargeait et s'arrêtait là sans passer par `compose_illustration`).

**o) Dérive linguistique récurrente (portugais).**
Plusieurs occurrences de réponses en portugais dans Claude Code au cours de cette session,
malgré correction ponctuelle à chaque fois. Correction appliquée : règle ajoutée en tête de
CLAUDE.md plutôt qu'une simple instruction en cours de session, dans l'espoir d'une meilleure
persistance à travers les sessions futures. À reconfirmer si la récidive continue.

**p) Dérive de scope catastrophique — créative Ads "méchant/gentil cahier" (remontage).**
Consigne initiale : reprendre la créative originale (~44-47s), garder uniquement les plans
correspondant aux frames validées dans un nouveau script (réduit à 12 frames : 4 monstre + 8
Curio), retirer le reste, remplacer uniquement l'audio par la nouvelle voix off (plus de
lip-sync). Résultat : Claude Code a fini par lancer des générations d'images (GPT Image 2 via
API OpenAI directe après échec Higgsfield faute de crédits) pour des sous-plans qu'il jugeait
nécessiteux de contenu visuel neuf, sans validation explicite de cette extension de scope —
alors que la consigne ne demandait aucune génération, seulement du montage (cut + remplacement
audio) sur des plans MP4 déjà existants dans la version originale. Confusion aggravée par une
étape de "split" de segments audio longs en plusieurs sous-plans visuels (7a/7b, 8a/8b, 10a/10b)
qui a été interprétée à tort comme un besoin de nouveaux visuels distincts par sous-plan,
plutôt qu'une simple répétition du visuel du plan parent. **Statut : consigne reformulée de
façon stricte (interdiction explicite de toute génération, process en 3 étapes séquentielles
avec validation à chaque étape), envoyée mais résultat pas encore confirmé au moment de ce
résumé — à vérifier en priorité à la reprise (voir §7).**

---

## 4. DÉCISIONS TECHNIQUES ET POURQUOI (nouvelles, cette session)

- **Remotion choisi pour les sous-titres plutôt que garder FFmpeg/ASS** : composant prêt à
  l'emploi (`@remotion/captions`, `parseSrt` + `createTikTokStyleCaptions`) correspondant
  exactement au besoin (style pop mot-par-mot façon TikTok), licence gratuite pour l'usage,
  intégration limitée à une seule étape du pipeline (pas un remplacement complet de FFmpeg).
- **Remotion (motion design) reconnu comme plafonné en qualité sans bonne matière première** :
  testé et confirmé — la qualité du rendu dépend fortement de la précision des images sources
  (ex: résolution de carte world-atlas). Conclusion assumée : les comptes Instagram à très
  haute qualité de motion design utilisent probablement du montage humain (After Effects/
  Premiere) ou des agences, pas de la génération 100% automatisée — Remotion reste un choix de
  compromis volume/rapidité vs finition maximale, cohérent avec l'objectif de délégation à
  Tony plutôt que dépendance à un monteur à temps plein.
- **HyperFrames non retenu comme outil principal** (Higgsfield non plus, résilié) — Remotion
  reste l'outil de motion design par défaut, HyperFrames en filet de sécurité seulement.
- **stock_query_en généré dans le même appel Claude que le script** plutôt qu'un appel de
  traduction séparé : évite coût et latence supplémentaires, exploite un appel déjà existant.
- **Filtre de pertinence stock accepté imparfait plutôt que renforcé** : un filtre strict
  (tous les mots-clés obligatoires) ferait chuter le taux de succès stock sur la majorité des
  requêtes (les alt-text Pexels ne reprennent rarement tous les mots d'une requête de 3-5
  mots), annulant le bénéfice principal du chantier (réduction de coût). Le checkpoint de
  validation humaine existant absorbe le risque résiduel.
- **Pas de clonage vocal pour la pub "flash info"** : remplacé par une présentatrice fictive
  clairement publicitaire, pour éviter l'usurpation d'identité et la tromperie sur la nature
  du contenu (pub déguisée en vrai reportage).

---

## 5. ÉTAT ACTUEL EXACT

### Fonctionnel, testé, en prod (curio-automation)
- Pipeline complet curiosités + compétences, inchangé depuis le dernier résumé, toujours
  opérationnel.
- **Sous-titres Remotion** : intégrés dans `video_assembler.py` (flux 3 passes), testés bout en
  bout sur un vrai reel (Toblerone), committés et poussés. Position et taille ajustées et
  validées visuellement par l'utilisateur (pas seulement sur description texte).
- **Recherche d'images stock (Pexels/Wikimedia)** : intégrée dans `image_generator.py`, testée
  bout en bout, committée et poussée. Gain de coût mesuré sur un test réel : 0,033$ vs 0,088$
  si tout GPT Image (~62% d'économie sur ce cas). Compositing cahier appliqué correctement sur
  les photos stock.
- **Fix v2.19** (chemin Remotion + fix Whisper `condition_on_previous_text`) — était en attente
  depuis une session antérieure (13/08), committé et poussé séparément cette session.

### En cours de production (curio-automation)
- **Génération des reels des 17, 18, 19 août** — lancée en fin de session avec les deux
  nouveaux ajouts (stock images + sous-titres repositionnés) en conditions réelles pour la
  première fois combinées. Sujets curiosité à valider par l'utilisateur (3 propositions
  attendues par jour concerné) avant génération. **Statut final non confirmé au moment de ce
  résumé — à vérifier en priorité à la reprise.**

### Prototype, jamais branché au pipeline (curio-automation)
- **5 prototypes motion design carte** (`remotion/src/curio-motion/`, dossiers
  `01-PageFlip.tsx` à `05-ChaosToNotebook.tsx`), 100% isolés, zéro impact sur le pipeline réel.
  **Motion design n°3 identifié comme le meilleur des 5** par l'utilisateur — gardé en local,
  volontairement pas commité (POC, pas prêt pour intégration).
- Prototype d'animation carte "Lac Hillier" (zoom pays → pin → nom), testé et affiné (zoom
  ralenti, départ vue monde, cadrage final corrigé), validé visuellement mais **jamais intégré
  au pipeline de production** — chantier explicitement mis de côté pour privilégier le
  chantier stock images (gain de coût immédiat) et la production ads (urgence).

### Ads Meta — état des deux créatives
- **Créatif 1 "reportage"** : terminé et livré (`06_final/creative1_reportage/
  creative1_v2_avec_soustitres.mp4`, 33s), scripts et voix ElevenLabs (Matilda/Alice/Sarah)
  documentés en mémoire projet.
- **Créatif 2 "méchant/gentil cahier"** : version PRÉCÉDENTE terminée et livrée
  (`06_final/creative2_pixar/creative2_v3_avec_soustitres.mp4`, 43,90s, voix Callum + voix
  custom "gentil"). **EN COURS DE REFONTE** cette session : nouveau script réduit à 12 frames
  précises (voir consigne stricte §3.p), audio ElevenLabs pour les 7 nouvelles phrases généré
  (dossier `05_audio_elevenlabs/creative2_pixar/FINALES/segments_par_plan_script_definitif/`,
  durée réelle mesurée ~49,3s), mais **le montage final (cut des plans + remplacement audio) a
  dérivé vers de la génération non voulue, corrigé par une consigne stricte, résultat pas
  encore confirmé.**
- Le dossier ads n'est pas versionné avec git — aucune action git nécessaire là-dessus.
- CTA motion design du créatif 2 (plan 14 dans l'ancienne version) : en attente de documents
  que l'utilisateur comptait fournir, point resté ouvert depuis plusieurs sessions, pas
  bloquant.

### Pas commencé / mis de côté
- Intégration du motion design carte au pipeline réel (mis de côté volontairement ce soir,
  reprise prévue "demain" selon l'utilisateur).
- Vérification de l'installation effective du skill/agent HyperFrames.
- Agent de décision Pexels/GPT Image "intelligent" évoqué dans les images de contexte (graphique
  manuscrit) — actuellement implémenté comme une logique de règles simples (disqualification par
  mots-clés), pas un agent de décision à part entière plus sophistiqué. À clarifier si
  l'utilisateur veut aller plus loin sur ce point.

---

## 6. CHEMINS DE FICHIERS IMPORTANTS (mise à jour)

```
curio-automation/
├── CLAUDE.md                              ← source de vérité, règle langue française
│                                             ajoutée en tête cette session
├── CONTEXT_SUMMARY.md                     ← ce fichier
├── generators/
│   ├── script_generator.py                ← + champ stock_query_en (Type A illustrations)
│   ├── image_generator.py                 ← + logique décision stock Pexels/Wikimedia/GPT
│   ├── stock_image_search.py              ← NOUVEAU, fonctionnel, testé (Pexels + Wikimedia)
│   ├── video_assembler.py                 ← réécrit, flux 3 passes (FFmpeg → Remotion → FFmpeg)
│   └── subtitle_generator.py              ← inchangé dans sa logique, fix v2.19 appliqué
├── test_stock_image_search.py             ← script de test
├── remotion/                              ← Node/TS isolé, Remotion 4.0.507
│   ├── src/
│   │   ├── Root.tsx                       ← enregistre TikTokCaptions (prod) + 5 compositions
│   │   │                                     curio-motion (prototype, pas en prod)
│   │   ├── tiktok-captions/
│   │   │   ├── TikTokCaptions.tsx         ← composant prod, position/taille ajustées
│   │   │   └── words.ts                   ← approximation mots depuis SRT phrase
│   │   └── curio-motion/                  ← 5 prototypes motion design carte, isolés
│   │       ├── shared.tsx
│   │       ├── 01-PageFlip.tsx à 05-ChaosToNotebook.tsx
│   │       └── MapZoomPin.tsx             ← prototype carte Lac Hillier
│   └── public/curio-motion/*.jpg          ← 4 images Pexels copiées pour tests
├── testing_remotion/                      ← dossier de test, gitignored, versions numérotées
│                                             (v1/v2/v3...), jamais écrasé
└── test_outputs/                          ← ajouté au .gitignore cette session

~/Desktop/Curio /ads_reportage_vs_pixar/   ← PAS un repo git, attention à l'espace dans le nom
├── 01_script/
│   ├── creative1_reportage.md
│   └── creative2_pixar.md                 ← section "TIMELINE RÉELLE" fait foi
├── 05_audio_elevenlabs/creative2_pixar/FINALES/
│   └── segments_par_plan_script_definitif/  ← 12 fichiers audio (4 monstre + 8 Curio)
├── 06_final/
│   ├── creative1_reportage/creative1_v2_avec_soustitres.mp4
│   └── creative2_pixar/creative2_v3_avec_soustitres.mp4  ← ANCIENNE version, avant refonte
└── curio-ads-meta-reportage-pixar.md      ← mémoire projet persistante
```

**Config voix ElevenLabs (Ads)** : créatif 1 = Matilda/Alice/Sarah ; créatif 2 = Callum (monstre)
+ voix custom sauvegardée (gentil/Curio).

**Config voix ElevenLabs (Reels)** : voix "Curio 8", modèle eleven_v3, cible 78-88 mots
(viser 78-82), 28-35s.

---

## 7. QUESTIONS OUVERTES / POINTS BLOQUANTS (priorité en tête)

1. **PRIORITÉ ABSOLUE — Créatif 2 Ads, remontage en cours** : la consigne stricte anti-génération
   a été envoyée mais le résultat n'est pas confirmé au moment de ce résumé. Vérifier en premier
   à la reprise : est-ce que le montage a enfin fonctionné (cut des plans MP4 originaux +
   remplacement audio uniquement, sans aucune génération), ou faut-il reprendre encore.
2. **Génération des reels 17-19 août** : lancée avec les deux nouveaux chantiers combinés
   (stock images + sous-titres repositionnés) pour la première fois en conditions réelles.
   Statut final (sujets curiosité choisis, reels produits, qualité visuelle) non confirmé — à
   vérifier et à regarder attentivement (première utilisation combinée des deux changements).
3. **Motion design carte** : mis de côté explicitement, reprise prévue mais pas encore faite.
   Motion design n°3 identifié comme le meilleur des 5 prototypes — base à reprendre en
   priorité si ce chantier redémarre. Pas encore intégré au pipeline réel.
4. **HyperFrames** : statut d'installation réel non confirmé (l'utilisateur pensait l'avoir
   installé "il y a environ 2 mois" mais ce n'est pas vérifié dans ce repo).
5. **CTA motion design créatif 2 (ancienne version, plan 14)** : documents à fournir par
   l'utilisateur toujours en attente, point ouvert depuis plusieurs sessions, pas bloquant.
6. **Dérive linguistique (portugais)** : correction renforcée (règle en tête de CLAUDE.md)
   appliquée mais pas garantie sur la durée — à surveiller sur les prochaines sessions.
7. **Agent de décision Pexels/GPT Image "avancé"** évoqué par l'utilisateur (schéma manuscrit)
   : la version actuellement implémentée est une logique de règles simples, pas un agent de
   décision élaboré. Écart possible avec l'ambition initiale de l'utilisateur — à clarifier si
   pertinent.

---

*Fin du résumé. Pour toute reprise de travail : lire CLAUDE.md en premier (source de vérité du
code), ce fichier en complément (contexte et historique). Priorité de vérification à la reprise :
point 1 et 2 de la section 7 ci-dessus, qui étaient en cours d'exécution au moment de la coupure.*

---

## 8. MISE À JOUR — 28/08/2026

- **Bug preload MapZoomUyuni corrigé** : l'`<image>` SVG brute utilisée pour la texture carte
  (Blue Marble, géo-alignée sur le zoom/pan) ne bloquait pas le rendu Remotion tant qu'elle
  n'était pas chargée — au tout premier frame de la scène (cut à 20s dans le reel), Remotion
  capturait avant la fin du décodage, laissant un frame quasi vide/glitché. Fix : hook
  `useDelayedImagePreload` (`delayRender`/`continueRender`, `remotion/src/desert-sel/MapZoomUyuni.tsx`).
  Commit `0f3dc94`.
- **Ajout de `motion-catalog.md`** à la racine du projet — catalogue de 90 techniques de motion
  design (caméra/cadrage) pour les reels. Nouvelle règle obligatoire dans CLAUDE.md (§10, v2.20) :
  avant toute génération de motion design sur un reel, segmenter le script en beats et assigner
  une technique du catalogue à CHAQUE beat non-HOOK (aucun beat sans motion assigné), jamais la
  même technique de caméra/cadrage plus de 2 fois consécutives. Commit `31f5d8a`.
