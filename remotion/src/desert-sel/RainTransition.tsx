import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

// Transition animée sol sec -> miroir : gouttes de pluie qui tombent sur un
// fond neutre (feedback Benjamin : superposer une vraie photo en dessous
// faisait bizarre — le raccord se fait en cut sec vers miroir_pur.png juste
// après, pas besoin d'image ici, juste le mécanisme "la pluie tombe, des
// flaques se forment"). Positions/timings FIXES (pas de Math.random) pour un
// rendu déterministe et reproductible d'un render à l'autre.

type Drop = { xPercent: number; birthFrame: number; periodFrames: number; landYPercent: number };
type Puddle = { xPercent: number; yPercent: number; birthFrame: number; growFrames: number; maxRadiusPx: number };

const DROPS: Drop[] = [
  { xPercent: 12, birthFrame: 0, periodFrames: 26, landYPercent: 58 },
  { xPercent: 24, birthFrame: 5, periodFrames: 30, landYPercent: 64 },
  { xPercent: 38, birthFrame: 2, periodFrames: 22, landYPercent: 55 },
  { xPercent: 50, birthFrame: 9, periodFrames: 28, landYPercent: 62 },
  { xPercent: 62, birthFrame: 3, periodFrames: 24, landYPercent: 60 },
  { xPercent: 74, birthFrame: 12, periodFrames: 32, landYPercent: 68 },
  { xPercent: 86, birthFrame: 6, periodFrames: 27, landYPercent: 57 },
  { xPercent: 18, birthFrame: 15, periodFrames: 25, landYPercent: 72 },
  { xPercent: 45, birthFrame: 18, periodFrames: 29, landYPercent: 78 },
  { xPercent: 70, birthFrame: 20, periodFrames: 23, landYPercent: 74 },
  { xPercent: 30, birthFrame: 22, periodFrames: 31, landYPercent: 66 },
  { xPercent: 90, birthFrame: 14, periodFrames: 26, landYPercent: 63 },
  { xPercent: 8, birthFrame: 24, periodFrames: 28, landYPercent: 80 },
  { xPercent: 58, birthFrame: 26, periodFrames: 24, landYPercent: 82 },
];

// Flaques qui grandissent et finissent par se rejoindre : simples disques
// bleus (pas de reveal d'image dessous), la dernière assez grande pour
// suggérer que tout le sol est devenu liquide juste avant le cut vers
// miroir_pur.png.
const PUDDLES: Puddle[] = [
  { xPercent: 24, yPercent: 62, birthFrame: 8, growFrames: 30, maxRadiusPx: 90 },
  { xPercent: 68, yPercent: 68, birthFrame: 30, growFrames: 32, maxRadiusPx: 120 },
  { xPercent: 45, yPercent: 58, birthFrame: 45, growFrames: 30, maxRadiusPx: 100 },
  { xPercent: 52, yPercent: 62, birthFrame: 55, growFrames: 50, maxRadiusPx: 900 },
];

const FALL_FRACTION = 0.75; // portion du cycle passée à tomber (le reste = ondes qui s'estompent avant la goutte suivante)

const puddleRadius = (p: Puddle, frame: number) =>
  interpolate(frame, [p.birthFrame, p.birthFrame + p.growFrames], [0, p.maxRadiusPx], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

const RainDrop: React.FC<{ drop: Drop; frame: number }> = ({ drop, frame }) => {
  if (frame < drop.birthFrame) return null;
  const t = (frame - drop.birthFrame) % drop.periodFrames;
  const fallFrames = drop.periodFrames * FALL_FRACTION;
  const isFalling = t < fallFrames;

  if (isFalling) {
    const progress = t / fallFrames;
    const y = interpolate(progress, [0, 1], [-5, drop.landYPercent], { easing: Easing.in(Easing.quad) });
    const opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 0.9, 0.9, 0.3]);
    return (
      <div
        style={{
          position: "absolute",
          left: `${drop.xPercent}%`,
          top: `${y}%`,
          width: 3,
          height: 34,
          borderRadius: 3,
          background: "linear-gradient(to bottom, rgba(255,255,255,0), rgba(230,245,255,0.9))",
          opacity,
          transform: "translateX(-50%)",
        }}
      />
    );
  }

  const rippleT = (t - fallFrames) / (drop.periodFrames - fallFrames);
  const rippleRadius = interpolate(rippleT, [0, 1], [4, 46], { easing: Easing.out(Easing.cubic) });
  const rippleOpacity = interpolate(rippleT, [0, 1], [0.8, 0]);
  return (
    <div
      style={{
        position: "absolute",
        left: `${drop.xPercent}%`,
        top: `${drop.landYPercent}%`,
        width: rippleRadius * 2,
        height: rippleRadius * 0.4,
        borderRadius: "50%",
        border: "2px solid rgba(230,245,255,0.95)",
        opacity: rippleOpacity,
        transform: "translate(-50%, -50%)",
      }}
    />
  );
};

export const RainTransition: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{ overflow: "hidden", background: "linear-gradient(to bottom, #0b2a4a 0%, #123a63 55%, #1b4f82 100%)" }}
    >
      {PUDDLES.map((p, i) => {
        const r = puddleRadius(p, frame);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${p.xPercent}%`,
              top: `${p.yPercent}%`,
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              // Aplati en ellipse (perspective sol vu de face, pas une sphère) :
              // une flaque vue à hauteur d'oeil est bien plus large que haute.
              transform: "translate(-50%, -50%) scaleY(0.4)",
              background: "radial-gradient(circle at 42% 38%, #6fb8e6 0%, #2f6da0 45%, #123a63 100%)",
              boxShadow: "inset 0 0 30px rgba(255,255,255,0.25)",
            }}
          />
        );
      })}

      {DROPS.map((d, i) => (
        <RainDrop key={i} drop={d} frame={frame} />
      ))}
    </AbsoluteFill>
  );
};
