// Calage du SECOND montage — « le Sahara nourrit l'Amazonie », version 2.
//
// Même matière, autre ordre : on part du chiffre, on remonte à l'origine, puis
// on explique. L'ordre d'une enquête plutôt que celui d'un exposé — et surtout
// un ordre qui donne au montage son alternance : chaque bloc d'explication
// appelle Curio dans la carte du haut, chaque preuve reprend le plein écran.
//
// Ici le SWITCH est la ligne directrice, pas un effet posé sur un montage
// existant. Trois passages en deux carrés, répartis sur les trois quarts du
// reel, chacun sur une phrase d'explication et jamais sur une démonstration.
//
// Durées et mots relevés sur assets/sahara_amazonie/audio2/.

export const FPS = 30;
export const PAUSE = 10;

export const DUREES2 = {
  chiffre: 308, // 9,92 s de voix
  origine: 308, // 9,92 s
  algues: 154, // 4,80 s
  voyage: 252, // 8,08 s
  phosphore: 238, // 7,60 s
  chute: 137, // 4,24 s
} as const;

const CURIO = "sahara/curio_studio.mp4";

/** Beat 1 — le chiffre. « millions » à 1,44 s, « camions » à 7,28 s.
 *  Curio annonce le chiffre, puis rend l'écran à la flotte : c'est elle la
 *  démonstration, elle ne peut pas tenir dans une carte. */
export const V2_CHIFFRE = {
  numberIn: 40,
  curio: { src: CURIO, from: 14, to: 150 },
};

/** Beat 2 — l'origine. « Bodélé » à 3,86 s, « Tchad » à 4,78 s, « lac » à
 *  6,06 s. Curio pose la question, la vue satellite répond en plein écran. */
export const V2_ORIGINE = {
  curio: { src: CURIO, from: 8, to: 112 },
  labelIn: 120,
};

/** Beat 3 — les algues. Plein écran d'un bout à l'autre : la descente du sable
 *  aux diatomées est une affaire d'échelle, une carte la tuerait.
 *  « squelettes » à 2,86 s. */
export const V2_ALGUES = { diatomeesFrom: 86, overlap: 26 };

/** Beat 4 — le voyage. « arrache » à 0,58 s, « Atlantique » à 5,72 s. */
export const V2_VOYAGE = {
  revealFrom: 6,
  revealTo: 40,
  originOn: 17,
  arcFrom: 30,
  arcTo: 172,
  targetOn: 164,
};

/** Beat 5 — le phosphore. « phosphore » à 1,26 s, « Sans » à 4,20 s, « pluie »
 *  à 5,42 s. Curio explique, puis le diptyque avec/sans prend l'écran au mot
 *  « Sans » — la bascule part avant lui, de la durée du mouvement. */
export const V2_PHOSPHORE = {
  curio: { src: CURIO, from: 8, to: 115 },
  wordIn: 38,
  split: 126,
  rainFrom: 163,
};

/** Beat 6 — la chute. « nourrie » à 2,70 s : le raccord forêt → lac tombe
 *  dessus, comme dans le premier montage. */
export const V2_CHUTE = { cut: 81 };
