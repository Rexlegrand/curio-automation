import { z } from "zod";
import { zColor } from "@remotion/zod-types";

export const cutoutDocSchema = z.object({
  cutoutX: z.number(),
  cutoutY: z.number(),
  cutoutScale: z.number().min(0.1).max(3),
  cutoutRotationDeg: z.number().min(-45).max(45),
  cutoutEntranceFrame: z.number().min(0),
  cutoutEntranceDurationInFrames: z.number().min(1).max(120),

  markerColor: zColor(),
  markerStrokeWidth: z.number().min(0).max(40),
  markerOffsetX: z.number().min(-40).max(40),
  markerOffsetY: z.number().min(-40).max(40),
  markerBlur: z.number().min(0).max(20),
});

export type CutoutDocProps = z.infer<typeof cutoutDocSchema>;
