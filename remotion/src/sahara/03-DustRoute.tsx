import React, { useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill,
  Composition,
  continueRender,
  delayRender,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Captions, useMots } from "./captions";
import { DUREES, ROUTE } from "./timing";
import * as THREE from "three";

// Reel « le Sahara nourrit l'Amazonie » — beat 3, le voyage.
// « Chaque année, le vent arrache au Sahara des millions de tonnes de poussière
//   et les emporte au-dessus de l'Atlantique. »
//
// Un globe en vraie 3D, pas une carte plate : le trajet fait un quart de tour
// de planète, et c'est le seul moyen de le montrer sans mentir sur les
// distances. La texture est le Blue Marble de la NASA déjà présent dans le
// repo (remotion/public/desert-sel/), réutilisé tel quel — pas de copie.
//
// Le globe tourne pour amener successivement les deux points face caméra,
// pendant que l'arc se dessine entre eux. La caméra, elle, ne bouge pas :
// deux mouvements simultanés donneraient le mal de mer.

const FPS = 30;
const W = 1080;
const H = 1920;
// Valeurs du premier montage par défaut, surchargées par le second.
export type DustRouteProps = {
  duration: number;
  segment: string;
  revealFrom: number;
  revealTo: number;
  originOn: number;
  arcFrom: number;
  arcTo: number;
  targetOn: number;
};

// Blue Marble réduit à 4096×2048 : la source du repo fait 8192×4096, soit
// 128 Mo de VRAM non compressée, que le rasteriseur logiciel utilisé au rendu
// (ANGLE/SwiftShader, pas de GPU en headless) refuse silencieusement — le
// globe sortait noir sans la moindre erreur.
const TEXTURE = "sahara/earth_4096.jpg";

// Dépression du Bodélé (Tchad) et Amazonie centrale. Coordonnées réelles :
// tout le propos du reel est géographique, une approximation se verrait.
const BODELE: [number, number] = [16.5, 17.5]; // lat, lon
const AMAZONIE: [number, number] = [-3.1, -60.0];

const GLOBE_R = 2;
const ARC_LIFT = 0.34; // hauteur de l'arc au-dessus de la surface
const ARC_POINTS = 220;
const DUST_COUNT = 90;

// Timings

/** Latitude/longitude vers la position sur la sphère, dans la convention de
 *  SphereGeometry : u = 0 à la longitude -180. */
const toVec3 = ([lat, lon]: [number, number], radius: number): THREE.Vector3 => {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lon + 180) * Math.PI) / 180;
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  );
};

/** Rotation Y qui amène une longitude face à la caméra (+Z). */
const rotationForLon = (lon: number) => ((-90 - lon) * Math.PI) / 180;

/** Points de l'arc : grand cercle entre les deux villes, soulevé au milieu. */
const buildArc = (): THREE.Vector3[] => {
  const a = toVec3(BODELE, 1);
  const b = toVec3(AMAZONIE, 1);
  const points: THREE.Vector3[] = [];
  for (let i = 0; i <= ARC_POINTS; i++) {
    const t = i / ARC_POINTS;
    // Interpoler puis renormaliser suit le grand cercle d'assez près pour
    // 77° d'arc, sans sortir l'artillerie des quaternions.
    const p = a.clone().lerp(b, t).normalize();
    points.push(p.multiplyScalar(GLOBE_R + ARC_LIFT * Math.sin(Math.PI * t)));
  }
  return points;
};

const useTexture = (src: string) => {
  const [texture, setTexture] = useState<THREE.Texture | null>(null);
  useEffect(() => {
    // Chargement par <img> puis THREE.Texture, et non par TextureLoader : c'est
    // la voie déjà éprouvée dans ce repo (useDelayedImagePreload de
    // MapZoomUyuni, commit 0f3dc94). Sans delayRender, Remotion capture avant
    // la fin du décodage et le globe sort noir.
    const handle = delayRender(`texture-${src}`);
    const img = new Image();
    img.onload = () => {
      const t = new THREE.Texture(img);
      t.colorSpace = THREE.SRGBColorSpace;
      t.needsUpdate = true;
      setTexture(t);
      continueRender(handle);
    };
    img.onerror = () => continueRender(handle);
    img.src = src;
  }, [src]);
  return texture;
};

const Marker: React.FC<{
  position: THREE.Vector3;
  color: string;
  visible: number;
  pulse: number;
}> = ({ position, color, visible, pulse }) => {
  if (visible <= 0) return null;
  return (
    <group position={position}>
      <mesh scale={visible}>
        <sphereGeometry args={[0.045, 20, 20]} />
        <meshBasicMaterial color={color} />
      </mesh>
      {/* Halo : il grossit et s'efface, c'est ce qui fait lire le point comme
          un signal et non comme une pastille collée. */}
      <mesh scale={visible * (1 + pulse * 2.2)}>
        <sphereGeometry args={[0.07, 20, 20]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.5 * visible * (1 - pulse)}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
};

const Scene: React.FC<{ frame: number; texture: THREE.Texture; p: DustRouteProps }> = ({
  frame,
  texture,
  p,
}) => {
  const arc = useMemo(buildArc, []);

  // Le globe pivote du Bodélé vers l'Amazonie, en retard sur le tracé : l'arc
  // part avant que la rotation commence vraiment, sinon on ne voit jamais son
  // point de départ.
  const spin = interpolate(
    frame,
    [p.originOn, p.arcTo + 20],
    [rotationForLon(BODELE[1]), rotationForLon(AMAZONIE[1])],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    },
  );

  const intro = interpolate(frame, [0, p.revealTo], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const globeScale = 0.86 + 0.14 * intro;

  const drawn = interpolate(frame, [p.arcFrom, p.arcTo], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  const originIn = interpolate(frame, [p.originOn, p.originOn + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const targetIn = interpolate(frame, [p.targetOn, p.targetOn + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Un tube, pas une ligne : LineBasicMaterial ignore `linewidth` sur presque
  // toutes les plateformes et le trait sortait à 1 px, invisible sous les
  // grains. La géométrie est reconstruite sur la portion tracée à chaque
  // image — 220 points, le coût est négligeable.
  const tube = useMemo(() => {
    const n = Math.max(2, Math.round(drawn * ARC_POINTS));
    const curve = new THREE.CatmullRomCurve3(arc.slice(0, n + 1));
    return new THREE.TubeGeometry(curve, Math.max(2, n), 0.016, 8, false);
  }, [arc, drawn]);

  // La poussière suit l'arc en traînée derrière la tête du tracé, chaque grain
  // avec son propre retard : un peloton compact ne ressemblerait pas à du vent.
  const dust = useMemo(
    () =>
      new Array(DUST_COUNT).fill(0).map((_, i) => ({
        lag: (i / DUST_COUNT) * 0.22 + Math.random() * 0.03,
        off: new THREE.Vector3(
          (Math.random() - 0.5) * 0.09,
          (Math.random() - 0.5) * 0.09,
          (Math.random() - 0.5) * 0.09,
        ),
        size: 0.012 + Math.random() * 0.016,
      })),
    [],
  );

  return (
    <>
      {/* Lumière presque frontale, légèrement décalée : un vrai éclairage
          rasant plongerait dans l'ombre toute la moitié ouest — exactement
          celle que le trajet doit traverser. On perd en réalisme
          astronomique, on gagne la lisibilité du propos. */}
      <ambientLight intensity={1.05} />
      <directionalLight position={[2.5, 2, 8]} intensity={1.8} />

      <group rotation={[0, spin, 0]} scale={globeScale}>
        <mesh>
          <sphereGeometry args={[GLOBE_R, 96, 96]} />
          <meshStandardMaterial map={texture} roughness={1} metalness={0} />
        </mesh>

        <mesh geometry={tube}>
          <meshBasicMaterial color="#F5C77A" transparent opacity={0.92} />
        </mesh>

        {dust.map((d, i) => {
          const t = drawn - d.lag;
          if (t <= 0 || drawn >= 1) return null;
          const p = arc[Math.round(t * ARC_POINTS)];
          if (!p) return null;
          return (
            <mesh key={i} position={p.clone().add(d.off)}>
              <sphereGeometry args={[d.size, 6, 6]} />
              <meshBasicMaterial
                color="#E8C489"
                transparent
                opacity={0.35 + 0.5 * (1 - d.lag / 0.25)}
                depthWrite={false}
              />
            </mesh>
          );
        })}

        <Marker
          position={toVec3(BODELE, GLOBE_R + 0.02)}
          color="#F5A623"
          visible={originIn}
          pulse={interpolate(frame, [p.originOn, p.originOn + 26], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}
        />
        <Marker
          position={toVec3(AMAZONIE, GLOBE_R + 0.02)}
          color="#5BD98A"
          visible={targetIn}
          pulse={interpolate(frame, [p.targetOn, p.targetOn + 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}
        />
      </group>
    </>
  );
};

export const DustRoute: React.FC<DustRouteProps> = (p) => {
  const frame = useCurrentFrame();
  const mots = useMots(p.segment);
  // La texture est chargée ICI, dans l'arbre React classique, et passée en
  // prop : à l'intérieur de <ThreeCanvas>, react-three-fiber monte son propre
  // reconciler et le contexte Remotion ne le traverse pas. delayRender() y est
  // sans effet — le rendu partait sans attendre et la sphère sortait nue.
  // Même raison pour laquelle `frame` descend en prop plutôt que par
  // useCurrentFrame().
  const texture = useTexture(staticFile(TEXTURE));

  const halo = interpolate(frame, [0, p.revealTo], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#05070C" }}>
      {/* Halo atmosphérique peint en CSS derrière le globe : en 3D il aurait
          coûté une passe de post-traitement pour le même résultat. */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(58% 33% at 50% 50%," +
            `rgba(96,146,214,${0.30 * halo}) 0%,` +
            `rgba(50,86,140,${0.16 * halo}) 45%, rgba(5,7,12,0) 72%)`,
        }}
      />
      {texture ? (
        <ThreeCanvas width={W} height={H} camera={{ fov: 42, position: [0, 0, 12] }}>
          <Scene frame={frame} texture={texture} p={p} />
        </ThreeCanvas>
      ) : null}
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};

export const DustRouteComposition: React.FC = () => (
  <Composition
    id="sahara-03-route"
    component={DustRoute}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.route}
    defaultProps={{
      duration: DUREES.route,
      segment: "mots/03-route",
      ...ROUTE,
    }}
  />
);
