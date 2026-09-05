import React from "react";
import { Composition } from "remotion";
import { Hook } from "../../sahara/01-Hook";
import { DeuxMondes } from "../../sahara/02-DeuxMondes";
import { DeuxSols } from "../../sahara/05-DeuxSols";
import { Revelation } from "../../sahara/06-Revelation";
import { Chute } from "../../sahara/07-Chute";
import { ClipSousTitre } from "../../sahara/v-Clip";
import { FPS, W, H } from "../../sahara/shared";
import { Descente } from "./Descente";
import { EchelleVerticale } from "./EchelleVerticale";

// Reel 1 de la série — « la fosse des Mariannes ».
//
// Cinq des sept beats sont ceux du sahara, paramétrés : le raccord sec du
// hook, le diptyque des deux mondes, le diptyque avec/sans, la descente en
// échelles emboîtées et la chute. Rien n'est recopié — les composants portent
// désormais leurs images et leurs textes en props, et le sahara garde les
// siens en valeurs par défaut.
//
// Deux beats sont propres à ce reel et n'ont pas d'équivalent dans le sahara :
//   - `Descente`, le mécanisme : on s'enfonce, donc une translation et non un
//     zoom ;
//   - `EchelleVerticale`, le chiffre : l'Everest posé au fond de la fosse.
//     C'est le pic du reel, l'équivalent des vingt-sept millions de tonnes.
//
// Toutes les durées sont celles de la narration, imprimées par
// `python build_reel.py mariannes --timings` — jamais posées au jugé.
// Tous les calages sont relevés sur la transcription mot à mot
// (`remotion/public/reels/mariannes/mots/`), le mot déclencheur est en
// commentaire à chaque fois.

const P = "reels/mariannes";
const M = `${P}/mots`;

// Bleu froid : l'accent du fond de l'état carte. L'or du sahara appartient au
// désert, il jurerait sous l'eau.
const ACCENT = "#2E5F7A";

export const DUREES = {
  hook: 108,
  hookSuite: 183,
  deuxMondes: 281,
  descente: 300,
  chiffre: 195,
  pression: 284,
  revelation: 303,
  chute: 140,
  cta: 116,
} as const;

// Géométrie réelle, vérifiée le 2026-09-03. Le beat du chiffre en dérive
// entièrement : c'est parce qu'une seule échelle gouverne la colonne d'eau et
// la montagne qu'on a le droit de dire « il reste deux kilomètres ».
const FOND_METRES = 10935; // Challenger Deep
const EVEREST_METRES = 8849;

export const MariannesCompositions: React.FC = () => (
  <>
    <Composition
      id="mariannes-hook"
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
      id="mariannes-hook-suite"
      component={Hook}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.hookSuite}
      defaultProps={{
        duration: DUREES.hookSuite,
        segment: `${M}/01-hook-suite`,
        cut: 91, // « creux », 3,04 s
        srcA: `${P}/surface.jpg`,
        srcB: `${P}/abysse.jpg`,
        overlaySrc: `${P}/particules.jpg`,
        line: "L'endroit le plus profond de la Terre",
        keyword: "11 000 m",
      }}
    />

    <Composition
      id="mariannes-deux-mondes"
      component={DeuxMondes}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.deuxMondes}
      defaultProps={{
        duration: DUREES.deuxMondes,
        segment: `${M}/02-deux-mondes`,
        topIn: 8,
        bottomIn: 139, // « De l'autre », 4,62 s
        ruleIn: 171, // « onze kilomètres », 5,70 s
        topSrc: `${P}/surface.jpg`,
        botSrc: `${P}/abysse.jpg`,
        topLabel: "SURFACE",
        botLabel: "MARIANNES",
        badge: "11 000 m",
        accent: ACCENT,
        // Curio tient la carte haute pendant la moitié de phrase qui ne parle
        // que de la surface, et rend l'écran avant que la seconde fenêtre
        // s'ouvre : les deux formats ne peuvent pas cohabiter.
        curio: { src: `${P}/curio_studio.mp4`, from: 20, to: 132 },
      }}
    />

    <Composition
      id="mariannes-descente"
      component={Descente}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.descente}
      defaultProps={{
        duration: DUREES.descente,
        segment: `${M}/03-descente`,
        layers: [`${P}/surface.jpg`, `${P}/penombre.jpg`, `${P}/abysse.jpg`],
        // Le compteur passe par ces points : 200 m quand la voix dit « deux
        // cents mètres » (1,76 s), 1 000 m quand elle dit « mille » (5,34 s).
        paliers: [
          [53, 200],
          [160, 1000],
        ],
        fondFrom: 252, // « dixième du chemin », 8,40 s
        fondMetres: FOND_METRES,
      }}
    />

    <Composition
      id="mariannes-chiffre"
      component={EchelleVerticale}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chiffre}
      defaultProps={{
        duration: DUREES.chiffre,
        segment: `${M}/04-chiffre`,
        fond: FOND_METRES,
        montagne: EVEREST_METRES,
        chiffreIn: 11, // « kilomètres », 0,36 s
        chuteFrom: 46, // « l'Everest », 1,52 s
        ecartFrom: 98, // « il reste encore », 3,26 s
      }}
    />

    <Composition
      id="mariannes-pression"
      component={DeuxSols}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.pression}
      defaultProps={{
        duration: DUREES.pression,
        segment: `${M}/05-pression`,
        wordIn: 70, // « Mille fois », 2,34 s
        split: 149, // « L'équivalent », 4,98 s
        // Pas de pluie : elle illustre le lessivage d'un sol, elle n'a aucun
        // sens à onze mille mètres sous l'eau.
        rainFrom: null,
        srcA: `${P}/gobelet_avant.jpg`,
        srcB: `${P}/gobelet_apres.jpg`,
        labelA: "EN SURFACE",
        labelB: "AU FOND",
        tintA: "#9BD8E0",
        tintB: "#E0A98F",
        word: "1 000 fois",
        wordSub: "LA PRESSION DE LA SURFACE",
        accent: ACCENT,
        // Deux objets isolés sur noir : ils se cadrent au centre, là où les
        // coupes de sol du sahara s'alignaient sur leur ligne de surface.
        objectPosition: "50% 50%",
        // Sans ça le grand mot passe DERRIÈRE le panneau plein cadre et ne
        // s'affiche jamais — le défaut du sahara, cf. 05-DeuxSols.tsx.
        wordOnTop: true,
        curio: { src: `${P}/curio_studio.mp4`, from: 8, to: 66 },
      }}
    />

    <Composition
      id="mariannes-revelation"
      component={Revelation}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.revelation}
      defaultProps={{
        duration: DUREES.revelation,
        segment: `${M}/06-revelation`,
        // Deux échelles seulement, là où le sahara en enchaînait trois : le
        // sujet est qu'il y a quelque chose de vivant là où on n'attend rien,
        // pas un changement d'ordre de grandeur. On s'approche, on ne descend
        // plus — la descente, c'était le beat 3.
        layers: [
          { src: `${P}/fond_fosse.jpg`, from: 0, until: 90, zoomFrom: 1.0, zoomTo: 1.7 },
          // « Des poissons transparents », 2,90 s.
          { src: `${P}/poisson.jpg`, from: 90, until: 303, zoomFrom: 0.85, zoomTo: 1.5 },
        ],
        overlap: 30,
        accent: ACCENT,
        curio: { src: `${P}/curio_studio.mp4`, from: 10, to: 80 },
      }}
    />

    <Composition
      id="mariannes-chute"
      component={Chute}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chute}
      defaultProps={{
        duration: DUREES.chute,
        segment: `${M}/07-chute`,
        cut: 73, // « n'est pas », 2,42 s
        // L'ordre des plans suit la phrase : elle nomme le NOIR d'abord et la
        // vie ensuite. Le sahara avait fait l'inverse et la transcription mot
        // à mot l'avait montré.
        srcA: `${P}/abysse.jpg`,
        srcB: `${P}/poisson.jpg`,
        line: "L'endroit le plus noir de la planète",
        keyword: "n'est pas un endroit mort",
        firstFrom: 8,
        secondFrom: 73,
      }}
    />

    <Composition
      id="mariannes-cta"
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
