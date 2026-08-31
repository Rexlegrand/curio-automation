// PROTOTYPE 3 — "La caméra qui se déplace" : le cahier est une immense
// surface à carreaux, la caméra se promène de zone en zone puis dézoome
// pour révéler l'ensemble de la fresque.

import React from "react";
import { AbsoluteFill, Composition, interpolate, useCurrentFrame } from "remotion";
import { CahierBackground, PastedPhoto, CurioMascotte, IMAGES, FPS, W, H } from "./shared";

const BIG_W = W * 2.4;
const BIG_H = H * 2.4;

const SPOTS = [
  { x: BIG_W * 0.28, y: BIG_H * 0.24, src: IMAGES.eclipse, w: 520 },
  { x: BIG_W * 0.72, y: BIG_H * 0.4, src: IMAGES.tdf, w: 560 },
  { x: BIG_W * 0.38, y: BIG_H * 0.68, src: IMAGES.stadium, w: 500 },
  { x: BIG_W * 0.74, y: BIG_H * 0.78, src: IMAGES.footballKid, w: 480 },
];

// Timeline caméra : arrêt sur chaque spot, puis dézoom final sur toute la surface.
const HOLD = 45;
const TRAVEL = 25;
const legFrames = (SPOTS.length - 1) * (HOLD + TRAVEL) + HOLD;
const DEZOOM_DURATION = 65;
export const CAMERA_JOURNEY_TOTAL = legFrames + DEZOOM_DURATION + 20;

const FIT_SCALE = Math.min(W / BIG_W, H / BIG_H);

const keyframeAt = (frame: number) => {
  // Renvoie {cx, cy, scale} pour la position caméra à cette frame (avant dézoom).
  const legLen = HOLD + TRAVEL;
  const legIndex = Math.min(Math.floor(frame / legLen), SPOTS.length - 1);
  const from = SPOTS[Math.max(0, Math.min(legIndex, SPOTS.length - 1))];
  const to = SPOTS[Math.min(legIndex + 1, SPOTS.length - 1)];
  const localFrame = frame - legIndex * legLen;
  const t = interpolate(localFrame, [HOLD, HOLD + TRAVEL], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cx = interpolate(t, [0, 1], [from.x, to.x]);
  const cy = interpolate(t, [0, 1], [from.y, to.y]);
  return { cx, cy };
};

const Scene: React.FC = () => {
  const frame = useCurrentFrame();

  const dezoomT = interpolate(frame, [legFrames, legFrames + DEZOOM_DURATION], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const { cx, cy } = keyframeAt(Math.min(frame, legFrames));
  const camScale = interpolate(dezoomT, [0, 1], [1.55, FIT_SCALE]);
  const finalCx = interpolate(dezoomT, [0, 1], [cx, BIG_W / 2]);
  const finalCy = interpolate(dezoomT, [0, 1], [cy, BIG_H / 2]);

  const translateX = W / 2 - finalCx * camScale;
  const translateY = H / 2 - finalCy * camScale;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "rgb(253,253,250)" }}>
      <div
        style={{
          position: "absolute",
          width: BIG_W,
          height: BIG_H,
          transformOrigin: "0 0",
          transform: `translate(${translateX}px, ${translateY}px) scale(${camScale})`,
        }}
      >
        <CahierBackground>
          {SPOTS.map((s, i) => {
            const revealAt = i === 0 ? 0 : i * (HOLD + TRAVEL) - 10;
            const opacity = interpolate(frame, [revealAt, revealAt + 15], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: s.x,
                  top: s.y,
                  transform: "translate(-50%, -50%)",
                  opacity,
                }}
              >
                <PastedPhoto src={s.src} width={s.w} rotateDeg={i % 2 === 0 ? -3 : 2.5} />
              </div>
            );
          })}
          <div
            style={{
              position: "absolute",
              left: BIG_W * 0.55,
              top: BIG_H * 0.2,
              opacity: dezoomT,
            }}
          >
            <CurioMascotte size={260} />
          </div>
        </CahierBackground>
      </div>
    </AbsoluteFill>
  );
};

export const CurioCameraJourneyComposition: React.FC = () => (
  <Composition
    id="Curio-CameraJourney"
    component={Scene}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={CAMERA_JOURNEY_TOTAL}
  />
);
