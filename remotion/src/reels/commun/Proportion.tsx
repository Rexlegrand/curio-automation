import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { Captions, useMots } from "../../sahara/captions";
import { Grain, SANS, SERIF, CREAM, OLIVE, FPS } from "../../sahara/shared";

// Beat de proportion : une part écrasante contre un reste minuscule.
//
// Le diptyque `DeuxSols` du sahara ne convient pas ici : il coupe le cadre en
// deux moitiés égales, ce qui dit exactement le contraire d'une part de
// 99,8 %. Une barre dont la hauteur EST la proportion règle le problème — et
// c'est la même raison qui gouverne le beat du chiffre du reel 1 : la
// géométrie à l'écran doit être la géométrie réelle, sinon le plan ment.
//
// La barre se remplit, elle n'apparaît pas : c'est le remplissage qui fait
// sentir jusqu'où ça monte, et l'arrêt brutal à la fin qui montre le peu qui
// reste. Le petit reste est toujours dessiné, même quand il fait deux pixels :
// l'effacer donnerait 100 %, et 100 % n'est pas ce qui est dit.

export type ProportionProps = {
  duration: number;
  segment: string;
  /** Part de la grande masse, en pourcent. */
  part: number;
  /** Les deux noms, et l'unité de la part. */
  labelGrand: string;
  labelPetit: string;
  /** Image où la barre commence à se remplir, où le reste est nommé. */
  remplitFrom: number;
  resteFrom: number;
  couleurGrand?: string;
  couleurPetit?: string;
  fond?: string;
};

const BARRE_TOP = 420;
const BARRE_H = 1160;
const BARRE_W = 520;

export const Proportion: React.FC<ProportionProps> = ({
  duration,
  segment,
  part,
  labelGrand,
  labelPetit,
  remplitFrom,
  resteFrom,
  couleurGrand = "#F5A623",
  couleurPetit = "#7FC7E8",
  fond = "#06070B",
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);

  const remplit = interpolate(frame, [remplitFrom, remplitFrom + 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const reste = interpolate(frame, [resteFrom, resteFrom + 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Le chiffre monte avec la barre : il est lu, pas affiché d'un coup.
  const valeur = part * remplit;
  const hauteurGrand = (BARRE_H * part * remplit) / 100;
  const hauteurPetit = (BARRE_H * (100 - part)) / 100;

  const gauche = (1080 - BARRE_W) / 2;

  return (
    <AbsoluteFill style={{ backgroundColor: fond }}>
      {/* Halo de l'astre derrière la barre : le plan reste dans le sujet, il
          ne devient pas un graphique posé sur du noir. */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(46% 30% at 50% 42%, ${couleurGrand}22 0%, transparent 70%)`,
        }}
      />

      {/* Le contour de la barre est là dès le début, vide : on voit la place
          à remplir avant que ça monte. */}
      <div
        style={{
          position: "absolute",
          left: gauche,
          top: BARRE_TOP,
          width: BARRE_W,
          height: BARRE_H,
          border: "2px solid rgba(255,255,255,0.16)",
          borderRadius: 10,
        }}
      />

      {/* Le reste, tout en bas, toujours dessiné. */}
      <div
        style={{
          position: "absolute",
          left: gauche,
          top: BARRE_TOP + BARRE_H - hauteurPetit,
          width: BARRE_W,
          height: hauteurPetit,
          backgroundColor: couleurPetit,
          borderRadius: "0 0 8px 8px",
        }}
      />

      {/* La grande part, qui se remplit par le bas. */}
      <div
        style={{
          position: "absolute",
          left: gauche,
          top: BARRE_TOP + BARRE_H - hauteurPetit - hauteurGrand,
          width: BARRE_W,
          height: hauteurGrand,
          background: `linear-gradient(180deg, ${couleurGrand} 0%, ${couleurGrand}CC 100%)`,
          borderRadius: "8px 8px 0 0",
        }}
      />

      {/* Le chiffre, dans la barre, au-dessus du niveau atteint. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: BARRE_TOP + 60,
          textAlign: "center",
          opacity: remplit,
        }}
      >
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 118,
            color: CREAM,
            lineHeight: 1,
            textShadow: "0 4px 26px rgba(0,0,0,0.95)",
          }}
        >
          {valeur.toFixed(1).replace(".", ",")} %
        </div>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 40,
            letterSpacing: 7,
            color: CREAM,
            marginTop: 4,
            textShadow: "0 3px 18px rgba(0,0,0,0.95)",
          }}
        >
          {labelGrand}
        </div>
      </div>

      {/* Le reste, nommé à côté de sa bande — trop mince pour porter du texte
          à l'intérieur.
          La largeur est BORNÉE à ce qui reste entre la barre et le bord : sur
          un libellé long, `nowrap` faisait sortir la fin du cadre (constaté
          sur « SOUS LE NIVEAU DE LA MER », coupé à « SOUS LE NIVEA »). Il vaut
          mieux deux lignes qu'une phrase amputée. */}
      <div
        style={{
          position: "absolute",
          left: gauche + BARRE_W + 24,
          width: 1080 - (gauche + BARRE_W + 24) - 24,
          top: BARRE_TOP + BARRE_H - hauteurPetit - 30,
          opacity: reste,
          transform: `translateX(${(1 - reste) * -18}px)`,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 46,
            color: couleurPetit,
            textShadow: "0 3px 18px rgba(0,0,0,0.95)",
          }}
        >
          {(100 - part).toFixed(1).replace(".", ",")} %
        </div>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 26,
            letterSpacing: 3,
            lineHeight: 1.24,
            color: OLIVE,
          }}
        >
          {labelPetit}
        </div>
      </div>

      <Grain frame={frame} opacity={0.08} />
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};
