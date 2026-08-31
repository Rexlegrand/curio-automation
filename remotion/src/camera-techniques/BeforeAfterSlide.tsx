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

// Motion-catalog.md, catégorie 4 — "Before/after slide" : curseur qui glisse
// pour révéler l'état avant/après. Beat CAUSE-EFFET / COMPARAISON.

const FPS = 30;
const W = 1080;
const H = 1920;
const DURATION = 171; // 5.7s — calibré sur le beat CAUSE-EFFET du reel désert de sel (5.1-10.8s)

export type BeforeAfterSlideProps = {
  beforeSrc: string;
  afterSrc: string;
  durationInFrames?: number;
  holdBeforeFrames?: number; // frames d'immobilité avant que le curseur bouge
  holdAfterFrames?: number; // frames d'immobilité une fois "after" pleinement révélé
};

export const BeforeAfterSlide: React.FC<BeforeAfterSlideProps> = ({
  beforeSrc,
  afterSrc,
  durationInFrames = DURATION,
  holdBeforeFrames = 20,
  holdAfterFrames = 30,
}) => {
  const frame = useCurrentFrame();
  const sweepStart = holdBeforeFrames;
  const sweepEnd = durationInFrames - holdAfterFrames;

  // Position du curseur en % de la largeur, 100% (tout "before") -> 0% (tout "after")
  const cursorPct = interpolate(
    frame,
    [sweepStart, sweepEnd],
    [100, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    }
  );

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img
        src={afterSrc}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      <AbsoluteFill
        style={{ clipPath: `inset(0 ${100 - cursorPct}% 0 0)` }}
      >
        <Img
          src={beforeSrc}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: `${cursorPct}%`,
          width: 4,
          backgroundColor: "rgba(255,255,255,0.9)",
          boxShadow: "0 0 20px rgba(0,0,0,0.5)",
          transform: "translateX(-2px)",
        }}
      />
    </AbsoluteFill>
  );
};

export const BeforeAfterSlideComposition: React.FC = () => {
  return (
    <Composition
      id="CameraTechnique-BeforeAfterSlide"
      component={BeforeAfterSlide}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION}
      defaultProps={{
        beforeSrc: staticFile("desert-sel/sol_sec.jpg"),
        afterSrc: staticFile("desert-sel/miroir_pur.png"),
      }}
    />
  );
};
