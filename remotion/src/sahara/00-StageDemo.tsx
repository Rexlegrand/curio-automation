import React from "react";
import { AbsoluteFill, Composition, Img, staticFile, useCurrentFrame } from "remotion";
import { Backdrop } from "./backdrop";
import { Stage, stageProgress } from "./stage";
import { Grain, Subtitle, FPS, W, H } from "./shared";

// Banc d'essai de la bascule plein écran ↔ carte, avant de la propager aux sept
// beats. Trois temps : plein écran, bascule vers la carte, retour. Rien d'autre
// à l'écran, pour que seul le mouvement soit jugé.

const DURATION = 200;
const TO_CARD = 50;
const TO_FULL = 140;

export const StageDemo: React.FC = () => {
  const frame = useCurrentFrame();

  // Deux bascules successives : la seconde annule la première.
  const t =
    frame < TO_FULL
      ? stageProgress(frame, TO_CARD, 1)
      : stageProgress(frame, TO_FULL, 0);

  return (
    <AbsoluteFill>
      <Stage
        t={t}
        background={<Backdrop frame={frame} />}
        overlay={
          <>
            <Grain frame={frame} opacity={0.07} />
            <Subtitle text="LE SABLE DU SAHARA TRAVERSE L'ATLANTIQUE." from={8} frame={frame} mid />
          </>
        }
      >
        <Img
          src={staticFile("sahara/dune.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </Stage>
    </AbsoluteFill>
  );
};

export const StageDemoComposition: React.FC = () => (
  <Composition
    id="sahara-00-stage"
    component={StageDemo}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DURATION}
  />
);
