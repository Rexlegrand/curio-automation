import React from "react";
import { AbsoluteFill, Composition, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { Captions, useMots } from "./captions";
import { Grain, FPS, W, H } from "./shared";

// Le hook animé et le CTA passent par Remotion, et non plus directement par
// FFmpeg au montage.
//
// La raison est simple : montés bruts, ils échappaient au système de
// sous-titres. Les deux reels avaient donc des sous-titres partout SAUF sur
// leur première et leur dernière phrase — exactement les deux moments qui
// décident qu'on reste ou qu'on passe.
//
// La piste audio du clip n'est jamais montée : une seule voix porte le reel,
// du premier au dernier cadre (règle v2.15 du brief). C'est la narration
// ElevenLabs qu'on entend sur le bec de Curio, et ce sont ses mots qui
// s'affichent.

export type ClipProps = {
  src: string;
  segment: string;
  duration: number;
};

export const ClipSousTitre: React.FC<ClipProps> = ({ src, segment }) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0D10" }}>
      <OffthreadVideo
        src={staticFile(src)}
        muted
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      <Grain frame={frame} opacity={0.06} />
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};

/** Quatre compositions : le hook et le CTA de chacun des deux montages. Les
 *  durées sont celles des segments de voix, pauses comprises — imprimées par
 *  `build_reel_sahara.py --timings` et `test_sahara2.py reel`. */
export const ClipsComposition: React.FC = () => (
  <>
    <Composition
      id="sahara-hook"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={104}
      defaultProps={{
        src: "sahara/hook_video.mp4",
        segment: "mots/00-hook",
        duration: 104,
      }}
    />
    <Composition
      id="sahara-cta"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={123}
      defaultProps={{ src: "sahara/curio_cta.mp4", segment: "mots/08-cta", duration: 123 }}
    />
    <Composition
      id="sahara2-hook"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={101}
      defaultProps={{
        src: "sahara/hook_video.mp4",
        segment: "mots2/00-hook",
        duration: 101,
      }}
    />
    <Composition
      id="sahara2-cta"
      component={ClipSousTitre}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={120}
      defaultProps={{ src: "sahara/curio_cta.mp4", segment: "mots2/07-cta", duration: 120 }}
    />
  </>
);
