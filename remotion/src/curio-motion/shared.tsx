// Prototypes motion design Curio — composants partagés par les 5 directions.
// Charte reprise de generators/math_renderers/cahier_background.py (mêmes
// couleurs Seyès) et compose_illustration() (bordure blanche + ombre +
// rotation légère) pour rester dans l'esthétique déjà validée du pipeline.

import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";

export const GRID_COLOR = "rgb(198,216,240)";
export const PAPER_COLOR = "rgb(253,253,250)";
export const MARGIN_COLOR = "rgb(230,140,140)";
export const GRID_STEP = 40;
export const MARGIN_X = 90;

export const CahierBackground: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => (
  <AbsoluteFill style={{ backgroundColor: PAPER_COLOR }}>
    <AbsoluteFill
      style={{
        backgroundImage: `
          linear-gradient(to right, ${GRID_COLOR} 1px, transparent 1px),
          linear-gradient(to bottom, ${GRID_COLOR} 1px, transparent 1px)
        `,
        backgroundSize: `${GRID_STEP}px ${GRID_STEP}px`,
      }}
    />
    <div
      style={{
        position: "absolute",
        left: MARGIN_X,
        top: 0,
        bottom: 0,
        width: 2,
        backgroundColor: MARGIN_COLOR,
      }}
    />
    {children}
  </AbsoluteFill>
);

// Photo "collée" style magazine-clip : bordure blanche + ombre + rotation.
export const PastedPhoto: React.FC<{
  src: string;
  width: number;
  rotateDeg?: number;
  style?: React.CSSProperties;
}> = ({ src, width, rotateDeg = 0, style }) => (
  <div
    style={{
      display: "inline-block",
      backgroundColor: "white",
      padding: 14,
      boxShadow: "0 18px 40px rgba(0,0,0,0.35)",
      transform: `rotate(${rotateDeg}deg)`,
      ...style,
    }}
  >
    <Img src={src} style={{ width, display: "block" }} />
  </div>
);

export const CurioMascotte: React.FC<{
  size?: number;
  style?: React.CSSProperties;
}> = ({ size = 220, style }) => (
  <Img
    src={staticFile("curio-mascotte.png")}
    style={{ width: size, ...style }}
  />
);

export const IMAGES = {
  eclipse: staticFile("curio_motion/img_eclipse.jpg"),
  tdf: staticFile("curio_motion/img_tdf.jpg"),
  stadium: staticFile("curio_motion/img_stadium.jpg"),
  footballKid: staticFile("curio_motion/img_football_kid.jpg"),
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;
