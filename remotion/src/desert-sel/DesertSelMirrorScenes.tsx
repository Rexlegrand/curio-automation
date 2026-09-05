import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { RainTransition } from "./RainTransition";

// Reel curiosité "Le désert de sel qui devient un miroir géant" (Salar
// d'Uyuni, Bolivie) — structure validée phase 2 : scène 1 (hook, sol sec ->
// pluie animée -> miroir révélé) puis scène 2 (marche dans les nuages,
// silhouette). Cut sec entre les plans photo (§3 CLAUDE.md, cohérent avec la
// lumière différente de chaque source — jour / coucher de soleil / orage,
// traité comme plans distincts) ; la transition pluie, elle, est un vrai
// morceau de motion design animé (feedback Benjamin : il manquait le
// mécanisme visuel montrant COMMENT la pluie crée le miroir).

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;

const SCENE1_SOL_SEC_FRAMES = 120; // 4s — sol sec, push-in
const SCENE1_RAIN_FRAMES = 110; // 3.67s — pluie animée, révèle le miroir
const SCENE1_MIROIR_HOLD_FRAMES = 70; // 2.33s — miroir pleinement révélé, push-in
const SCENE2_SILHOUETTE_FRAMES = 300; // 10s
const TOTAL_FRAMES =
  SCENE1_SOL_SEC_FRAMES + SCENE1_RAIN_FRAMES + SCENE1_MIROIR_HOLD_FRAMES + SCENE2_SILHOUETTE_FRAMES;

type KenBurnsProps = {
  src: string;
  durationInFrames: number;
  zoomFrom?: number;
  zoomTo?: number;
  panXFrom?: number;
  panXTo?: number;
};

// Ken Burns simple : zoom + pan lents sur toute la durée du plan, easing
// out (transcript Y6mOBK5peDU) pour un mouvement qui décélère naturellement.
const KenBurnsPhoto: React.FC<KenBurnsProps> = ({
  src,
  durationInFrames,
  zoomFrom = 1,
  zoomTo = 1.08,
  panXFrom = 0,
  panXTo = 0,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const panX = interpolate(frame, [0, durationInFrames], [panXFrom, panXTo], {
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
          transform: `scale(${scale}) translateX(${panX}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

export const DesertSelMirrorScenes: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Scène 1a — sol sec craquelé, push-in lent (0-4s) */}
      <Sequence from={0} durationInFrames={SCENE1_SOL_SEC_FRAMES}>
        <KenBurnsPhoto
          src={staticFile("desert-sel/sol_sec.jpg")}
          durationInFrames={SCENE1_SOL_SEC_FRAMES}
          zoomFrom={1}
          zoomTo={1.1}
        />
      </Sequence>

      {/* Cut sec -> Scène 1b — pluie animée qui révèle le miroir (4-7.67s) */}
      <Sequence from={SCENE1_SOL_SEC_FRAMES} durationInFrames={SCENE1_RAIN_FRAMES}>
        <RainTransition />
      </Sequence>

      {/* Miroir pleinement révélé, push-in continue (7.67-10s) */}
      <Sequence
        from={SCENE1_SOL_SEC_FRAMES + SCENE1_RAIN_FRAMES}
        durationInFrames={SCENE1_MIROIR_HOLD_FRAMES}
      >
        <KenBurnsPhoto
          src={staticFile("desert-sel/miroir_pur.png")}
          durationInFrames={SCENE1_MIROIR_HOLD_FRAMES}
          zoomFrom={1}
          zoomTo={1.06}
        />
      </Sequence>

      {/* Cut sec -> Scène 2 — silhouette qui marche dans le reflet des nuages (10-20s) */}
      <Sequence
        from={SCENE1_SOL_SEC_FRAMES + SCENE1_RAIN_FRAMES + SCENE1_MIROIR_HOLD_FRAMES}
        durationInFrames={SCENE2_SILHOUETTE_FRAMES}
      >
        <KenBurnsPhoto
          src={staticFile("desert-sel/silhouette_marche.jpg")}
          durationInFrames={SCENE2_SILHOUETTE_FRAMES}
          zoomFrom={1.05}
          zoomTo={1}
          panXFrom={-15}
          panXTo={15}
        />
      </Sequence>
    </AbsoluteFill>
  );
};

export const DesertSelMirrorScenesComposition: React.FC = () => {
  return (
    <Composition
      id="DesertSelMirrorScenes"
      component={DesertSelMirrorScenes}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      durationInFrames={TOTAL_FRAMES}
    />
  );
};
