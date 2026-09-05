import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Composition,
  Sequence,
  staticFile,
} from "remotion";
import { Caption, parseSrt } from "@remotion/captions";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import type { ExtendedFeatureCollection } from "d3-geo";
import { DesertSelMirrorScenes } from "./DesertSelMirrorScenes";
import { MapZoomUyuni } from "./MapZoomUyuni";
import { TikTokCaptions } from "../tiktok-captions/TikTokCaptions";

// Phase 6 — assemblage final du reel "désert de sel miroir géant" : les 2
// scènes motion design (phase 5) + voix ElevenLabs Curio 8 (audio_v1, 32.48s)
// + sous-titres Whisper (subtitles.srt) rendus par TikTokCaptions (même
// composant que le reste du pipeline, §3/v2.18 CLAUDE.md — une ligne à la
// fois, mot actif surligné).

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;

const MIRROR_SCENES_FRAMES = 600; // 20s — DesertSelMirrorScenes
const MAP_CTA_FRAMES = 380; // 12.67s — MapZoomUyuni (+ CTA overlay intégré)
const TOTAL_FRAMES = MIRROR_SCENES_FRAMES + MAP_CTA_FRAMES; // 980 frames = 32.67s ~ audio 32.48s + AUDIO_TAIL 0.2s

const MAP_DATA_FILE = "countries-50m.json";

type Props = {
  captions: Caption[];
  countries: ExtendedFeatureCollection;
};

export const DesertSelFinal: React.FC<Props> = ({ captions, countries }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence from={0} durationInFrames={MIRROR_SCENES_FRAMES}>
        <DesertSelMirrorScenes />
      </Sequence>
      <Sequence from={MIRROR_SCENES_FRAMES} durationInFrames={MAP_CTA_FRAMES}>
        <MapZoomUyuni countries={countries} target={null} />
      </Sequence>

      <TikTokCaptions captions={captions} totalSeconds={null} srtText={null} />

      <Audio src={staticFile("desert-sel/audio_v1.mp3")} />
    </AbsoluteFill>
  );
};

const calculateMetadata: CalculateMetadataFunction<Props> = async () => {
  const [srtText, topoResponse] = await Promise.all([
    fetch(staticFile("desert-sel/subtitles.srt")).then((r) => r.text()),
    fetch(staticFile(MAP_DATA_FILE)).then((r) => r.json() as Promise<Topology>),
  ]);
  const { captions } = parseSrt({ input: srtText });
  const countries = feature(
    topoResponse,
    topoResponse.objects.countries as GeometryCollection
  ) as unknown as ExtendedFeatureCollection;

  return {
    durationInFrames: TOTAL_FRAMES,
    props: { captions, countries },
  };
};

export const DesertSelFinalComposition: React.FC = () => {
  return (
    <Composition
      id="DesertSelFinal"
      component={DesertSelFinal}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      durationInFrames={TOTAL_FRAMES}
      defaultProps={{ captions: [], countries: { type: "FeatureCollection", features: [] } } as Props}
      calculateMetadata={calculateMetadata}
    />
  );
};
