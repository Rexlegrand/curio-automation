import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Backdrop } from "./backdrop";
import { Captions, useMots } from "./captions";
import { Stage, duoProgress, CurioWindow } from "./stage";
import { Grain, SANS, SERIF, OLIVE, CREAM, FPS, W, H } from "./shared";
import { DUREES, DEUX_SOLS } from "./timing";

// Beat 5 — pourquoi ça compte.
// « Cette poussière contient du phosphore. Un engrais naturel. Sans lui... la
//   pluie laverait le sol de la forêt, et l'appauvrirait. »
//
// Plein écran d'un bout à l'autre. Le diptyque avec/sans a besoin de toute la
// hauteur pour que les deux coupes restent lisibles, et une carte ne s'ouvre
// dans ce reel que pour faire de la place à Curio.
//
// Les deux coupes viennent d'images distinctes, rognées à leur ligne de sol
// par prep_sahara_assets.py : générées séparément, leur surface ne tombait pas
// à la même hauteur et le passage de l'une à l'autre sautait.

// Valeurs du premier montage par défaut, surchargées par le second, qui fait
// précéder le diptyque d'un passage de Curio.
export type DeuxSolsProps = {
  duration: number;
  segment: string;
  wordIn: number;
  split: number;
  /** Pluie sur le panneau du bas. `null` la supprime : elle illustre le
   *  lessivage du sol, elle n'a pas de sens sur un autre sujet. */
  rainFrom: number | null;
  curio?: CurioWindow;
  /** Les deux moitiés du diptyque, dans l'ordre où la phrase les nomme. */
  srcA?: string;
  srcB?: string;
  labelA?: string;
  labelB?: string;
  tintA?: string;
  tintB?: string;
  /** Le mot qui tient le fond avant que le diptyque s'ouvre, et sa légende. */
  word?: string;
  wordSub?: string;
  accent?: string;
  /** Place le grand mot AU-DESSUS du diptyque au lieu de le laisser dans le
   *  fond. Dans le fond, il n'est visible que si le panneau du dessus ne
   *  couvre pas tout le cadre — ce qui n'arrive jamais avant l'ouverture du
   *  diptyque : sur le sahara le mot « Phosphore » ne s'affiche donc pas du
   *  tout (vérifié sur sahara-05-deux-sols_debut.png). Le défaut `false`
   *  garde le comportement du sahara intact ; les reels suivants passent
   *  `true`. */
  wordOnTop?: boolean;
  /** Cadrage des deux moitiés. Les coupes de sol du sahara sont rognées à
   *  leur ligne de sol et s'alignent en haut ; une matière centrée (un objet
   *  isolé sur noir, par exemple) se cadre au centre. */
  objectPosition?: string;
};

/** Pluie : des traits, pas des gouttes rondes. À cette échelle une goutte
 *  photographique ne se lit pas, une traînée oui. */
const Rain: React.FC<{ frame: number; opacity: number }> = ({ frame, opacity }) => {
  const drops = React.useMemo(
    () =>
      new Array(70).fill(0).map((_, i) => ({
        x: (i * 37) % 100,
        delay: (i * 13) % 40,
        speed: 26 + ((i * 7) % 14),
        len: 40 + ((i * 11) % 50),
      })),
    [],
  );
  if (opacity <= 0) return null;
  return (
    <AbsoluteFill style={{ opacity, pointerEvents: "none", overflow: "hidden" }}>
      {drops.map((d, i) => {
        const t = ((frame + d.delay) * d.speed) % 900;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${d.x}%`,
              top: t - 100,
              width: 2,
              height: d.len,
              background:
                "linear-gradient(180deg, rgba(200,220,255,0) 0%, rgba(200,220,255,0.75) 100%)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const SoilPanel: React.FC<{
  src: string;
  label: string;
  tint: string;
  top: string;
  height: string;
  showLabel: boolean;
  objectPosition: string;
}> = ({ src, label, tint, top, height, showLabel, objectPosition }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top, height, overflow: "hidden" }}>
    <Img
      src={staticFile(src)}
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: "100%",
        height: "100%",
        objectFit: "cover",
        // Les deux coupes sont rognées à leur surface : le même objectPosition
        // sur les deux garde la ligne de sol alignée quelle que soit la
        // hauteur de la fenêtre.
        objectPosition,
      }}
    />
    {showLabel ? (
      <div
        style={{
          position: "absolute",
          left: 34,
          top: 22,
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 40,
          letterSpacing: 5,
          color: tint,
          textShadow: "0 3px 14px rgba(0,0,0,0.95)",
        }}
      >
        {label}
      </div>
    ) : null}
  </div>
);

export const DeuxSols: React.FC<DeuxSolsProps> = ({
  duration,
  segment,
  wordIn: wordInFrame,
  split: SPLIT,
  rainFrom: RAIN_FROM,
  curio,
  srcA = "sahara/sol_riche.jpg",
  srcB = "sahara/sol_pauvre.jpg",
  labelA = "AVEC",
  labelB = "SANS",
  tintA = "#9BE0A8",
  tintB = "#E0A98F",
  word = "Phosphore",
  wordSub = "UN ENGRAIS NATUREL",
  accent = "#8C6B2F",
  objectPosition = "50% 0%",
  wordOnTop = false,
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  const t = duoProgress(frame, curio);

  const split = interpolate(frame, [SPLIT, SPLIT + 34], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // En pourcentages : le cadre change de taille sous les panneaux, des pixels
  // les décrocheraient pendant la bascule.
  const richeH = 100 - split * 50;

  const rain =
    RAIN_FROM === null
      ? 0
      : interpolate(frame, [RAIN_FROM, RAIN_FROM + 26], [0, 0.85], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const wordIn = interpolate(frame, [wordInFrame, wordInFrame + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  // Le mot s'efface quand le diptyque s'ouvre : la démonstration prend le relais.
  const wordOut = interpolate(frame, [SPLIT - 16, SPLIT], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const bloqueMot = word ? (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 330,
        textAlign: "center",
        opacity: wordIn * wordOut * (1 - t),
        transform: `scale(${0.94 + 0.06 * wordIn})`,
      }}
    >
      <div style={{ fontFamily: SERIF, fontSize: 124, color: OLIVE }}>{word}</div>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 42,
          letterSpacing: 6,
          color: CREAM,
          marginTop: 6,
        }}
      >
        {wordSub}
      </div>
    </div>
  ) : null;

  return (
    <Stage
      t={t}
      curio={curio}
      background={
        <>
          <Backdrop frame={frame} accent={accent} />
          {wordOnTop ? null : bloqueMot}
        </>
      }
      overlay={
        <>
          {wordOnTop ? bloqueMot : null}
          <Grain frame={frame} opacity={0.08} />
          <Captions mots={mots} frame={frame} fps={FPS} />
        </>
      }
    >
      <SoilPanel
        src={srcA}
        label={labelA}
        tint={tintA}
        objectPosition={objectPosition}
        top="0%"
        height={`${richeH}%`}
        showLabel={split > 0.15}
      />
      {split > 0 ? (
        <SoilPanel
          src={srcB}
          label={labelB}
          tint={tintB}
          objectPosition={objectPosition}
          top={`${richeH}%`}
          height={`${split * 50}%`}
          showLabel={split > 0.35}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: `${richeH}%`,
          bottom: 0,
          overflow: "hidden",
        }}
      >
        <Rain frame={frame} opacity={rain} />
      </div>
    </Stage>
  );
};

export const DeuxSolsComposition: React.FC = () => (
  <Composition
    id="sahara-05-deux-sols"
    component={DeuxSols}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.deuxSols}
    defaultProps={{
      duration: DUREES.deuxSols,
      segment: "mots/05-deux-sols",
      ...DEUX_SOLS,
    }}
  />
);
