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
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Grain, SANS, CREAM, FPS, W, H } from "./shared";
import { Backdrop } from "./backdrop";
import { Stage, duoProgress, CurioWindow } from "./stage";
import { DUREES, CAMIONS } from "./timing";

// Beat 4 — le chiffre.
// « Vingt-sept millions de tonnes finissent leur voyage en Amazonie.
//   L'équivalent d'environ un million de camions de sable, déversés depuis le
//   ciel. »
//
// Un nombre écrit ne veut rien dire à un enfant de primaire : c'est la MASSE
// qui doit se voir. La caméra part sur un camion isolé, à hauteur d'homme,
// puis recule sans coupe jusqu'à ce que le cadre en contienne des centaines
// qui se perdent dans la brume. Le chiffre n'arrive qu'une fois qu'on a vu
// l'étendue, jamais avant : sinon il explique une image au lieu d'être
// expliqué par elle.
//
// Les camions sont un InstancedMesh : un seul appel de rendu pour les 480
// exemplaires, faute de quoi le rendu logiciel (aucun GPU en headless) ne
// tiendrait pas les 240 images.

// Les valeurs du premier montage sont les valeurs par défaut ; le second les
// surcharge par props. Dupliquer le composant aurait dupliqué la flotte, son
// bruit déterministe et ses réglages de brume.
export type CamionsProps = {
  duration: number;
  numberIn: number;
  segment: string;
  curio?: CurioWindow;
  /** L'objet instancié. PNG à fond transparent : le matériau utilise
   *  `alphaTest`, un fond opaque ferait des vignettes carrées. */
  texture?: string;
  /** Largeur d'un exemplaire en unités monde. Un objet plus haut que large
   *  doit être réduit, sans quoi les rangées se masquent l'une l'autre. */
  objetLargeur?: number;
  /** Le chiffre et sa légende. */
  nombre?: string;
  legende?: string;
  /** Couleurs du plan : dégradé du sol, brume, accent du fond de carte et
   *  couleur de la légende. La flotte de camions est ocre, un champ de Terres
   *  ne peut pas l'être. */
  degrade?: string;
  brume?: string;
  accent?: string;
  legendeCouleur?: string;
};
const COLS = 24;
const ROWS = 20;
const COUNT = COLS * ROWS;

const SPACING_X = 3.4;
const SPACING_Z = 5.2;
const TRUCK_W = 2.6; // largeur en unités monde, valeur du sahara

const useTexture = (src: string) => {
  // Chargé hors du canvas : le contexte Remotion ne traverse pas le reconciler
  // de react-three-fiber, delayRender() y serait sans effet et la première
  // image partirait avant le décodage.
  const [texture, setTexture] = useState<THREE.Texture | null>(null);
  useEffect(() => {
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

const Fleet: React.FC<{ texture: THREE.Texture; ratio: number; largeur: number }> = ({
  texture,
  ratio,
  largeur: TRUCK_W,
}) => {
  // L'InstancedMesh est construit et rempli dans un useMemo, PAS dans un
  // useEffect : Remotion capture l'image sans attendre les effets, et les 480
  // instances restaient toutes à la matrice identité — empilées à l'origine,
  // elles ne montraient qu'un seul camion. Ici tout est posé avant que la
  // première image puisse être prise.
  const mesh = useMemo(() => {
    const geometry = new THREE.PlaneGeometry(TRUCK_W, TRUCK_W / ratio);
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      alphaTest: 0.5,
      toneMapped: false,
    });
    const instanced = new THREE.InstancedMesh(geometry, material, COUNT);
    const dummy = new THREE.Object3D();
    let i = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        // Désordre déterministe : un Math.random() rejouerait une disposition
        // différente à chaque image et la flotte grouillerait.
        const n1 = Math.sin((r * 12.9898 + c * 78.233) * 43758.5453);
        const n2 = Math.sin((r * 39.3468 + c * 11.135) * 24634.6345);
        const scale = 0.9 + (n2 - Math.floor(n2)) * 0.22;
        dummy.position.set(
          (c - (COLS - 1) / 2) * SPACING_X + (n1 - Math.floor(n1) - 0.5) * 1.5,
          (TRUCK_W / ratio / 2) * scale,
          -r * SPACING_Z + (n2 - Math.floor(n2) - 0.5) * 1.9,
        );
        dummy.scale.setScalar(scale);
        dummy.updateMatrix();
        instanced.setMatrixAt(i++, dummy.matrix);
      }
    }
    instanced.instanceMatrix.needsUpdate = true;
    return instanced;
  }, [texture, ratio, TRUCK_W]);

  return <primitive object={mesh} />;
};

const Scene: React.FC<{
  frame: number;
  texture: THREE.Texture;
  ratio: number;
  duration: number;
  largeur: number;
  brume: string;
}> = ({ frame, texture, ratio, duration, largeur, brume }) => {
  // Le recul : un camion seul, puis la flotte. L'accélération est en ease-in
  // pour que le premier tiers reste lisible et que l'ampleur arrive d'un coup.
  // Ne pas reculer plus loin : au-delà, chaque camion tombe sous le pixel et
  // la masse se lit comme du bruit, pas comme un nombre.
  const z = interpolate(frame, [0, duration], [5, 26], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });
  const y = interpolate(frame, [0, duration], [1.4, 5.4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });

  return (
    <>
      <PerspectiveRig y={y} z={z} />
      <ambientLight intensity={1} />
      <Fleet texture={texture} ratio={ratio} largeur={largeur} />
      {/* Brume : elle mange les rangées lointaines et laisse croire que la
          flotte continue au-delà du cadre — 480 camions doivent en suggérer
          un million. */}
      <fog attach="fog" args={[brume, 34, 130]} />
    </>
  );
};

/** La caméra recule et monte : sans la prise de hauteur, les rangées se
 *  masquent l'une l'autre et le nombre ne se voit jamais. */
const PerspectiveRig: React.FC<{ y: number; z: number }> = ({ y, z }) => {
  const { camera } = useThree();
  camera.position.set(0, y, z);
  // Viser haut et loin : trop de plongée et la flotte se tasse dans le tiers
  // bas du 9:16, laissant un vide brun sur toute la moitié haute.
  camera.lookAt(0, 3.2, -46);
  camera.updateProjectionMatrix();
  return null;
};

export const Camions: React.FC<CamionsProps> = ({
  duration,
  numberIn: numberInFrame,
  segment,
  curio,
  texture: textureSrc = "sahara/camion.png",
  objetLargeur = TRUCK_W,
  nombre = "27 millions",
  legende = "DE TONNES PAR AN",
  degrade = "linear-gradient(180deg, #2A1B0C 0%, #191106 46%, #0C0805 100%)",
  brume = "#171008",
  accent = "#8C6B2F",
  legendeCouleur = "#F5C77A",
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  const texture = useTexture(staticFile(textureSrc));
  const t = duoProgress(frame, curio);
  // `texture.image` est typé `{}` par three : on relit les dimensions sur
  // l'élément HTML, qui est bien ce qu'on a passé au constructeur.
  const img = texture?.image as HTMLImageElement | undefined;
  const ratio = img?.width && img?.height ? img.width / img.height : 1.68;

  // « 27 millions » est dit dès 0,58 s : le chiffre ne peut pas attendre.
  const numberIn = interpolate(frame, [numberInFrame, numberInFrame + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <Stage
      t={t}
      curio={curio}
      background={<Backdrop frame={frame} accent={accent} />}
      overlay={
        <>
          <Grain frame={frame} opacity={0.08} />
          <Captions mots={mots} frame={frame} fps={FPS} />
        </>
      }
    >
      <AbsoluteFill
        style={{
          background: degrade,
        }}
      />
      {texture ? (
        <ThreeCanvas width={W} height={H} camera={{ fov: 46, position: [0, 1.4, 5] }}>
          <Scene
            frame={frame}
            texture={texture}
            ratio={ratio}
            duration={duration}
            largeur={objetLargeur}
            brume={brume}
          />
        </ThreeCanvas>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 230,
          textAlign: "center",
          opacity: numberIn,
          transform: `translateY(${(1 - numberIn) * -16}px)`,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 126,
            letterSpacing: -2,
            color: CREAM,
            textShadow: "0 6px 30px rgba(0,0,0,0.95)",
          }}
        >
          {nombre}
        </div>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 48,
            letterSpacing: 8,
            color: legendeCouleur,
            marginTop: 2,
            textShadow: "0 3px 18px rgba(0,0,0,0.95)",
          }}
        >
          {legende}
        </div>
      </div>

    </Stage>
  );
};

export const CamionsComposition: React.FC = () => (
  <Composition
    id="sahara-04-camions"
    component={Camions}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.camions}
    defaultProps={{
      duration: DUREES.camions,
      numberIn: CAMIONS.numberIn,
      segment: "mots/04-camions",
    }}
  />
);
