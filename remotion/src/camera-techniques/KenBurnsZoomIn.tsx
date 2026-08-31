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

// Motion-catalog.md, catégorie 1 — "Ken Burns zoom-in" : zoom lent
// progressif vers un point focal. Beat FAIT / DÉFINITION.

const FPS = 30;
const W = 1080;
const H = 1920;
const DURATION = 105; // 3.5s — calibré sur le beat FAIT du reel désert de sel (1.1-4.6s)

export type KenBurnsZoomInProps = {
  src: string;
  durationInFrames?: number;
  zoomFrom?: number;
  zoomTo?: number;
  focalOriginX?: string; // ex: "50%" (centre) ou "30%" (point focal décalé)
  focalOriginY?: string;
};

export const KenBurnsZoomIn: React.FC<KenBurnsZoomInProps> = ({
  src,
  durationInFrames = DURATION,
  zoomFrom = 1,
  zoomTo = 1.15,
  focalOriginX = "50%",
  focalOriginY = "50%",
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transformOrigin: `${focalOriginX} ${focalOriginY}`,
          transform: `scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

export const KenBurnsZoomInComposition: React.FC = () => {
  return (
    <Composition
      id="CameraTechnique-KenBurnsZoomIn"
      component={KenBurnsZoomIn}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION}
      defaultProps={{ src: staticFile("desert-sel/sol_sec.jpg") }}
    />
  );
};
