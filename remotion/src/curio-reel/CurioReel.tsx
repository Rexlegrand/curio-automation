import React, { useMemo } from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Caption, parseSrt } from "@remotion/captions";
import { approximateWordCaptions, groupWordsIntoLines } from "../tiktok-captions/words";

// Reel complet rendu 100% localement — aucune plateforme externe, aucun hook
// Dreamina. Trois couches empilées :
//
//   1. DÉCOR   — une photo par segment, avec un mouvement de caméra et, quand
//                le segment s'y prête, un cartouche de lieu qui monte à l'écran.
//   2. CURIO   — le personnage découpé, qui s'illumine au rythme de sa voix.
//                Trois états : grand au centre (hook, CTA), pastille ronde en
//                bas à droite (intervention), absent (le narrateur parle).
//   3. SOUS-TITRES — une ligne à la fois, mot actif surligné. La couleur du mot
//                actif change selon QUI parle : vert Curio, bleu narrateur.
//
// Tout ce qui varie image par image (niveau de voix, taille et présence de
// Curio) est précalculé côté Python et passé en tableaux : le rendu est
// déterministe et ne dépend d'aucune heuristique côté React.

const FPS = 30;
const W = 1080;
const H = 1920;

// Curio, état « grand » (hook et CTA).
const BIG_HEIGHT = 860;
const BIG_CENTER_Y = 900;

// Curio, état « pastille » (intervention par-dessus le décor).
const PILL_SIZE = 260;
const PILL_CENTER_X = W - 60 - PILL_SIZE / 2;
const PILL_CENTER_Y = 1160;
const PILL_BG = "#132B52";

// Anneau vert « quelqu'un parle », référence Discord — validé par Benjamin le
// 31/08 contre la variante bleu charte.
const GLOW = "rgba(60, 230, 130, 0.85)";

const COLOR_CURIO = "#3CE682";
const COLOR_NARRATEUR = "#3EC1FF";

const MAX_CHARS_PER_LINE = 28;

export type Scene = {
  start: number;
  duration: number;
  src: string;
  motion: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "pan-up";
  /** Cartouche de lieu, monte à l'écran en début de scène. Vide = aucun. */
  label: string;
};

export type SpeakerSpan = { startMs: number; endMs: number; speaker: "curio" | "narrateur" };

export type CurioReelProps = {
  curioSrc: string;
  scenes: Scene[];
  /** Niveau de voix de Curio par image, 0 → 1. Pilote la lumière. */
  levels: number[];
  /** 1 = Curio en grand au centre, 0 = en pastille. Lissé côté Python. */
  bigness: number[];
  /** 1 = Curio visible, 0 = absent de l'écran (le narrateur parle). */
  presence: number[];
  speakerSpans: SpeakerSpan[];
  srtText: string | null;
  captions: Caption[];
  totalFrames: number;
};

const at = (arr: number[], frame: number) =>
  arr.length === 0 ? 0 : arr[Math.min(Math.max(frame, 0), arr.length - 1)];

/** Mouvement de caméra d'une scène : échelle et translation à l'image locale. */
const cameraTransform = (motion: Scene["motion"], frame: number, duration: number) => {
  const p = interpolate(frame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  switch (motion) {
    case "zoom-in":
      return { scale: 1.06 + p * 0.14, x: 0, y: 0 };
    case "zoom-out":
      return { scale: 1.24 - p * 0.14, x: 0, y: 0 };
    case "pan-left":
      return { scale: 1.2, x: 60 - p * 120, y: 0 };
    case "pan-right":
      return { scale: 1.2, x: -60 + p * 120, y: 0 };
    case "pan-up":
      return { scale: 1.2, x: 0, y: 70 - p * 140 };
  }
};

const SceneLayer: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { scale, x, y } = cameraTransform(scene.motion, frame, scene.duration);

  // Cartouche de lieu : monte et s'efface. C'est la technique hors caméra du
  // beat (CLAUDE.md §10 : un mouvement de caméra ne suffit jamais seul).
  const labelIn = interpolate(frame, [6, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const labelOut = interpolate(frame, [scene.duration - 14, scene.duration - 4], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const labelOpacity = labelIn * labelOut;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#0E1013" }}>
      <Img
        src={staticFile(scene.src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${x}px, ${y}px)`,
        }}
      />
      {scene.label ? (
        <div
          style={{
            position: "absolute",
            left: 60,
            top: 300,
            opacity: labelOpacity,
            transform: `translateY(${(1 - labelIn) * 26}px)`,
            backgroundColor: "rgba(14,16,19,0.82)",
            borderLeft: `8px solid ${COLOR_CURIO}`,
            padding: "18px 30px",
            borderRadius: 14,
            fontFamily: "Arial, sans-serif",
            fontWeight: 700,
            fontSize: 52,
            color: "white",
            letterSpacing: 0.5,
          }}
        >
          {scene.label}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const CurioLayer: React.FC<{
  curioSrc: string;
  levels: number[];
  bigness: number[];
  presence: number[];
}> = ({ curioSrc, levels, bigness, presence }) => {
  const frame = useCurrentFrame();
  const level = at(levels, frame);
  const big = at(bigness, frame);
  const shown = at(presence, frame);

  if (shown <= 0.001) {
    return null;
  }

  const centerX = interpolate(big, [0, 1], [PILL_CENTER_X, W / 2]);
  const centerY = interpolate(big, [0, 1], [PILL_CENTER_Y, BIG_CENTER_Y]);
  const height = interpolate(big, [0, 1], [PILL_SIZE * 0.78, BIG_HEIGHT]);
  const bob = Math.sin((frame / FPS) * 1.7) * interpolate(big, [0, 1], [3, 10]);

  const glowCore = 8 + level * 14;
  const glowWide = 26 + level * 74;

  return (
    <AbsoluteFill style={{ opacity: shown }}>
      {/* Assombrissement du décor, uniquement quand Curio est en grand. */}
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: big * 0.62 }} />

      <div
        style={{
          position: "absolute",
          left: centerX - PILL_SIZE / 2,
          top: centerY - PILL_SIZE / 2,
          width: PILL_SIZE,
          height: PILL_SIZE,
          borderRadius: "50%",
          backgroundColor: PILL_BG,
          opacity: 1 - big,
          boxShadow: `0 0 0 ${3 + level * 7}px ${GLOW}, 0 0 ${24 + level * 46}px ${
            8 + level * 10
          }px ${GLOW}`,
        }}
      />

      <Img
        src={staticFile(curioSrc)}
        style={{
          position: "absolute",
          height,
          left: centerX,
          top: centerY + bob,
          transform: "translate(-50%, -50%)",
          filter:
            `drop-shadow(0 0 ${glowCore}px ${GLOW}) ` +
            `drop-shadow(0 0 ${glowWide}px ${GLOW}) ` +
            `drop-shadow(0 0 ${glowWide}px ${GLOW}) ` +
            `drop-shadow(0 6px 18px rgba(0,0,0,0.5))`,
        }}
      />
    </AbsoluteFill>
  );
};

type LineWindow = {
  startMs: number;
  endMs: number;
  tokens: { text: string; fromMs: number; toMs: number }[];
};

// Même règle que la composition de production TikTokCaptions : une seule ligne
// à l'écran, jamais de retour à la ligne, regroupement phrase par phrase.
const buildLineWindows = (captions: Caption[]): LineWindow[] => {
  const lines: LineWindow[] = [];
  for (const phrase of captions) {
    const words = approximateWordCaptions([phrase]);
    for (const line of groupWordsIntoLines(words, MAX_CHARS_PER_LINE)) {
      lines.push({
        startMs: line[0].startMs,
        endMs: line[line.length - 1].endMs,
        tokens: line.map((w) => ({ text: w.text, fromMs: w.startMs, toMs: w.endMs })),
      });
    }
  }
  return lines;
};

const CaptionLayer: React.FC<{ captions: Caption[]; speakerSpans: SpeakerSpan[] }> = ({
  captions,
  speakerSpans,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const timeMs = (frame / fps) * 1000;

  const lines = useMemo(() => buildLineWindows(captions), [captions]);
  const active = lines.find((l) => timeMs >= l.startMs && timeMs < l.endMs);
  if (!active) return null;

  // Le locuteur est déterminé sur le DÉBUT de la ligne : une ligne à cheval sur
  // un changement de voix garde une seule couleur, elle ne clignote pas.
  const span = speakerSpans.find((s) => active.startMs >= s.startMs && active.startMs < s.endMs);
  const highlight = span?.speaker === "narrateur" ? COLOR_NARRATEUR : COLOR_CURIO;

  return (
    <AbsoluteFill
      style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: "32%" }}
    >
      <div
        style={{ fontFamily: "Arial, sans-serif", fontWeight: 700, fontSize: 76, whiteSpace: "nowrap" }}
      >
        {active.tokens.map((token, i) => {
          const isActive = timeMs >= token.fromMs && timeMs < token.toMs;
          return (
            <span
              key={i}
              style={{
                color: isActive ? highlight : "white",
                WebkitTextStroke: "3px black",
                paintOrder: "stroke fill",
                textShadow: "0 2px 6px rgba(0,0,0,0.6)",
                marginRight: 10,
              }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const CurioReel: React.FC<CurioReelProps> = ({
  curioSrc,
  scenes,
  levels,
  bigness,
  presence,
  speakerSpans,
  captions,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0E1013" }}>
      {scenes.map((scene, i) => (
        <Sequence key={i} from={scene.start} durationInFrames={scene.duration}>
          <SceneLayer scene={scene} />
        </Sequence>
      ))}
      <CurioLayer curioSrc={curioSrc} levels={levels} bigness={bigness} presence={presence} />
      <CaptionLayer captions={captions} speakerSpans={speakerSpans} />
    </AbsoluteFill>
  );
};

const calculateMetadata: CalculateMetadataFunction<CurioReelProps> = ({ props }) => {
  const { captions } = props.srtText
    ? parseSrt({ input: props.srtText })
    : { captions: [] as Caption[] };
  return {
    durationInFrames: Math.max(1, props.totalFrames),
    props: { ...props, captions },
  };
};

export const CurioReelComposition: React.FC = () => {
  return (
    <Composition
      id="CurioReel"
      component={CurioReel}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={900}
      calculateMetadata={calculateMetadata}
      defaultProps={{
        curioSrc: "curio-reel/curio_flat.png",
        scenes: [] as Scene[],
        levels: [] as number[],
        bigness: [] as number[],
        presence: [] as number[],
        speakerSpans: [] as SpeakerSpan[],
        srtText: null,
        captions: [] as Caption[],
        totalFrames: 900,
      }}
    />
  );
};
