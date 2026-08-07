import React, { useMemo } from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Caption, parseSrt } from "@remotion/captions";
import { approximateWordCaptions, groupWordsIntoLines } from "./words";

const FPS = 30;

// Aligné sur MAX_LINE_CHARS dans generators/subtitle_generator.py — même largeur
// de ligne que le montage FFmpeg actuel, pour un rendu visuel comparable.
const MAX_CHARS_PER_LINE = 28;

// srtText / totalSeconds : fournis par generators/video_assembler.py via
// --props=<fichier.json> (un fichier temporaire par reel, jamais de JSON inline
// en ligne de commande à cause des apostrophes françaises). totalSeconds est la
// durée EXACTE du montage (audio + AUDIO_TAIL, config.py) — les sous-titres
// doivent durer aussi longtemps que la vidéo, jamais calés sur le seul dernier
// timestamp du SRT. captions est calculé par calculateMetadata, jamais fourni
// en entrée. En dev (Studio, npm run dev, aucune prop) : fallback sur l'exemple
// public/sample-captions.srt pour prévisualiser sans dépendre du pipeline Python.
type Props = {
  srtText: string | null;
  totalSeconds: number | null;
  captions: Caption[];
};

type LineWindow = {
  text: string;
  startMs: number;
  endMs: number;
  tokens: { text: string; fromMs: number; toMs: number }[];
};

// Règle CLAUDE.md non négociable : une seule phrase/ligne à l'écran à la fois,
// jamais de retour à la ligne. Chaque ligne groupée devient une fenêtre
// d'affichage séquentielle — une seule à l'écran, jamais deux empilées.
// Le regroupement en lignes de ≤28 caractères se fait PHRASE PAR PHRASE (jamais
// à cheval sur deux blocs du SRT) : chaque bloc subtitles.srt est déjà une unité
// de sens (une phrase ou un morceau de phrase, subtitle_generator.py) — fusionner
// la fin d'une phrase avec le début de la suivante romprait cette logique.
const buildLineWindows = (phraseCaptions: Caption[]): LineWindow[] => {
  const lines: LineWindow[] = [];

  for (const phrase of phraseCaptions) {
    const words = approximateWordCaptions([phrase]);
    const phraseLines = groupWordsIntoLines(words, MAX_CHARS_PER_LINE);

    for (const line of phraseLines) {
      lines.push({
        text: line.map((w) => w.text).join(" "),
        startMs: line[0].startMs,
        endMs: line[line.length - 1].endMs,
        tokens: line.map((w) => ({
          text: w.text,
          fromMs: w.startMs,
          toMs: w.endMs,
        })),
      });
    }
  }

  return lines;
};

export const TikTokCaptions: React.FC<Props> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const timeMs = (frame / fps) * 1000;

  const lines = useMemo(() => buildLineWindows(captions), [captions]);
  const active = lines.find((l) => timeMs >= l.startMs && timeMs < l.endMs);

  if (!active) {
    return null;
  }

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: "21%" }}>
      <div
        style={{
          fontFamily: "Arial, sans-serif",
          fontWeight: 700,
          fontSize: 60,
          whiteSpace: "nowrap",
        }}
      >
        {active.tokens.map((token, i) => {
          const isActive = timeMs >= token.fromMs && timeMs < token.toMs;
          return (
            <span
              key={i}
              style={{
                color: isActive ? "#3ec1ff" : "white",
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

const calculateMetadata: CalculateMetadataFunction<Props> = async ({ props }) => {
  const text = props.srtText ?? (await (await fetch(staticFile("sample-captions.srt"))).text());
  const { captions } = parseSrt({ input: text });
  const lastEndMs = captions.length ? captions[captions.length - 1].endMs : 0;
  const durationSeconds = props.totalSeconds ?? (lastEndMs + 500) / 1000;

  return {
    durationInFrames: Math.max(1, Math.round(durationSeconds * FPS)),
    props: { ...props, captions },
  };
};

export const TikTokCaptionsComposition: React.FC = () => {
  return (
    <Composition
      id="TikTokCaptions"
      component={TikTokCaptions}
      fps={FPS}
      width={1080}
      height={1920}
      durationInFrames={1}
      defaultProps={{ srtText: null, totalSeconds: null, captions: [] } as Props}
      calculateMetadata={calculateMetadata}
    />
  );
};
