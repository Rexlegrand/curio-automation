// Calage du reel « le Sahara nourrit l'Amazonie » sur la narration réelle.
//
// Rien ici n'est choisi à l'œil : chaque durée est celle du segment de voix
// correspondant, et chaque événement tombe sur le mot qui le déclenche, relevé
// par Whisper mot à mot sur `assets/sahara_amazonie/audio/`.
//
// Version 2 de la narration : ponctuation hachée pour que la voix respire,
// et PAUSE images de silence ajoutées après chaque beat. La première version
// enchaînait sans un souffle et le montage semblait couper sec.
//
// Régénérer après toute nouvelle narration : `python build_reel_sahara.py
// --timings` imprime les durées, `python export_mots_sahara.py` les mots.

export const FPS = 30;

/** Silence tenu à la fin de chaque beat. C'est lui qui fait respirer le
 *  montage : sans pause, une phrase démarre sur la dernière syllabe de la
 *  précédente et chaque changement de plan se lit comme une coupe. */
export const PAUSE = 10;

/** Durée de chaque beat = segment de narration + PAUSE. */
export const DUREES = {
  hook: 149, // 4,64 s de voix
  deuxMondes: 286, // 9,20 s
  route: 250, // 8,00 s
  camions: 286, // 9,20 s
  deuxSols: 255, // 8,16 s
  revelation: 444, // 14,48 s
  chute: 195, // 6,16 s
} as const;

/** Beat 1 — le raccord tombe sur « forêt » (3,66 s). */
export const HOOK = { cut: 110 };

/** Beat 2 — « de l'autre » à 5,62 s, « Amazonie » à 6,38 s.
 *  Curio revient pendant « D'un côté, le Sahara... » et laisse l'écran avant
 *  que la seconde fenêtre s'ouvre : les deux carrés et le diptyque
 *  Sahara/Amazonie ne peuvent pas cohabiter. */
export const DEUX_MONDES = {
  topIn: 8,
  bottomIn: 169,
  ruleIn: 212,
  curio: { src: "sahara/curio_studio.mp4", from: 26, to: 150 },
};

/** Beat 3 — « arrache » à 1,58 s, « Atlantique » à 7,30 s : le tracé atteint
 *  l'Amazonie quand le mot tombe, pas après. */
export const ROUTE = {
  revealFrom: 10,
  revealTo: 46,
  originOn: 47,
  arcFrom: 58,
  arcTo: 219,
  targetOn: 210,
};

/** Beat 4 — « 27 millions » est dit dès 0,52 s : le chiffre s'affiche
 *  immédiatement et c'est la flotte qui le rattrape. */
export const CAMIONS = { numberIn: 16 };

/** Beat 5 — « phosphore » à 1,22 s, « Sans » à 3,92 s, « pluie » à 5,14 s.
 *  Plein écran d'un bout à l'autre : le diptyque avec/sans a besoin de toute
 *  la hauteur, et une carte ne s'ouvre que pour Curio. */
export const DEUX_SOLS = { wordIn: 37, split: 118, rainFrom: 154 };

/** Beat 6 — « asséché » à 9,52 s, « sable » à 11,40 s, « algues » à 13,22 s.
 *  Curio revient sur « Et ce phosphore vient d'un endroit précis », puis rend
 *  l'écran pour la descente jusqu'aux diatomées : un zoom continu dans une
 *  carte de 940 px ne se lirait pas, c'est l'échelle qui est le sujet. */
export const REVELATION = {
  curio: { src: "sahara/curio_studio.mp4", from: 18, to: 142 },
  sableFrom: 300,
  diatomeesFrom: 390,
  overlap: 30,
  labelOut: 250,
};

/** Beat 7 — « nourrie » à 3,02 s. La phrase nomme la FORÊT d'abord et le lac
 *  ensuite : l'ordre des plans suit la phrase. */
export const CHUTE = { cut: 91, forestText: 10, lakeText: 100 };

// Les sous-titres n'ont plus de position par beat : ils sont TOUJOURS en bas
// du cadre, comme en production. À mi-hauteur ils barraient le globe en pleine
// rotation et mordaient sur les plans ; il n'existe aucun moment du reel où
// cette place-là les sert.
