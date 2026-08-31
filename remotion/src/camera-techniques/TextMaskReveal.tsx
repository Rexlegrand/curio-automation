import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

// Motion-catalog.md, catégorie 3 — "Text mask avec vidéo/image" : texte
// rempli par une texture animée en arrière-plan. Beat HOOK / CONCLUSION.

const FPS = 30;
const W = 1080;
const H = 1920;
const DURATION = 135; // 4.5s — calibré sur le beat CONCLUSION du reel désert de sel (28.2-32.7s)

export type TextMaskRevealProps = {
  text: string;
  textureSrc: string;
  durationInFrames?: number;
  fontSize?: number;
};

export const TextMaskReveal: React.FC<TextMaskRevealProps> = ({
  text,
  textureSrc,
  durationInFrames = DURATION,
  fontSize = 92,
}) => {
  const frame = useCurrentFrame();

  // Texture qui dérive lentement derrière le texte, pour donner l'impression
  // d'une vraie image/vidéo vivante plutôt qu'un simple fond figé.
  const bgPositionPct = interpolate(frame, [0, durationInFrames], [40, 60], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: `url(${textureSrc})`,
          backgroundSize: `${scale * 130}%`,
          backgroundPosition: `${bgPositionPct}% 50%`,
          filter: "brightness(0.6)",
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: 60 }}>
        <div
          style={{
            fontFamily: "Arial, sans-serif",
            fontWeight: 900,
            fontSize,
            lineHeight: 1.15,
            textAlign: "center",
            backgroundImage: `url(${textureSrc})`,
            backgroundSize: `${scale * 130}%`,
            backgroundPosition: `${bgPositionPct}% 50%`,
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
            filter: "brightness(1.6) contrast(1.2)",
          }}
        >
          {text}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const TextMaskRevealComposition: React.FC = () => {
  return (
    <Composition
      id="CameraTechnique-TextMaskReveal"
      component={TextMaskReveal}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION}
      defaultProps={{
        text: "Un seul jour de pluie\nsuffit",
        textureSrc: staticFile("desert-sel/miroir_pur.png"),
      }}
    />
  );
};
