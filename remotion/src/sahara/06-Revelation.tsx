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
import { Grain, Vignette, FPS, W, H } from "./shared";
import { Captions, useMots } from "./captions";
import { Backdrop } from "./backdrop";
import { Stage, duoProgress, CurioWindow } from "./stage";
import { DUREES, REVELATION } from "./timing";

// Beat 6 — la révélation, et le beat le plus long du reel.
// « Et ce phosphore vient surtout d'un endroit précis : la dépression du
//   Bodélé, au Tchad. C'était un lac immense, aujourd'hui asséché. Son sable
//   est fait de squelettes d'algues microscopiques. »
//
// Un seul geste du début à la fin : un zoom qui ne s'arrête jamais, de
// l'orbite au microscope. Trois échelles s'enchaînent — vue satellite, grains
// de sable, diatomées — et chacune prend le relais de la précédente en
// grandissant depuis son centre, pendant que celle d'avant continue de
// s'ouvrir. C'est ce recouvrement qui fait croire à une descente continue
// plutôt qu'à trois plans successifs ; une coupe sèche casserait l'illusion,
// et c'est le seul endroit du reel où l'enchaîné se justifie.
//
// La vue satellite est une vraie image NASA du Bodélé et les diatomées de
// vraies photos NOAA au microscope : la géographie et la science du reel ne
// sont pas illustrées de mémoire (cf. assets/sahara_amazonie/SOURCES.md).
//
// Le beat s'ouvre en CARTE, le temps qu'on nomme le lieu : une vue satellite
// est une pièce à conviction, et le nom du lieu prend la place au-dessus. Le
// plein écran revient pour la descente — un zoom continu dans une vignette de
// 972 px ne se lirait pas, c'est l'échelle qui est le sujet.

export type Layer = {
  src: string;
  from: number;
  until: number;
  zoomFrom: number;
  zoomTo: number;
};

// Les trois échelles du sahara n'ont pas la même durée : on reste sur le lieu
// tant que la voix en parle (« un lac immense, aujourd'hui asséché » court
// jusqu'à 8,82 s), et le sable ne cède aux diatomées qu'au mot « algues », à
// 12,34 s. C'est la valeur par défaut ; un autre reel passe ses propres
// échelles, en nombre libre.
const LAYERS_SAHARA: Layer[] = [
  {
    src: "sahara/bodele.jpg",
    from: 0,
    until: REVELATION.sableFrom,
    zoomFrom: 1.0,
    zoomTo: 2.5,
  },
  {
    src: "sahara/sable_macro.jpg",
    from: REVELATION.sableFrom,
    until: REVELATION.diatomeesFrom,
    zoomFrom: 0.75,
    zoomTo: 2.0,
  },
  {
    src: "sahara/diatomees.jpg",
    from: REVELATION.diatomeesFrom,
    until: DUREES.revelation,
    zoomFrom: 0.7,
    zoomTo: 1.8,
  },
];

export type RevelationProps = {
  duration?: number;
  segment?: string;
  /** Les échelles à traverser, de la plus large à la plus serrée. */
  layers?: Layer[];
  /** Recouvrement entre deux échelles : c'est lui qui fait lire la descente
   *  comme un seul geste plutôt que comme des plans successifs. */
  overlap?: number;
  curio?: CurioWindow;
  accent?: string;
};

export const Revelation: React.FC<RevelationProps> = ({
  segment = "mots/06-revelation",
  layers: LAYERS = LAYERS_SAHARA,
  overlap: OVERLAP = REVELATION.overlap,
  curio = REVELATION.curio,
  accent = "#8C6B2F",
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);

  // La carte ne s'ouvre que le temps que Curio dise « un endroit précis » :
  // la descente qui suit a besoin de tout l'écran.
  const t = duoProgress(frame, curio);

  return (
    <Stage
      t={t}
      background={
        <>
          <Backdrop frame={frame} accent={accent} />
        </>
      }
      curio={curio}
      overlay={
        <>
          <Vignette strength={0.6} />
          <Grain frame={frame} opacity={0.1} />
          {/* Les sous-titres descendent sur la carte basse quand Curio occupe
              le haut : entre les deux cartes il ne reste que 50 px. */}
          <Captions mots={mots} frame={frame} fps={FPS} />
        </>
      }
    >
      {LAYERS.map((layer, i) => {
        // Chaque échelle apparaît en grandissant et reste ensuite : celles du
        // dessous continuent de zoomer hors cadre, on ne les voit plus mais
        // leur mouvement porte encore la descente aux bords de l'image.
        // Chaque échelle entre en grandissant, sur le recouvrement, puis
        // continue de zoomer jusqu'à la fin du plan — celles du dessous ne se
        // voient plus mais leur mouvement porte encore la descente aux bords.
        const enter = interpolate(
          frame,
          [layer.from - OVERLAP, layer.from],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) },
        );
        if (enter <= 0) return null;
        const zoom = interpolate(
          frame,
          [layer.from - OVERLAP, layer.until],
          [layer.zoomFrom, layer.zoomTo],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad) },
        );
        return (
          <AbsoluteFill key={i} style={{ opacity: enter, overflow: "hidden" }}>
            <Img
              src={staticFile(layer.src)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${zoom})`,
              }}
            />
          </AbsoluteFill>
        );
      })}

    </Stage>
  );
};

export const RevelationComposition: React.FC = () => (
  <Composition
    id="sahara-06-revelation"
    component={Revelation}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.revelation}
  />
);
