import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Test v6 — 2D en couches, recalé sur la référence réelle
// (references/motion-examples/Screen Recording 2026-08-28 at 4.46.32 pm.mov,
// "How I Fully Automated Video Editing with Claude Opus 5", frame à 0:05).
//
// Ce que la référence fait, et qui définit la scène :
//   - illustration PLATE empilée en couches (le "3D layered" vient de
//     l'empilement et du chevauchement, pas d'une caméra 3D) ;
//   - la scène vit dans une CARD arrondie, à côté d'une seconde card
//     (le talking head) ;
//   - les 3 objets du midground sont POSÉS SUR la balustrade, un par beat
//     de narration (graphique en barres / écran / éolienne) ;
//   - chaque objet qui apparaît déclenche un petit BURST d'étincelles
//     dorées autour de lui ;
//   - chaque bande de décor OSCILLE latéralement, à des amplitudes et des
//     phases différentes selon sa profondeur — c'est ce tangage décalé
//     (façon bateau) qui crée la sensation de relief, pas de la vraie 3D.

const FPS = 30;
const W = 1920;
const H = 1080;
const BEAT_FRAMES = 120; // 4s par beat
const TOTAL_FRAMES = BEAT_FRAMES * 3;

const CARD = { x: 60, y: 50, w: 1160, h: 980, r: 28 };
const HEAD_CARD = { x: 1250, y: 50, w: 610, h: 980, r: 28 };

// Repères verticaux DANS la card (coordonnées locales, card 1160x980).
const SUN = { x: 580, y: 216, r: 122 };
const HILL_FAR_Y = 529;
const HILL_NEAR_Y = 588;
const RAIL_Y = 700; // haut de la poutre : les objets posent leur base ici
const RAIL_H = 20;
const BAND_Y = 833; // bande bordeaux du premier plan

// Marge de débord : les couches qui oscillent sont plus larges que la card
// pour ne jamais découvrir un bord pendant le mouvement.
const OVER = 90;

const PALETTE = {
  pageBg: "#15171C",
  pageGrid: "rgba(255,255,255,0.035)",
  cardEmpty: "#1B1E24",
  skyTop: "#31586A",
  skyBottom: "#5C8494",
  rayDark: "rgba(38,64,74,0.55)",
  rayLight: "rgba(196,190,140,0.42)",
  sunCore: "#FFD166",
  sunEdge: "#F2A93B",
  sunGlow: "rgba(255,193,94,0.45)",
  cloud: "#FBF6EC",
  cloudShade: "#E7DECD",
  bird: "#1B2A36",
  hillFar: "#4A7A8C",
  hillNear: "#22404E",
  railTop: "#E9CE95",
  railBottom: "#C4A063",
  band: "#7A1F3D",
  leaf: "#2F9E6E",
  leafVein: "#1F7A54",
  barCream: "#F3E8CC",
  barGold: "#F2C230",
  screenFrame: "#1B2A36",
  screenFace: "#F7F1E1",
  screenEdge: "#3FA9B8",
  block: "#F3E8CC",
  turbineShade: "#D8C9A4",
  sparkle: "#F5C542",
};

// ---------- Tangage : oscillation latérale par couche ----------
// Même mouvement pour toutes les couches, mais amplitude croissante vers
// l'avant et phases opposées d'une bande à l'autre — c'est le décalage qui
// donne la profondeur. Période ~6s.

const SWAY_PERIOD = 180;

const useSway = (amplitude: number, phase = 0) => {
  const frame = useCurrentFrame();
  return Math.sin((frame / SWAY_PERIOD) * Math.PI * 2 + phase) * amplitude;
};

const SwayLayer: React.FC<{
  amplitude: number;
  phase?: number;
  children: React.ReactNode;
}> = ({ amplitude, phase = 0, children }) => {
  const dx = useSway(amplitude, phase);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: CARD.w,
        height: CARD.h,
        transform: `translateX(${dx}px)`,
      }}
    >
      {children}
    </div>
  );
};

// ---------- Étincelles au moment où un objet apparaît ----------

const Sparkles: React.FC<{
  cx: number;
  cy: number;
  activeSinceFrame: number;
  count?: number;
  radius?: number;
}> = ({ cx, cy, activeSinceFrame, count = 10, radius = 130 }) => {
  const frame = useCurrentFrame();
  const local = frame - activeSinceFrame;
  if (local < 0 || local > 48) return null;

  const p = interpolate(local, [0, 42], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const opacity = interpolate(local, [0, 7, 30, 46], [0, 1, 0.9, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const box = radius * 3;

  return (
    <svg
      width={box}
      height={box}
      style={{
        position: "absolute",
        left: cx - box / 2,
        top: cy - box / 2,
        overflow: "visible",
        opacity,
        pointerEvents: "none",
      }}
    >
      <g transform={`translate(${box / 2} ${box / 2})`}>
        {Array.from({ length: count }).map((_, i) => {
          const a = (i / count) * 360 + 14;
          const d = interpolate(p, [0, 1], [radius * 0.34, radius]);
          const s = interpolate(p, [0, 1], [1.05, 0.5]);
          return (
            <path
              key={i}
              d="M 0 -10 L 6.5 5 L -6.5 5 Z"
              fill={PALETTE.sparkle}
              transform={`rotate(${a}) translate(0 ${-d}) scale(${s})`}
            />
          );
        })}
      </g>
    </svg>
  );
};

// ---------- FOND : rayons, soleil, nuage, oiseaux ----------

const Rays: React.FC = () => {
  const frame = useCurrentFrame();
  const rotation = interpolate(frame, [0, TOTAL_FRAMES], [0, 20]);
  const stripes = 26;
  const stops: string[] = [];
  for (let i = 0; i < stripes; i++) {
    const a = (i / stripes) * 360;
    const b = ((i + 1) / stripes) * 360;
    stops.push(`${i % 2 === 0 ? PALETTE.rayDark : PALETTE.rayLight} ${a}deg ${b}deg`);
  }

  const size = 2600;
  return (
    <div
      style={{
        position: "absolute",
        left: SUN.x - size / 2,
        top: SUN.y - size / 2,
        width: size,
        height: size,
        transform: `rotate(${rotation}deg)`,
        background: `conic-gradient(${stops.join(",")})`,
      }}
    />
  );
};

const Sun: React.FC = () => (
  <>
    <div
      style={{
        position: "absolute",
        left: SUN.x - SUN.r - 44,
        top: SUN.y - SUN.r - 44,
        width: (SUN.r + 44) * 2,
        height: (SUN.r + 44) * 2,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${PALETTE.sunGlow} 0%, rgba(255,193,94,0) 70%)`,
      }}
    />
    <div
      style={{
        position: "absolute",
        left: SUN.x - SUN.r,
        top: SUN.y - SUN.r,
        width: SUN.r * 2,
        height: SUN.r * 2,
        borderRadius: "50%",
        background: `radial-gradient(circle at 40% 36%, ${PALETTE.sunCore} 0%, ${PALETTE.sunEdge} 78%)`,
      }}
    />
  </>
);

const Cloud: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, TOTAL_FRAMES], [0, 46]);
  const bob = Math.sin(frame / 45) * 5;

  return (
    <div style={{ position: "absolute", left: 852 + drift, top: 104 + bob }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 34,
          width: 148,
          height: 70,
          borderRadius: 44,
          backgroundColor: PALETTE.cloud,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 52,
          top: 0,
          width: 104,
          height: 90,
          borderRadius: 52,
          backgroundColor: PALETTE.cloud,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 118,
          top: 26,
          width: 92,
          height: 74,
          borderRadius: 46,
          backgroundColor: PALETTE.cloud,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 62,
          width: 96,
          height: 40,
          borderRadius: 26,
          backgroundColor: PALETTE.cloudShade,
        }}
      />
    </div>
  );
};

const Bird: React.FC<{ delay: number; top: number; speed: number; fromLeft: boolean }> = ({
  delay,
  top,
  speed,
  fromLeft,
}) => {
  const frame = useCurrentFrame() - delay;
  if (frame < 0) return null;

  const progress = interpolate(frame, [0, 260 / speed], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.linear,
  });
  const x = fromLeft
    ? interpolate(progress, [0, 1], [-80, CARD.w + 80])
    : interpolate(progress, [0, 1], [CARD.w + 80, -80]);
  const bob = Math.sin(frame / 7) * 12;
  const flap = Math.sin(frame / 4.5) * 9;

  return (
    <svg width={46} height={24} style={{ position: "absolute", left: x, top: top + bob }}>
      <path
        d={`M 0 12 Q 11 ${12 - flap} 23 12 Q 35 ${12 - flap} 46 12`}
        stroke={PALETTE.bird}
        strokeWidth={3.5}
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
};

// ---------- COLLINES (festons) ----------

const HillBand: React.FC<{ count: number; amp: number; baseY: number; color: string }> = ({
  count,
  amp,
  baseY,
  color,
}) => {
  const width = CARD.w + OVER * 2;
  const w = width / count;
  let d = `M 0 ${baseY + amp} `;
  for (let i = 0; i < count; i++) {
    const cx = i * w + w / 2;
    d += `Q ${cx} ${baseY - amp} ${(i + 1) * w} ${baseY + amp} `;
  }
  d += `L ${width} ${CARD.h} L 0 ${CARD.h} Z`;

  return (
    <svg
      width={width}
      height={CARD.h}
      style={{ position: "absolute", left: -OVER, top: 0 }}
    >
      <path d={d} fill={color} />
    </svg>
  );
};

// ---------- MIDGROUND : 3 objets POSÉS SUR la balustrade ----------

const useEnter = (activeSinceFrame: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - activeSinceFrame;
  const entrance = spring({
    frame: Math.max(0, local),
    fps,
    config: { damping: 12, mass: 0.6 },
  });
  return {
    visible: local >= 0,
    local,
    rise: interpolate(entrance, [0, 1], [46, 0]),
    scale: interpolate(entrance, [0, 1], [0.72, 1]),
    opacity: interpolate(Math.max(0, local), [0, 10], [0, 1], {
      extrapolateRight: "clamp",
    }),
  };
};

// Beat 1 — "motion graphics" : barres qui poussent depuis la poutre.
const BarChart: React.FC<{ activeSinceFrame: number }> = ({ activeSinceFrame }) => {
  const { visible, local, rise, opacity } = useEnter(activeSinceFrame);
  if (!visible) return null;

  const bars = [
    { x: 0, w: 42, h: 62, color: PALETTE.barCream, delay: 0 },
    { x: 54, w: 42, h: 104, color: PALETTE.barCream, delay: 6 },
    { x: 108, w: 42, h: 150, color: PALETTE.barGold, delay: 12 },
    { x: 162, w: 42, h: 196, color: PALETTE.barGold, delay: 18 },
  ];

  return (
    <div
      style={{
        position: "absolute",
        left: 131,
        top: 0,
        opacity,
        transform: `translateY(${rise}px)`,
      }}
    >
      {bars.map((b, i) => {
        const grow = interpolate(local, [b.delay, b.delay + 22], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const h = b.h * grow;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: b.x,
              top: RAIL_Y - h,
              width: b.w,
              height: h,
              backgroundColor: b.color,
              borderRadius: 4,
            }}
          />
        );
      })}
    </div>
  );
};

// Beat 2 — "transitions" : écran posé sur la poutre, contenu qui balaie.
const Monitor: React.FC<{ activeSinceFrame: number }> = ({ activeSinceFrame }) => {
  const { visible, local, rise, scale, opacity } = useEnter(activeSinceFrame);
  if (!visible) return null;

  const screenW = 232;
  const screenH = 168;
  const sweep = interpolate(local, [14, 44], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  return (
    <div
      style={{
        position: "absolute",
        left: 449,
        top: RAIL_Y - screenH - 26,
        opacity,
        transform: `translateY(${rise}px) scale(${scale})`,
        transformOrigin: "50% 100%",
      }}
    >
      <div
        style={{
          position: "relative",
          width: screenW,
          height: screenH,
          borderRadius: 12,
          backgroundColor: PALETTE.screenFrame,
          padding: 8,
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            borderRadius: 6,
            backgroundColor: PALETTE.screenFace,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              bottom: 0,
              width: 16,
              backgroundColor: PALETTE.screenEdge,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `${sweep * 100}%`,
              width: 46,
              background: `linear-gradient(90deg, rgba(63,169,184,0), ${PALETTE.screenEdge}, rgba(63,169,184,0))`,
              opacity: 0.55,
            }}
          />
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: screenW / 2 - 16,
          top: screenH,
          width: 32,
          height: 16,
          backgroundColor: PALETTE.screenFrame,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: screenW / 2 - 44,
          top: screenH + 16,
          width: 88,
          height: 10,
          borderRadius: 5,
          backgroundColor: PALETTE.screenFrame,
        }}
      />
    </div>
  );
};

// Beat 3 — "animations" : éolienne posée sur la poutre, rotor qui démarre
// puis tourne en continu (réf. images fournies : 3 pales blanches effilées,
// mât tubulaire légèrement conique, nacelle courte).
const TURBINE = { boxW: 200, boxH: 250, baseX: 100, baseY: 250, hubY: 78 };

const WindTurbine: React.FC<{ activeSinceFrame: number }> = ({ activeSinceFrame }) => {
  const { visible, local, rise, scale, opacity } = useEnter(activeSinceFrame);
  if (!visible) return null;

  const spinUp = interpolate(local, [0, 45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const angle = local * 3.4 * spinUp;
  const blade = "M -5 0 C -12 -32 -10 -70 0 -98 C 10 -70 12 -32 5 0 Z";

  return (
    <svg
      width={TURBINE.boxW}
      height={TURBINE.boxH}
      style={{
        position: "absolute",
        left: 888 - TURBINE.boxW / 2,
        top: RAIL_Y - TURBINE.boxH,
        opacity,
        transform: `translateY(${rise}px) scale(${scale})`,
        transformOrigin: "50% 100%",
        overflow: "visible",
      }}
    >
      <path
        d={`M ${TURBINE.baseX - 11} ${TURBINE.baseY}
            L ${TURBINE.baseX - 4.5} ${TURBINE.hubY}
            L ${TURBINE.baseX + 4.5} ${TURBINE.hubY}
            L ${TURBINE.baseX + 11} ${TURBINE.baseY} Z`}
        fill={PALETTE.block}
      />
      <path
        d={`M ${TURBINE.baseX + 3} ${TURBINE.baseY}
            L ${TURBINE.baseX + 1.5} ${TURBINE.hubY}
            L ${TURBINE.baseX + 4.5} ${TURBINE.hubY}
            L ${TURBINE.baseX + 11} ${TURBINE.baseY} Z`}
        fill={PALETTE.turbineShade}
      />
      <rect
        x={TURBINE.baseX - 13}
        y={TURBINE.hubY - 9}
        width={26}
        height={18}
        rx={9}
        fill={PALETTE.block}
      />
      <g transform={`translate(${TURBINE.baseX} ${TURBINE.hubY}) rotate(${angle})`}>
        {[0, 120, 240].map((a) => (
          <path key={a} d={blade} transform={`rotate(${a})`} fill={PALETTE.block} />
        ))}
        <circle r={8} fill={PALETTE.turbineShade} />
      </g>
    </svg>
  );
};

// ---------- BALUSTRADE + PREMIER PLAN ----------

const Railing: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: -OVER,
      top: RAIL_Y,
      width: CARD.w + OVER * 2,
      height: RAIL_H,
      background: `linear-gradient(to bottom, ${PALETTE.railTop}, ${PALETTE.railBottom})`,
    }}
  />
);

const Band: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: -OVER,
      top: BAND_Y,
      width: CARD.w + OVER * 2,
      height: CARD.h - BAND_Y,
      backgroundColor: PALETTE.band,
    }}
  />
);

const Leaves: React.FC = () => {
  const frame = useCurrentFrame();
  const sway = Math.sin(frame / 55) * 1.4;

  return (
    <>
      <svg
        width={360}
        height={200}
        style={{
          position: "absolute",
          left: -46,
          top: RAIL_Y - 74,
          transform: `rotate(${sway}deg)`,
          transformOrigin: "12% 88%",
        }}
      >
        <path
          d="M 18 178 C 6 116 60 34 336 16 C 234 74 130 130 18 178 Z"
          fill={PALETTE.leaf}
        />
        <path
          d="M 34 172 C 86 114 164 70 320 24"
          stroke={PALETTE.leafVein}
          strokeWidth={4}
          fill="none"
          strokeLinecap="round"
          opacity={0.55}
        />
      </svg>
      <svg
        width={260}
        height={120}
        style={{ position: "absolute", left: -60, top: BAND_Y - 34 }}
      >
        <path
          d="M 10 100 C 4 60 60 22 250 8 C 168 44 92 72 10 100 Z"
          fill={PALETTE.leaf}
          opacity={0.9}
        />
      </svg>
    </>
  );
};

// ---------- SCÈNE (contenu de la card de gauche) ----------
// L'ordre des <SwayLayer> = l'ordre de profondeur. L'amplitude croît vers
// l'avant et la phase alterne (0 / π), pour que les bandes se croisent au
// lieu de glisser toutes ensemble.

const VoxScene: React.FC = () => {
  const frame = useCurrentFrame();
  const beatIndex = Math.min(2, Math.floor(frame / BEAT_FRAMES));

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: CARD.w,
        height: CARD.h,
        overflow: "hidden",
        background: `linear-gradient(to bottom, ${PALETTE.skyTop} 0%, ${PALETTE.skyBottom} 100%)`,
      }}
    >
      <SwayLayer amplitude={5}>
        <Rays />
      </SwayLayer>

      <SwayLayer amplitude={8} phase={Math.PI}>
        <Sun />
      </SwayLayer>

      <SwayLayer amplitude={12}>
        <Cloud />
        <Bird fromLeft delay={8} top={150} speed={1.25} />
        <Bird fromLeft delay={54} top={196} speed={1.05} />
        <Bird fromLeft={false} delay={120} top={128} speed={1.35} />
        <Bird fromLeft={false} delay={196} top={214} speed={1.15} />
      </SwayLayer>

      <SwayLayer amplitude={16} phase={Math.PI}>
        <HillBand count={6} amp={34} baseY={HILL_FAR_Y} color={PALETTE.hillFar} />
      </SwayLayer>

      <SwayLayer amplitude={24}>
        <HillBand count={7} amp={30} baseY={HILL_NEAR_Y} color={PALETTE.hillNear} />
      </SwayLayer>

      {/* Objets + poutre : même couche, ils tanguent ensemble */}
      <SwayLayer amplitude={34} phase={Math.PI}>
        {beatIndex >= 0 && (
          <>
            <BarChart activeSinceFrame={0} />
            <Sparkles cx={233} cy={598} activeSinceFrame={0} radius={132} />
          </>
        )}
        {beatIndex >= 1 && (
          <>
            <Monitor activeSinceFrame={BEAT_FRAMES} />
            <Sparkles
              cx={565}
              cy={604}
              activeSinceFrame={BEAT_FRAMES}
              radius={150}
              count={11}
            />
          </>
        )}
        {beatIndex >= 2 && (
          <>
            <WindTurbine activeSinceFrame={BEAT_FRAMES * 2} />
            <Sparkles
              cx={888}
              cy={578}
              activeSinceFrame={BEAT_FRAMES * 2}
              radius={144}
            />
          </>
        )}
        <Railing />
      </SwayLayer>

      <SwayLayer amplitude={46}>
        <Band />
        <Leaves />
      </SwayLayer>
    </div>
  );
};

// ---------- COMPOSITION COMPLÈTE ----------

export const VoxLayeredScene2Dv2: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: PALETTE.pageBg }}>
    <AbsoluteFill
      style={{
        backgroundImage: `
          linear-gradient(to right, ${PALETTE.pageGrid} 1px, transparent 1px),
          linear-gradient(to bottom, ${PALETTE.pageGrid} 1px, transparent 1px)
        `,
        backgroundSize: "48px 48px",
      }}
    />

    <div
      style={{
        position: "absolute",
        left: CARD.x,
        top: CARD.y,
        width: CARD.w,
        height: CARD.h,
        borderRadius: CARD.r,
        overflow: "hidden",
        boxShadow: "0 30px 70px rgba(0,0,0,0.45)",
      }}
    >
      <VoxScene />
    </div>

    <div
      style={{
        position: "absolute",
        left: HEAD_CARD.x,
        top: HEAD_CARD.y,
        width: HEAD_CARD.w,
        height: HEAD_CARD.h,
        borderRadius: HEAD_CARD.r,
        backgroundColor: PALETTE.cardEmpty,
        boxShadow: "0 30px 70px rgba(0,0,0,0.45)",
      }}
    />
  </AbsoluteFill>
);

export const VoxLayeredScene2Dv2Composition: React.FC = () => (
  <Composition
    id="VoxLayeredScene2D-v2"
    component={VoxLayeredScene2Dv2}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={TOTAL_FRAMES}
  />
);
