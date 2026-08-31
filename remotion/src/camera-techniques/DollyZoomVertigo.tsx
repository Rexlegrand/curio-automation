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

// Motion-catalog.md, catégorie 1 — "Dolly zoom (vertigo)" : zoom + contre-
// zoom simultané, effet de malaise/tension. Beat RÉVÉLATION / CAUSE-EFFET.
//
// Approximation CSS d'un vrai dolly zoom (qui nécessite une vraie caméra 3D
// et de la profondeur) : le sujet (Img) grossit pendant que le cadre englobant
// rétrécit à l'inverse pour garder sa taille apparente à peu près stable,
// combiné à une vignette radiale qui se creuse — c'est ce déséquilibre entre
// "le sujet ne change pas de taille" et "tout autour se déforme" qui donne
// la sensation de vertige, pas une vraie perspective changeante.

const FPS = 30;
const W = 1080;
const H = 1920;
const DURATION = 123; // 4.1s — calibré sur le beat RÉVÉLATION du reel désert de sel (16.0-20.1s)

export type DollyZoomVertigoProps = {
  src: string;
  durationInFrames?: number;
  innerZoomFrom?: number;
  innerZoomTo?: number;
  outerZoomFrom?: number;
  outerZoomTo?: number;
};

export const DollyZoomVertigo: React.FC<DollyZoomVertigoProps> = ({
  src,
  durationInFrames = DURATION,
  innerZoomFrom = 1,
  innerZoomTo = 1.4,
  outerZoomFrom = 1,
  outerZoomTo = 0.82,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const innerScale = interpolate(progress, [0, 1], [innerZoomFrom, innerZoomTo]);
  const outerScale = interpolate(progress, [0, 1], [outerZoomFrom, outerZoomTo]);
  const vignetteOpacity = interpolate(progress, [0, 1], [0, 0.65]);

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${outerScale})` }}>
        <Img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${innerScale})`,
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.9) 100%)",
          opacity: vignetteOpacity,
        }}
      />
    </AbsoluteFill>
  );
};

export const DollyZoomVertigoComposition: React.FC = () => {
  return (
    <Composition
      id="CameraTechnique-DollyZoomVertigo"
      component={DollyZoomVertigo}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION}
      defaultProps={{ src: staticFile("desert-sel/silhouette_marche.jpg") }}
    />
  );
};
