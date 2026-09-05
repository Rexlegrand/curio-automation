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
import { Captions, useMots } from "./captions";
import { Grain, Vignette, FPS, W, H } from "./shared";
import { DUREES2, V2_ALGUES } from "./timing2";

// Montage 2, beat « les algues ».
// « Son sable n'est pas vraiment du sable. Ce sont des squelettes d'algues
//   microscopiques. »
//
// Plein écran d'un bout à l'autre, et le seul beat du montage sans Curio :
// c'est une affaire d'ÉCHELLE, on passe du grain à ce qui le compose. Une
// carte tuerait exactement ce qu'il y a à voir.
//
// Les deux images se recouvrent au lieu de se succéder — la seconde grandit
// pendant que la première continue de s'ouvrir. C'est ce recouvrement qui fait
// croire à une descente continue plutôt qu'à deux plans collés, et c'est le
// seul endroit des deux montages où l'enchaîné se justifie.

const DURATION = DUREES2.algues;
const OVERLAP = V2_ALGUES.overlap;

export const V2Algues: React.FC = () => {
  const frame = useCurrentFrame();
  const mots = useMots("mots2/03-algues");

  const sable = interpolate(frame, [0, DURATION], [1.0, 2.1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });
  const entree = interpolate(
    frame,
    [V2_ALGUES.diatomeesFrom - OVERLAP, V2_ALGUES.diatomeesFrom],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) },
  );
  const diatomees = interpolate(
    frame,
    [V2_ALGUES.diatomeesFrom - OVERLAP, DURATION],
    [0.72, 1.7],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad) },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#04060A" }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={staticFile("sahara/sable_macro.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${sable})`,
          }}
        />
      </AbsoluteFill>
      {entree > 0 ? (
        <AbsoluteFill style={{ opacity: entree, overflow: "hidden" }}>
          <Img
            src={staticFile("sahara/diatomees.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${diatomees})`,
            }}
          />
        </AbsoluteFill>
      ) : null}
      <Vignette strength={0.6} />
      <Grain frame={frame} opacity={0.1} />
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};

export const V2AluesComposition: React.FC = () => (
  <Composition
    id="sahara2-03-algues"
    component={V2Algues}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DURATION}
  />
);
