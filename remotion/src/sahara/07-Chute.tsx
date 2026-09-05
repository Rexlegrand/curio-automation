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
import { Grain, Vignette, drift, SANS, SERIF, OLIVE, CREAM, FPS, W, H } from "./shared";
import { Captions, useMots } from "./captions";
import { DUREES, CHUTE } from "./timing";

// Beat 7 — la chute.
// « La forêt la plus vivante de la planète est nourrie par un lac mort il y a
//   des milliers d'années. »
//
// La phrase nomme la FORÊT d'abord et le lac ensuite : « La forêt la plus
// vivante de la planète est nourrie par un lac mort il y a des milliers
// d'années. » L'image suit cet ordre-là. Elle faisait l'inverse — lac puis
// forêt — jusqu'à ce que la transcription mot à mot le montre : on voyait un
// lac pendant qu'on entendait « forêt ».
//
// Le raccord tombe sur « nourrie » (2,70 s), le mot qui fait basculer la
// phrase d'un terme à l'autre. Le mouvement de caméra le traverse sans changer
// de vitesse, comme au beat 1 — les deux extrémités du reel se répondent.

export type ChuteProps = {
  duration: number;
  segment: string;
  cut: number;
  /** Les deux plans, dans l'ordre où la phrase les nomme. */
  srcA?: string;
  srcB?: string;
  /** Les deux moitiés de la phrase de chute, la seconde en serif. */
  line?: string;
  keyword?: string;
  /** Images d'entrée des deux moitiés, calées sur les mots. */
  firstFrom?: number;
  secondFrom?: number;
};

export const Chute: React.FC<ChuteProps> = ({
  duration,
  segment,
  cut: CUT,
  srcA = "sahara/canopee.jpg",
  srcB = "sahara/lac_asseche.jpg",
  line = "La forêt la plus vivante de la planète",
  keyword = "nourrie par un lac mort",
  firstFrom = CHUTE.forestText,
  secondFrom = CHUTE.lakeText,
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  const forest = frame < CUT;

  const zoom = drift(frame, duration, 1.04, 1.17);
  const slide = drift(frame, duration, 22, -22);

  const first = interpolate(frame, [firstFrom, firstFrom + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const second = interpolate(frame, [secondFrom, secondFrom + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0A09" }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={staticFile(forest ? srcA : srcB)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${zoom}) translateX(${slide}px)`,
          }}
        />
      </AbsoluteFill>

      <Vignette strength={0.66} />
      <Grain frame={frame} />
      <Captions mots={mots} frame={frame} fps={FPS} />

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 300,
          textAlign: "center",
          padding: "0 70px",
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 46,
            color: CREAM,
            lineHeight: 1.24,
            textShadow: "0 3px 18px rgba(0,0,0,0.95)",
            opacity: first,
            transform: `translateY(${(1 - first) * -12}px)`,
          }}
        >
          {line}
        </div>
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 96,
            color: OLIVE,
            lineHeight: 1.08,
            marginTop: 14,
            textShadow: "0 5px 28px rgba(0,0,0,0.98)",
            opacity: second,
            transform: `scale(${0.93 + 0.07 * second})`,
          }}
        >
          {keyword}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const ChuteComposition: React.FC = () => (
  <Composition
    id="sahara-07-chute"
    component={Chute}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.chute}
    defaultProps={{ duration: DUREES.chute, segment: "mots/07-chute", cut: CHUTE.cut }}
  />
);
