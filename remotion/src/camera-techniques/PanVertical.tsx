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

// Motion-catalog.md, catégorie 1 — "Pan vertical" : déplacement de haut en
// bas. Beat STAT / COMPARAISON.

const FPS = 30;
const W = 1080;
const H = 1920;
const DURATION = 126; // 4.2s — calibré sur le beat COMPARAISON du reel désert de sel (11.3-15.5s)

export type PanVerticalProps = {
  src: string;
  durationInFrames?: number;
  scale?: number; // sur-cadrage nécessaire pour avoir de la marge à panner
  panFromPct?: number; // position verticale de départ, en % (0 = haut de l'image visible)
  panToPct?: number;
};

export const PanVertical: React.FC<PanVerticalProps> = ({
  src,
  durationInFrames = DURATION,
  scale = 1.3,
  panFromPct = 0,
  panToPct = 100,
}) => {
  const frame = useCurrentFrame();
  const objectPositionY = interpolate(
    frame,
    [0, durationInFrames],
    [panFromPct, panToPct],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.sin),
    }
  );

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: `50% ${objectPositionY}%`,
          transform: `scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

export const PanVerticalComposition: React.FC = () => {
  return (
    <Composition
      id="CameraTechnique-PanVertical"
      component={PanVertical}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION}
      defaultProps={{ src: staticFile("desert-sel/miroir_pur.png") }}
    />
  );
};
