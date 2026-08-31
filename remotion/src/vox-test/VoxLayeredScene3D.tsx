import React, { useMemo } from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";

// Test — même scène que VoxLayeredScene.tsx mais en vrai 3D (React Three
// Fiber via @remotion/three, pas de CSS/SVG 2.5D). Vraie profondeur de scène
// (objets positionnés sur l'axe Z, caméra qui bouge légèrement en X) donc
// vrai parallax entre fond/midground/premier plan — pas un effet simulé.
// Style "low-poly flat-shaded" (Vox) : géométries simples, flatShading actif,
// pas de texture photo. Toutes les animations sont pilotées par
// useCurrentFrame() directement en props JSX (jamais useFrame/horloge R3F,
// qui ne tourne pas — @remotion/three force frameloop="never" et laisse
// Remotion piloter image par image pour rester seek-safe/déterministe).

const FPS = 30;
const W = 1080;
const H = 1920;
const BEAT_FRAMES = 120; // 4s par beat midground
const TOTAL_FRAMES = BEAT_FRAMES * 3;

const COLORS = {
  sun: "#FFE9A8",
  sunEmissive: "#FFB347",
  cloud: "#FFFFFF",
  bird: "#2B2140",
  accent1: "#FF6B6B",
  accent2: "#4ECDC4",
  accent3: "#FFD93D",
  midgroundText: "#2B2140",
  desk: "#5D4037",
  deskLeg: "#3E2723",
  laptop: "#2B2140",
  laptopScreen: "#8FD9FF",
  cup: "#F5F0E6",
  leaf: "#2F9E6E",
  leafDark: "#1F7A54",
  floor: "#C9B896",
};

// ---------- Texture texte (canvas 2D -> CanvasTexture), pas de police externe ----------

const useTextTexture = (text: string, color: string) => {
  return useMemo(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1024;
    canvas.height = 256;
    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "900 110px Arial, sans-serif";
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    return texture;
  }, [text, color]);
};

// ---------- FOND (z profond, -16 à -12) ----------

const Sun3D: React.FC = () => {
  const frame = useCurrentFrame();
  const rotation = interpolate(frame, [0, TOTAL_FRAMES], [0, Math.PI * 0.6]);
  const rayCount = 12;

  return (
    <group position={[0, 3.2, -16]}>
      <mesh>
        <sphereGeometry args={[2.1, 16, 16]} />
        <meshStandardMaterial
          color={COLORS.sun}
          emissive={COLORS.sunEmissive}
          emissiveIntensity={0.9}
          flatShading
        />
      </mesh>
      <group rotation={[0, 0, rotation]}>
        {Array.from({ length: rayCount }).map((_, i) => {
          const angle = (i / rayCount) * Math.PI * 2;
          const dist = 3.1;
          return (
            <mesh
              key={i}
              position={[Math.cos(angle) * dist, Math.sin(angle) * dist, 0]}
              rotation={[0, 0, angle + Math.PI / 2]}
            >
              <boxGeometry args={[0.28, 0.9, 0.28]} />
              <meshStandardMaterial color={COLORS.sun} flatShading />
            </mesh>
          );
        })}
      </group>
    </group>
  );
};

const CloudCluster: React.FC<{ baseX: number; y: number; z: number; speed: number; scale: number }> = ({
  baseX,
  y,
  z,
  speed,
  scale,
}) => {
  const frame = useCurrentFrame();
  const range = 16;
  const x = baseX + Math.sin((frame * speed) / 60) * range * 0.3 + (frame * speed) / 30;
  const wrappedX = (((x + range) % (range * 2)) - range) * 1;

  return (
    <group position={[wrappedX, y, z]} scale={scale}>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[1, 8, 6]} />
        <meshStandardMaterial color={COLORS.cloud} flatShading />
      </mesh>
      <mesh position={[0.9, 0.15, 0.1]}>
        <sphereGeometry args={[0.7, 8, 6]} />
        <meshStandardMaterial color={COLORS.cloud} flatShading />
      </mesh>
      <mesh position={[-0.85, 0.1, -0.1]}>
        <sphereGeometry args={[0.65, 8, 6]} />
        <meshStandardMaterial color={COLORS.cloud} flatShading />
      </mesh>
    </group>
  );
};

const Bird3D: React.FC<{ fromLeft: boolean; delay: number; y: number; z: number }> = ({
  fromLeft,
  delay,
  y,
  z,
}) => {
  const frame = useCurrentFrame() - delay;
  if (frame < 0) return null;

  const progress = interpolate(frame, [0, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.linear,
  });
  const startX = fromLeft ? -9 : 9;
  const endX = fromLeft ? 9 : -9;
  const x = interpolate(progress, [0, 1], [startX, endX]);
  const bob = Math.sin(frame / 6) * 0.35;
  const flap = Math.sin(frame / 4) * 0.5 + 0.5;

  return (
    <group position={[x, y + bob, z]} rotation={[0, fromLeft ? 0 : Math.PI, 0]}>
      <mesh rotation={[0, 0, flap * 0.6]} position={[-0.35, 0, 0]}>
        <coneGeometry args={[0.18, 0.7, 3]} />
        <meshStandardMaterial color={COLORS.bird} flatShading />
      </mesh>
      <mesh rotation={[0, 0, -flap * 0.6]} position={[0.35, 0, 0]}>
        <coneGeometry args={[0.18, 0.7, 3]} />
        <meshStandardMaterial color={COLORS.bird} flatShading />
      </mesh>
    </group>
  );
};

const Background3D: React.FC = () => (
  <>
    <mesh position={[0, 0, -20]}>
      <planeGeometry args={[40, 60]} />
      <meshBasicMaterial color="#FFB877" />
    </mesh>
    <Sun3D />
    <CloudCluster baseX={-4} y={4.5} z={-13} speed={0.5} scale={1.1} />
    <CloudCluster baseX={5} y={3} z={-14} speed={0.3} scale={0.8} />
    <CloudCluster baseX={0} y={5.5} z={-12} speed={0.7} scale={0.6} />
    <Bird3D fromLeft y={2} z={-9} delay={20} />
    <Bird3D fromLeft={false} y={1.2} z={-10} delay={70} />
    <Bird3D fromLeft y={3} z={-8} delay={140} />
    <Bird3D fromLeft={false} y={0.5} z={-9.5} delay={210} />
  </>
);

// ---------- MIDGROUND (z proche du centre, -3) ----------

const MidgroundBeat3D: React.FC<{ label: string; accent: string; variant: 0 | 1 | 2 }> = ({
  label,
  accent,
  variant,
}) => {
  const frame = useLocalFrame();
  const { fps } = useVideoConfig();
  const texture = useTextTexture(label, COLORS.midgroundText);

  const entrance = spring({ frame, fps, config: { damping: 14, mass: 0.6 } });
  const scale = interpolate(entrance, [0, 1], [0.3, 1]);
  const spin = interpolate(frame, [0, 100], [0, Math.PI * 2]);
  const bounce = Math.abs(Math.sin(frame / 12)) * 0.6;

  return (
    <group position={[0, 0.6, -3]}>
      <mesh scale={[3.4 * scale, 0.85 * scale, 1]}>
        <planeGeometry args={[1, 1]} />
        <meshBasicMaterial map={texture} transparent />
      </mesh>

      {variant === 0 && (
        <mesh position={[0, -1.6, 0]} rotation={[spin * 0.6, spin, 0]} scale={scale}>
          <icosahedronGeometry args={[0.55, 0]} />
          <meshStandardMaterial color={accent} flatShading />
        </mesh>
      )}

      {variant === 1 && (
        <mesh position={[0, -1.6, 0]} rotation={[Math.PI / 2, spin, 0]} scale={scale}>
          <torusGeometry args={[0.5, 0.18, 8, 16]} />
          <meshStandardMaterial color={accent} flatShading />
        </mesh>
      )}

      {variant === 2 && (
        <group position={[0, -1.6 + bounce, 0]} scale={scale}>
          <mesh rotation={[spin * 0.3, spin * 0.3, 0]}>
            <boxGeometry args={[0.7, 0.7, 0.7]} />
            <meshStandardMaterial color={accent} flatShading />
          </mesh>
        </group>
      )}
    </group>
  );
};

const Midground3D: React.FC = () => {
  const frame = useCurrentFrame();
  const beatIndex = Math.min(2, Math.floor(frame / BEAT_FRAMES));
  const beats: Array<{ label: string; accent: string; variant: 0 | 1 | 2 }> = [
    { label: "Motion Graphics", accent: COLORS.accent1, variant: 0 },
    { label: "Transitions", accent: COLORS.accent2, variant: 1 },
    { label: "Animations", accent: COLORS.accent3, variant: 2 },
  ];
  const beat = beats[beatIndex];
  const localFrame = frame - beatIndex * BEAT_FRAMES;

  return (
    <group>
      {/* On ne monte que le beat courant (Composition parente re-render chaque
          frame de toute façon) — frame locale recalée pour que chaque beat
          rejoue sa propre entrée. */}
      <MidgroundBeatWithLocalFrame frame={localFrame} {...beat} />
    </group>
  );
};

const MidgroundBeatWithLocalFrame: React.FC<{
  frame: number;
  label: string;
  accent: string;
  variant: 0 | 1 | 2;
}> = ({ frame, ...rest }) => {
  return (
    <LocalFrameProvider frame={frame}>
      <MidgroundBeat3D {...rest} />
    </LocalFrameProvider>
  );
};

// useCurrentFrame() vient du contexte Remotion (frame absolue du composant
// parent) — pour rejouer l'entrée de CHAQUE beat depuis 0, on a besoin d'une
// frame locale. Remotion n'expose pas de "sub-timeline" en dehors de
// <Sequence>, qui ne s'utilise qu'en DOM/CSS. Pour du contenu Three.js,
// on override simplement le frame lu par MidgroundBeat3D via ce petit
// provider (context React), pas via Sequence.
const LocalFrameContext = React.createContext<number | null>(null);
const LocalFrameProvider: React.FC<{ frame: number; children: React.ReactNode }> = ({
  frame,
  children,
}) => <LocalFrameContext.Provider value={frame}>{children}</LocalFrameContext.Provider>;

// Lit la frame locale du beat si un LocalFrameProvider est monté au-dessus,
// sinon retombe sur la frame globale Remotion (comportement par défaut).
const useLocalFrame = () => {
  const local = React.useContext(LocalFrameContext);
  const global = useCurrentFrame();
  return local ?? global;
};

// ---------- PREMIER PLAN (z proche caméra, +3) ----------

const Foreground3D: React.FC = () => {
  const frame = useCurrentFrame();
  const idle = Math.sin(frame / 25) * 0.06;

  return (
    <group position={[0, -3.4 + idle, 3]}>
      {/* Sol / terrasse */}
      <mesh position={[0, -1.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[14, 6]} />
        <meshStandardMaterial color={COLORS.floor} flatShading />
      </mesh>

      {/* Bureau */}
      <mesh position={[0, -0.35, 0]}>
        <boxGeometry args={[3.2, 0.22, 1.2]} />
        <meshStandardMaterial color={COLORS.desk} flatShading />
      </mesh>
      <mesh position={[-1.35, -0.85, 0.4]}>
        <boxGeometry args={[0.18, 0.8, 0.18]} />
        <meshStandardMaterial color={COLORS.deskLeg} flatShading />
      </mesh>
      <mesh position={[1.35, -0.85, 0.4]}>
        <boxGeometry args={[0.18, 0.8, 0.18]} />
        <meshStandardMaterial color={COLORS.deskLeg} flatShading />
      </mesh>

      {/* Laptop */}
      <mesh position={[-0.1, -0.18, -0.1]}>
        <boxGeometry args={[1.1, 0.06, 0.7]} />
        <meshStandardMaterial color={COLORS.laptop} flatShading />
      </mesh>
      <mesh position={[-0.1, 0.32, -0.42]} rotation={[-0.25, 0, 0]}>
        <boxGeometry args={[1.1, 0.7, 0.06]} />
        <meshStandardMaterial color={COLORS.laptop} flatShading />
      </mesh>
      <mesh position={[-0.1, 0.32, -0.39]} rotation={[-0.25, 0, 0]}>
        <planeGeometry args={[0.95, 0.55]} />
        <meshBasicMaterial color={COLORS.laptopScreen} />
      </mesh>

      {/* Tasse */}
      <mesh position={[1.1, -0.05, 0.2]}>
        <cylinderGeometry args={[0.16, 0.13, 0.32, 10]} />
        <meshStandardMaterial color={COLORS.cup} flatShading />
      </mesh>

      {/* Palmier, coin gauche */}
      <group position={[-3.6, 0.4, -0.6]}>
        {[0, 1, 2, 3, 4].map((i) => (
          <mesh
            key={i}
            position={[Math.cos((i / 5) * Math.PI - 0.4) * 0.9, Math.sin((i / 5) * Math.PI - 0.4) * 0.5 + 0.4, 0]}
            rotation={[0, 0, (i / 5) * Math.PI - 0.4 + Math.PI / 2]}
          >
            <coneGeometry args={[0.35, 1.7, 3]} />
            <meshStandardMaterial color={i % 2 === 0 ? COLORS.leaf : COLORS.leafDark} flatShading />
          </mesh>
        ))}
        <mesh position={[0, -0.9, 0]}>
          <cylinderGeometry args={[0.1, 0.14, 1.4, 6]} />
          <meshStandardMaterial color={COLORS.deskLeg} flatShading />
        </mesh>
      </group>
    </group>
  );
};

// ---------- CAMÉRA ----------

const CameraRig: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  // Léger travelling latéral en boucle douce : preuve du vrai 3D — le fond
  // (z=-16) se déplace beaucoup moins à l'écran que le premier plan (z=3)
  // pour un même mouvement caméra, contrairement à un parallax CSS simulé.
  const x = Math.sin(t * 0.35) * 1.1;
  const y = 0.4 + Math.sin(t * 0.2) * 0.15;

  return <PerspectiveCamera makeDefault position={[x, y, 9]} fov={55} />;
};

// ---------- SCÈNE COMPLÈTE ----------

const Scene3D: React.FC = () => (
  <>
    <CameraRig />
    <ambientLight intensity={0.65} />
    <directionalLight position={[4, 6, 6]} intensity={1.1} />
    <Background3D />
    <Midground3D />
    <Foreground3D />
  </>
);

export const VoxLayeredScene3D: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ThreeCanvas width={W} height={H}>
        <Scene3D />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

export const VoxLayeredScene3DComposition: React.FC = () => (
  <Composition
    id="VoxLayeredScene3D"
    component={VoxLayeredScene3D}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={TOTAL_FRAMES}
  />
);
