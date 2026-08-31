import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Test — scène 3D-layered style "Vox" (illustration plate, formes
// géométriques, ombres douces). Trois couches indépendantes : fond (soleil
// qui tourne + rayons + nuages + oiseaux qui entrent des deux bords),
// midground (3 beats texte/motion calés sur "motion graphics / transitions /
// animations"), premier plan (poste de travail extérieur minimaliste
// tropical, statique + idle bounce léger). Aucun asset externe : tout en
// SVG/CSS pour un test autonome, pas de dépendance de sourcing d'images.

const FPS = 30;
const W = 1080;
const H = 1920;
const BEAT_FRAMES = 120; // 4s par beat midground
const TOTAL_FRAMES = BEAT_FRAMES * 3;

const PALETTE = {
  skyTop: "#FFD9A0",
  skyBottom: "#FF9E7D",
  sun: "#FFF3C4",
  sunGlow: "#FFCF6E",
  cloud: "rgba(255,255,255,0.85)",
  bird: "#2B2140",
  midgroundText: "#2B2140",
  accent1: "#FF6B6B",
  accent2: "#4ECDC4",
  accent3: "#FFD93D",
  foregroundDesk: "#3E2723",
  foregroundDeskTop: "#5D4037",
  laptop: "#2B2140",
  leaf: "#2F9E6E",
  leafDark: "#1F7A54",
};

// ---------- FOND ----------

const Sun: React.FC = () => {
  const frame = useCurrentFrame();
  const rotation = interpolate(frame, [0, TOTAL_FRAMES], [0, 90], {
    extrapolateRight: "extend",
  });
  const rayCount = 12;

  return (
    <div
      style={{
        position: "absolute",
        top: 220,
        left: "50%",
        width: 420,
        height: 420,
        transform: "translateX(-50%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${PALETTE.sunGlow} 0%, rgba(255,207,110,0) 70%)`,
        }}
      />
      <svg
        width={420}
        height={420}
        style={{ position: "absolute", inset: 0, transform: `rotate(${rotation}deg)` }}
      >
        {Array.from({ length: rayCount }).map((_, i) => {
          const angle = (i / rayCount) * 360;
          return (
            <rect
              key={i}
              x={210 - 6}
              y={10}
              width={12}
              height={60}
              rx={6}
              fill={PALETTE.sun}
              opacity={0.9}
              transform={`rotate(${angle} 210 210)`}
            />
          );
        })}
      </svg>
      <div
        style={{
          position: "absolute",
          top: 90,
          left: 90,
          width: 240,
          height: 240,
          borderRadius: "50%",
          backgroundColor: PALETTE.sun,
          boxShadow: `0 0 80px 20px ${PALETTE.sunGlow}`,
        }}
      />
    </div>
  );
};

const Cloud: React.FC<{ top: number; scale: number; speed: number; startX: number }> = ({
  top,
  scale,
  speed,
  startX,
}) => {
  const frame = useCurrentFrame();
  const x = ((startX + frame * speed) % (W + 400)) - 200;

  return (
    <div
      style={{
        position: "absolute",
        top,
        left: x,
        transform: `scale(${scale})`,
        display: "flex",
      }}
    >
      <div style={{ width: 90, height: 60, borderRadius: 40, backgroundColor: PALETTE.cloud }} />
      <div
        style={{
          width: 70,
          height: 70,
          borderRadius: 40,
          backgroundColor: PALETTE.cloud,
          marginLeft: -40,
          marginTop: -20,
        }}
      />
      <div
        style={{
          width: 60,
          height: 45,
          borderRadius: 30,
          backgroundColor: PALETTE.cloud,
          marginLeft: -30,
          marginTop: 12,
        }}
      />
    </div>
  );
};

const Bird: React.FC<{ fromLeft: boolean; delay: number; top: number }> = ({
  fromLeft,
  delay,
  top,
}) => {
  const frame = useCurrentFrame() - delay;
  if (frame < 0) return null;

  const progress = interpolate(frame, [0, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.linear,
  });
  const startX = fromLeft ? -100 : W + 100;
  const endX = fromLeft ? W + 100 : -100;
  const x = interpolate(progress, [0, 1], [startX, endX]);
  const bob = Math.sin(frame / 6) * 18;
  const flap = Math.sin(frame / 4) * 14;

  return (
    <svg
      width={60}
      height={30}
      style={{ position: "absolute", left: x, top: top + bob, transform: fromLeft ? "none" : "scaleX(-1)" }}
    >
      <path
        d={`M 0 15 Q 15 ${15 - flap} 30 15 Q 45 ${15 - flap} 60 15`}
        stroke={PALETTE.bird}
        strokeWidth={4}
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
};

const Background: React.FC = () => (
  <AbsoluteFill>
    <AbsoluteFill
      style={{
        background: `linear-gradient(to bottom, ${PALETTE.skyTop} 0%, ${PALETTE.skyBottom} 100%)`,
      }}
    />
    <Sun />
    <Cloud top={340} scale={1.1} speed={0.6} startX={100} />
    <Cloud top={480} scale={0.8} speed={0.35} startX={600} />
    <Cloud top={260} scale={0.6} speed={0.9} startX={-100} />
    <Bird fromLeft top={380} delay={20} />
    <Bird fromLeft={false} top={430} delay={70} />
    <Bird fromLeft top={310} delay={140} />
    <Bird fromLeft={false} top={520} delay={210} />
  </AbsoluteFill>
);

// ---------- MIDGROUND ----------

const MidgroundBeat: React.FC<{ label: string; accent: string; variant: 0 | 1 | 2 }> = ({
  label,
  accent,
  variant,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, mass: 0.6 } });
  const scale = interpolate(entrance, [0, 1], [0.6, 1]);
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  // Variant 0 = "Motion Graphics" -> pop-in avec rebond + rotation
  // Variant 1 = "Transitions" -> swipe/wipe géométrique
  // Variant 2 = "Animations" -> kinetic list stagger (mots en cascade)
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      {variant === 1 && (
        <div
          style={{
            position: "absolute",
            width: interpolate(frame, [0, 40], [0, W], { extrapolateRight: "clamp" }),
            height: 340,
            backgroundColor: accent,
            opacity: 0.18,
          }}
        />
      )}

      {variant === 0 && (
        <div
          style={{
            opacity,
            transform: `scale(${scale}) rotate(${interpolate(frame, [0, 90], [0, 8])}deg)`,
            fontFamily: "Arial, sans-serif",
            fontWeight: 900,
            fontSize: 88,
            color: PALETTE.midgroundText,
            textAlign: "center",
            padding: "0 60px",
          }}
        >
          {label}
        </div>
      )}

      {variant === 2 &&
        label.split(" ").map((word, i) => {
          const wordDelay = i * 6;
          const wOpacity = interpolate(frame, [wordDelay, wordDelay + 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const wY = interpolate(frame, [wordDelay, wordDelay + 12], [40, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          return (
            <div
              key={i}
              style={{
                opacity: wOpacity,
                transform: `translateY(${wY}px)`,
                fontFamily: "Arial, sans-serif",
                fontWeight: 900,
                fontSize: 88,
                color: PALETTE.midgroundText,
              }}
            >
              {word}
            </div>
          );
        })}

      {variant === 1 && (
        <div
          style={{
            opacity,
            fontFamily: "Arial, sans-serif",
            fontWeight: 900,
            fontSize: 88,
            color: PALETTE.midgroundText,
            textAlign: "center",
            padding: "0 60px",
          }}
        >
          {label}
        </div>
      )}

      <div
        style={{
          marginTop: 30,
          width: 90,
          height: 10,
          borderRadius: 6,
          backgroundColor: accent,
          transform: `scaleX(${interpolate(frame, [10, 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })})`,
        }}
      />
    </AbsoluteFill>
  );
};

const Midground: React.FC = () => (
  <>
    <Sequence from={0} durationInFrames={BEAT_FRAMES}>
      <MidgroundBeat label="Motion Graphics" accent={PALETTE.accent1} variant={0} />
    </Sequence>
    <Sequence from={BEAT_FRAMES} durationInFrames={BEAT_FRAMES}>
      <MidgroundBeat label="Transitions" accent={PALETTE.accent2} variant={1} />
    </Sequence>
    <Sequence from={BEAT_FRAMES * 2} durationInFrames={BEAT_FRAMES}>
      <MidgroundBeat label="Animations" accent={PALETTE.accent3} variant={2} />
    </Sequence>
  </>
);

// ---------- PREMIER PLAN ----------

const Foreground: React.FC = () => {
  const frame = useCurrentFrame();
  const idle = Math.sin(frame / 25) * 4;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 520,
          transform: `translateY(${idle}px)`,
        }}
      >
        {/* Sol / terrasse */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 90,
            backgroundColor: "#C9B896",
          }}
        />
        {/* Bureau */}
        <div
          style={{
            position: "absolute",
            bottom: 90,
            left: 140,
            width: 520,
            height: 220,
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: 24,
              backgroundColor: PALETTE.foregroundDeskTop,
              borderRadius: 6,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 24,
              left: 20,
              width: 20,
              height: 196,
              backgroundColor: PALETTE.foregroundDesk,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 24,
              right: 20,
              width: 20,
              height: 196,
              backgroundColor: PALETTE.foregroundDesk,
            }}
          />
          {/* Laptop */}
          <div
            style={{
              position: "absolute",
              top: -110,
              left: 170,
              width: 180,
              height: 110,
              backgroundColor: PALETTE.laptop,
              borderRadius: "6px 6px 0 0",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 150,
              width: 220,
              height: 14,
              backgroundColor: PALETTE.laptop,
              borderRadius: 4,
            }}
          />
          {/* Tasse */}
          <div
            style={{
              position: "absolute",
              top: -40,
              left: 420,
              width: 44,
              height: 50,
              backgroundColor: "#F5F0E6",
              borderRadius: "4px 4px 10px 10px",
            }}
          />
        </div>
        {/* Feuille de palmier, coin bas gauche */}
        <svg
          width={340}
          height={420}
          style={{ position: "absolute", bottom: -40, left: -80 }}
        >
          <path
            d="M 170 420 C 60 300 20 160 170 20 C 150 160 160 300 170 420 Z"
            fill={PALETTE.leaf}
          />
          <path
            d="M 170 420 C 260 300 300 150 170 20 C 200 160 190 300 170 420 Z"
            fill={PALETTE.leafDark}
            opacity={0.8}
          />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ---------- SCÈNE COMPLÈTE ----------

export const VoxLayeredScene: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Background />
    <Midground />
    <Foreground />
  </AbsoluteFill>
);

export const VoxLayeredSceneComposition: React.FC = () => (
  <Composition
    id="VoxLayeredScene"
    component={VoxLayeredScene}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={TOTAL_FRAMES}
  />
);
