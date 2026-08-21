import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { CahierBackground, FPS, H, W } from "../curio-motion/shared";
import { MarkerStroke } from "./MarkerStroke";
import { cutoutDocSchema, CutoutDocProps } from "./schema";

const DURATION_SECONDS = 6;

// Placeholder — à remplacer par le vrai PNG détouré (manchot, œuf, monument...).
// Silhouette opaque sur fond transparent : MarkerStroke calque son alpha, pas
// une simple boîte rectangulaire.
const PlaceholderCutout: React.FC = () => (
  <svg width={360} height={360} viewBox="0 0 360 360">
    <ellipse cx={180} cy={200} rx={120} ry={150} fill="#2b2b2b" />
    <circle cx={180} cy={80} r={70} fill="#2b2b2b" />
    <text
      x={180}
      y={205}
      textAnchor="middle"
      fill="white"
      fontSize={20}
      fontFamily="Arial, sans-serif"
    >
      CUTOUT
    </text>
  </svg>
);

const CutoutDoc: React.FC<CutoutDocProps> = ({
  cutoutX,
  cutoutY,
  cutoutScale,
  cutoutRotationDeg,
  cutoutEntranceFrame,
  cutoutEntranceDurationInFrames,
  markerColor,
  markerStrokeWidth,
  markerOffsetX,
  markerOffsetY,
  markerBlur,
}) => {
  const frame = useCurrentFrame();

  const entranceProgress = interpolate(
    frame,
    [
      cutoutEntranceFrame,
      cutoutEntranceFrame + cutoutEntranceDurationInFrames,
    ],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.back(1.6)),
    },
  );

  return (
    <AbsoluteFill>
      {/* Fond cahier partagé — verrouillé, statique, jamais animé ni piloté par slider. */}
      <CahierBackground />

      <div
        style={{
          position: "absolute",
          left: cutoutX,
          top: cutoutY,
          transform: `translate(-50%, -50%) rotate(${cutoutRotationDeg}deg) scale(${
            cutoutScale * entranceProgress
          })`,
          opacity: entranceProgress,
        }}
      >
        <MarkerStroke
          color={markerColor}
          strokeWidth={markerStrokeWidth}
          offsetX={markerOffsetX}
          offsetY={markerOffsetY}
          blur={markerBlur}
        >
          <PlaceholderCutout />
        </MarkerStroke>
      </div>
    </AbsoluteFill>
  );
};

export const CutoutDocComposition: React.FC = () => {
  return (
    <Composition
      id="CutoutDoc"
      component={CutoutDoc}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DURATION_SECONDS * FPS}
      schema={cutoutDocSchema}
      defaultProps={{
        cutoutX: W / 2,
        cutoutY: H * 0.55,
        cutoutScale: 1,
        cutoutRotationDeg: 0,
        cutoutEntranceFrame: 10,
        cutoutEntranceDurationInFrames: 20,

        markerColor: "#e0483e",
        markerStrokeWidth: 10,
        markerOffsetX: 6,
        markerOffsetY: 6,
        markerBlur: 0,
      }}
    />
  );
};
