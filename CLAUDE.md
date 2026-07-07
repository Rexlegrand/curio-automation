# Curio Automation — Spec maître

Ce fichier est la **seule source de vérité** du projet. Toute évolution du projet
se fait en **réécrivant ce fichier en entier**, jamais en empilant des sections
au-dessus de l'existant. Si une règle change, elle remplace l'ancienne — elle ne
s'ajoute pas à côté.

**Pourquoi cette règle existe** : une version précédente du projet a accumulé du
code en couches successives (nouvelles consignes ajoutées par-dessus des anciennes
jamais retirées), ce qui a fini par produire des résultats incohérents. On ne
reproduit pas ce problème ici.

## Objectif

Assistant de production qui automatise la création de Réels Instagram/TikTok pour
Curio, du script à la vidéo montée. Objectif juillet 2026 : produire vite et sans
erreur, avec validation humaine à chaque étape clé. L'automatisation 100% autonome
(sans validation humaine) est un objectif de phase 2 (août 2026+), pas de maintenant.

Cible : un Réel produit en **30 minutes maximum**, du choix du sujet à la vidéo
finale prête à poster.

## Types de contenu

1. **Curiosité** — contenu principal, sujets tirés du tableau Excel fourni par
   Tony (référent Curio) et du cahier de sujets personnel.
2. **Compétences** — français et mathématiques, tous niveaux CP à CM2.

## Pipeline de production

Chaque étape a un **point de validation humaine explicite**. On ne passe à
l'étape suivante que si l'étape précédente est validée. Pas d'étape sautée, pas
d'étape qui avance "en attendant" la validation de la précédente.

### Étape 1 — Script et prompts

Claude propose, dans un seul fichier texte léger (`.txt` ou `.md`, pas de format
lourd) :
- le script audio complet (texte à dire par Curio)
- le prompt image pour le hook (GPT Image)
- le prompt vidéo pour le hook (Seedance 2.0, 4s, format 9:16)
- les prompts des 3 illustrations de structure
- le concept de la miniature

**Validation humaine** : cohérence du sujet, qualité du copywriting, pertinence
des prompts. Si refusé → on reste à l'étape 1, pas d'avance en parallèle.

### Étape 2 — Génération images + audio (en parallèle)

- **Images** : générées via GPT Image, à partir d'une image de référence PNG
  obligatoire à chaque génération (voir section Images).
- **Audio** : générées via ElevenLabs, voix n°8 (voix Curio). **Toujours générer
  2 versions** — l'humain choisit la meilleure.

**Validation humaine** : les images correspondent-elles à la trame ? L'audio
choisi est-il bon ?

### Étape 3 — Rendu vidéo (hook + structure)

L'utilisateur génère manuellement les vidéos (hook et structure, via Seedance)
à partir des illustrations validées, puis dépose le tout dans un dossier de
validation finale nommé d'après le Réel (voir Arborescence).

### Étape 4 — Montage final

Claude Code (via hyperframes) assemble le montage final : dynamique, sous-titres
correctement dimensionnés dans la zone de sécurité (ni trop petits — doivent
rester lisibles —, ni empiétant sur la zone occupée par les likes/commentaires/
nom de compte à l'écran).

## Séquence vidéo (ordre fixe, ne pas dévier)

1. Hook vidéo — 4s, Seedance 2.0, 9:16, Curio face caméra
2. Illustration 1
3. Vidéo structure 1 — Curio face caméra
4. Illustration 2
5. Vidéo structure 2 — Curio face caméra
6. Illustration 3
7. CTA — Curio face caméra

Total images GPT à générer par Réel : **5 à 6** (1 hook + 3 structure +
1 miniature, + éventuel visuel CTA si besoin).

Durée cible finale : **25 à 30 secondes**, 30s = maximum absolu.

## Spécifications images

- Style **hyper-réaliste** par défaut — comme des photos qu'on trouverait sur
  Wikipédia ou en photothèque. Aucune apparition du personnage Curio dans les
  illustrations (Curio n'apparaît qu'en vidéo — hook/structure/CTA — et en logo
  sur la miniature).
- Exception : illustrations de type diagramme explicatif (chiffres, flèches,
  symboles simples, un peu de texte) — toujours dans un rendu hyper-réaliste,
  jamais cartoon/illustratif.
- **Référence PNG obligatoire à chaque génération**, sans exception. C'est ce qui
  garantit que la qualité ne se dégrade pas dans le temps. Une génération sans
  image de référence n'est pas conforme au process.
- Contrainte de coût : **10 à 15 centimes maximum par image**. Si le rendu GPT
  Image en qualité standard produit des images de mauvaise qualité (rendu qui ne
  respecte pas le prompt), le problème est à investiguer côté prompt engineering
  et paramétrage des settings OpenAI — pas en montant en gamme de qualité si ça
  fait exploser le coût.

## Miniature

Composée à partir d'une ou deux images utilisées dans le Réel + petit logo Curio
en bas. Seul endroit où Curio apparaît visuellement de façon statique (hors
vidéo). Utilisée pour le feed Instagram — doit rester homogène avec les autres
miniatures publiées.

## Spécifications audio

- ElevenLabs, voix n°8 (voix officielle Curio).
- Toujours 2 générations par script — choix humain de la meilleure prise.

## Contenu source

- Tableau Excel fourni par Tony (référent Curio) — liste de sujets Curiosité.
- Cahier personnel de sujets (idées à traiter en complément).
- Objectif : maximiser le volume de contenu produit sur juillet 2026.

## Arborescence par Réel

```
projects/<nom_du_reel>/
  script.txt              # script + tous les prompts (étape 1)
  illustrations/
  hook/
  audio/
  final/                  # dossier de validation finale (étape 3 → 4)
```

## Stack technique

- Python pour la génération (script, images, audio, sous-titres, description).
- [hyperframes](https://github.com/heygen-com/hyperframes) (outil externe, basé
  Remotion) pour le montage final — cloné en local, jamais versionné dans ce
  repo (trop volumineux, c'est une dépendance externe, pas du code du projet).
- `.env` contient les clés API (OpenAI, ElevenLabs, Seedance/autres) — jamais
  committé, voir `.env.template` pour la liste des variables attendues.

## Roadmap

- **Juillet 2026** : automatisation assistée — gain de temps sur la production,
  validation humaine à chaque étape, pas d'objectif d'autonomie complète.
- **Août 2026+** (phase 2, hors scope actuel) : évaluer le passage vers une
  automatisation 100% autonome sans validation humaine.
