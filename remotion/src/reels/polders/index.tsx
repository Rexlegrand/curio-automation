import React from "react";
import { Composition } from "remotion";
import { Hook } from "../../sahara/01-Hook";
import { DeuxMondes } from "../../sahara/02-DeuxMondes";
import { Camions } from "../../sahara/04-Camions";
import { DeuxSols } from "../../sahara/05-DeuxSols";
import { Revelation } from "../../sahara/06-Revelation";
import { Chute } from "../../sahara/07-Chute";
import { ClipSousTitre } from "../../sahara/v-Clip";
import { FPS, W, H } from "../../sahara/shared";
import { Proportion } from "../commun/Proportion";

// Reel 3 de la série — « une partie des Pays-Bas a été prise à la mer ».
//
// Le reel le plus économique de la série : SEPT beats sur sept sortent de
// composants déjà écrits, aucun n'est neuf. Six viennent du sahara, le
// septième — `Proportion` — a été écrit pour le reel 2 et rangé dans
// `reels/commun/` en prévision exactement de ce cas.
//
// Le beat du chiffre est de nouveau la flotte : une ferme néerlandaise à la
// place du camion, à perte de vue sur l'ancien fond marin. C'est le troisième
// sujet que ce même composant sert, sans qu'une ligne de sa logique 3D ait
// bougé.
//
// Durées : `python build_reel.py polders --timings`. Calages : transcription
// mot à mot, mot déclencheur en commentaire.

const P = "reels/polders";
const M = `${P}/mots`;

// Vert-de-gris du Nord : ni l'or du sahara, ni le bleu des Mariannes.
const ACCENT = "#3E6B57";
const EAU = "#5FA8C7";

export const DUREES = {
  hook: 87,
  hookSuite: 106,
  deuxMondes: 250,
  digue: 284,
  chiffre: 197,
  niveau: 224,
  revelation: 291,
  chute: 130,
  cta: 132,
} as const;

export const PoldersCompositions: React.FC = () => (
  <>
    <Composition
      id="polders-hook"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.hook}
      defaultProps={{
        src: `${P}/hook_video.mp4`,
        segment: `${M}/00-hook`,
        duration: DUREES.hook,
      }}
    />

    <Composition
      id="polders-hook-suite"
      component={Hook}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.hookSuite}
      defaultProps={{
        duration: DUREES.hookSuite,
        segment: `${M}/01-hook-suite`,
        cut: 68, // « était », 2,27 s — la phrase bascule au passé, l'image aussi
        srcA: `${P}/polder_champs.jpg`,
        srcB: `${P}/mer_du_nord.jpg`,
        overlaySrc: "",
        line: "Une grande partie des Pays-Bas",
        keyword: "était sous l'eau",
      }}
    />

    <Composition
      id="polders-deux-mondes"
      component={DeuxMondes}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.deuxMondes}
      defaultProps={{
        duration: DUREES.deuxMondes,
        segment: `${M}/02-deux-mondes`,
        topIn: 8,
        bottomIn: 69, // « De l'autre », 2,30 s
        ruleIn: 202, // « Au même endroit », 6,73 s
        topSrc: `${P}/mer_du_nord.jpg`,
        botSrc: `${P}/polder_champs.jpg`,
        topLabel: "LA MER DU NORD",
        botLabel: "DES CHAMPS",
        // La mesure de l'écart n'est pas une distance ici : les deux mondes
        // sont au MÊME endroit, c'est tout le sujet du beat.
        badge: "même endroit",
        accent: ACCENT,
        curio: { src: `${P}/curio_studio.mp4`, from: 8, to: 60 },
      }}
    />

    <Composition
      id="polders-digue"
      component={Revelation}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.digue}
      defaultProps={{
        duration: DUREES.digue,
        segment: `${M}/03-digue`,
        // De l'orbite à la digue : le même geste que le beat 6 du sahara, qui
        // descendait de l'orbite au microscope. On voit d'abord OÙ, puis QUOI.
        layers: [
          { src: `${P}/carte_zuiderzee.jpg`, from: 0, until: 130, zoomFrom: 1.0, zoomTo: 1.8 },
          // « Trente-deux kilomètres de mur », 2,17 s.
          { src: `${P}/digue.jpg`, from: 130, until: 284, zoomFrom: 0.9, zoomTo: 1.4 },
        ],
        overlap: 30,
        accent: ACCENT,
        curio: { src: `${P}/curio_studio.mp4`, from: 8, to: 60 },
      }}
    />

    <Composition
      id="polders-chiffre"
      component={Camions}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chiffre}
      defaultProps={{
        duration: DUREES.chiffre,
        segment: `${M}/04-chiffre`,
        numberIn: 26, // « près de mille cinq cents », 0,87 s
        texture: `${P}/ferme.png`,
        // La ferme est presque aussi haute que large, comme la Terre du reel 2
        // et à la différence du camion : même réglage.
        objetLargeur: 2.5,
        nombre: "1 500 km²",
        legende: "SORTIS DE L'EAU",
        // Vert et gris du Nord, et le bas rejoint la brume pour que la
        // première rangée repose sur quelque chose.
        degrade: "linear-gradient(180deg, #223A31 0%, #1B2E27 52%, #16241F 100%)",
        brume: "#16241F",
        accent: ACCENT,
        legendeCouleur: "#9BD8B0",
      }}
    />

    <Composition
      id="polders-niveau"
      component={DeuxSols}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.niveau}
      defaultProps={{
        duration: DUREES.niveau,
        segment: `${M}/05-niveau`,
        wordIn: 10, // « Sans ces digues », 0,00 s
        split: 52, // « la mer reprendrait tout », 1,73 s
        // Ici la pluie a un sens — c'est le seul reel de la série où le
        // composant retrouve son usage d'origine, l'eau qui tombe sur la
        // terre. Elle arrive avec la moitié noyée.
        rainFrom: 70,
        srcA: `${P}/polder_sec.jpg`,
        srcB: `${P}/polder_noye.jpg`,
        labelA: "AVEC LES DIGUES",
        labelB: "SANS",
        tintA: "#9BE0A8",
        tintB: "#7FC7E8",
        word: "Sans les digues",
        wordSub: "LA MER REPREND TOUT",
        accent: ACCENT,
        objectPosition: "50% 50%",
        wordOnTop: true,
      }}
    />

    <Composition
      id="polders-revelation"
      component={Proportion}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.revelation}
      defaultProps={{
        duration: DUREES.revelation,
        segment: `${M}/06-revelation`,
        // 26 % du territoire est sous le niveau de la mer. C'est la petite
        // part qui porte le sens ici, à l'inverse du reel 2 : la barre montre
        // les trois quarts au-dessus, et c'est le quart du bas qu'on nomme.
        part: 74,
        labelGrand: "AU-DESSUS DE LA MER",
        labelPetit: "SOUS LE NIVEAU DE LA MER",  // tient sur deux lignes
        remplitFrom: 34, // « un quart du pays », 1,13 s
        resteFrom: 89, // « mer », 2,97 s
        couleurGrand: "#7FA88C",
        couleurPetit: EAU,
        fond: "#0A0F12",
      }}
    />

    <Composition
      id="polders-chute"
      component={Chute}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chute}
      defaultProps={{
        duration: DUREES.chute,
        segment: `${M}/07-chute`,
        cut: 83, // « où », 2,77 s — la phrase bascule sur les poissons
        // L'ordre suit la phrase : on MARCHE d'abord, les poissons ensuite.
        srcA: `${P}/flevoland.jpg`,
        srcB: `${P}/mer_du_nord.jpg`,
        line: "Un pays où l'on marche",
        keyword: "là où nageaient les poissons",
        firstFrom: 8,
        secondFrom: 83,
      }}
    />

    <Composition
      id="polders-cta"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.cta}
      defaultProps={{
        src: `${P}/curio_cta.mp4`,
        segment: `${M}/08-cta`,
        duration: DUREES.cta,
      }}
    />
  </>
);
