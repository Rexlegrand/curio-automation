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

// Reel 2 de la série — « le Soleil, c'est presque tout le système solaire ».
//
// Six des sept beats sortent du sahara, paramétrés. Le beat du chiffre est le
// plus littéral des réemplois : c'est la FLOTTE DE CAMIONS, avec la Terre à la
// place du camion. Un champ d'objets identiques qui fuit vers l'horizon
// jusqu'à ce que le cadre n'en montre plus la fin — la démonstration est la
// même, seul l'objet change.
//
// Un seul composant est neuf, `Proportion`, et il ne l'est pas pour ce reel en
// particulier : le diptyque `DeuxSols` coupe le cadre en deux moitiés égales,
// ce qui dit exactement le contraire d'une part de 99,8 %. Il vit donc dans
// `reels/commun/`.
//
// Toutes les durées viennent de `python build_reel.py soleil --timings`, tous
// les calages de la transcription mot à mot ; le mot déclencheur est en
// commentaire à chaque fois.

const P = "reels/soleil";
const M = `${P}/mots`;

// Ocre chaud : l'accent du fond de l'état carte, tiré du sujet.
const ACCENT = "#8C5A1F";
const OR = "#F5A623";

export const DUREES = {
  hook: 118,
  hookSuite: 140,
  deuxMondes: 264,
  balance: 305,
  chiffre: 166,
  jupiter: 286,
  revelation: 286,
  chute: 149,
  cta: 125,
} as const;

export const SoleilCompositions: React.FC = () => (
  <>
    <Composition
      id="soleil-hook"
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
      id="soleil-hook-suite"
      component={Hook}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.hookSuite}
      defaultProps={{
        duration: DUREES.hookSuite,
        segment: `${M}/01-hook-suite`,
        cut: 57, // « Soleil », 1,90 s
        srcA: `${P}/planetes.jpg`,
        srcB: `${P}/soleil_plein.jpg`,
        // Pas de calque soufflé : la poussière du sahara illustrait le vent,
        // il n'y a rien à faire souffler dans le vide.
        overlaySrc: "",
        line: "Le système solaire",
        keyword: "c'est le Soleil",
      }}
    />

    <Composition
      id="soleil-deux-mondes"
      component={DeuxMondes}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.deuxMondes}
      defaultProps={{
        duration: DUREES.deuxMondes,
        segment: `${M}/02-deux-mondes`,
        topIn: 8,
        bottomIn: 174, // « De l'autre », 5,80 s
        ruleIn: 217, // « une seule étoile », 7,22 s
        topSrc: `${P}/planetes.jpg`,
        botSrc: `${P}/soleil_disque.jpg`,
        topLabel: "8 PLANÈTES",
        botLabel: "1 ÉTOILE",
        badge: "99,8 %",
        accent: ACCENT,
        curio: { src: `${P}/curio_studio.mp4`, from: 20, to: 166 },
      }}
    />

    <Composition
      id="soleil-balance"
      component={Proportion}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.balance}
      defaultProps={{
        duration: DUREES.balance,
        segment: `${M}/03-balance`,
        part: 99.8,
        labelGrand: "LE SOLEIL",
        labelPetit: "TOUT LE RESTE",
        remplitFrom: 56, // « Le Soleil pèse », 1,88 s
        resteFrom: 206, // « Tout le reste », 6,88 s
        couleurGrand: OR,
        couleurPetit: "#7FC7E8",
      }}
    />

    <Composition
      id="soleil-chiffre"
      component={Camions}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chiffre}
      defaultProps={{
        duration: DUREES.chiffre,
        segment: `${M}/04-chiffre`,
        numberIn: 85, // « un million », 2,82 s
        texture: `${P}/terre.png`,
        // La Terre est ronde, le camion était deux fois plus large que haut.
        // Un premier essai à 1,8 les rendait trop petites : la flotte tenait
        // dans un bandeau au milieu du cadre et flottait sur du noir.
        objetLargeur: 2.5,
        nombre: "1 300 000",
        legende: "TERRES DANS LE SOLEIL",
        // Le bas du dégradé rejoint la couleur de la brume : sinon la
        // première rangée se découpe sur du noir et la flotte ne repose sur
        // rien.
        degrade: "linear-gradient(180deg, #2A1405 0%, #221002 52%, #1A0E04 100%)",
        brume: "#1A0E04",
        accent: ACCENT,
        legendeCouleur: OR,
      }}
    />

    <Composition
      id="soleil-jupiter"
      component={DeuxSols}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.jupiter}
      defaultProps={{
        duration: DUREES.jupiter,
        segment: `${M}/05-jupiter`,
        wordIn: 97, // « mille fois », 3,24 s
        split: 163, // « Et à elle seule », 5,42 s
        rainFrom: null,
        srcA: `${P}/jupiter.jpg`,
        srcB: `${P}/planetes.jpg`,
        labelA: "JUPITER",
        labelB: "LES 7 AUTRES",
        tintA: "#F0C48A",
        tintB: "#9BD8E0",
        word: "1 000 fois",
        wordSub: "PLUS LÉGÈRE QUE LE SOLEIL",
        accent: ACCENT,
        objectPosition: "50% 50%",
        wordOnTop: true,
        curio: { src: `${P}/curio_studio.mp4`, from: 8, to: 82 },
      }}
    />

    <Composition
      id="soleil-revelation"
      component={Revelation}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.revelation}
      defaultProps={{
        duration: DUREES.revelation,
        segment: `${M}/06-revelation`,
        // On est SUR notre étoile, puis on recule et une géante l'écrase.
        // C'est le mouvement inverse du sahara, qui descendait vers le
        // microscope — ici l'échelle se prend en s'éloignant.
        layers: [
          { src: `${P}/granulation.jpg`, from: 0, until: 190, zoomFrom: 1.4, zoomTo: 1.0 },
          // « Il en existe de mille fois plus larges », 6,74 s.
          { src: `${P}/geante_rouge.jpg`, from: 190, until: 286, zoomFrom: 0.85, zoomTo: 1.25 },
        ],
        overlap: 30,
        accent: ACCENT,
        curio: { src: `${P}/curio_studio.mp4`, from: 10, to: 84 },
      }}
    />

    <Composition
      id="soleil-chute"
      component={Chute}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES.chute}
      defaultProps={{
        duration: DUREES.chute,
        segment: `${M}/07-chute`,
        cut: 60, // « est », 2,00 s
        srcA: `${P}/soleil_plein.jpg`,
        srcB: `${P}/geante_rouge.jpg`,
        line: "L'astre qui écrase tout notre système",
        keyword: "est une étoile ordinaire",
        firstFrom: 8,
        secondFrom: 60,
      }}
    />

    <Composition
      id="soleil-cta"
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
