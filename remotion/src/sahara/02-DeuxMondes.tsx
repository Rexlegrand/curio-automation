import React from "react";
import {
  Composition,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Backdrop } from "./backdrop";
import { Captions, useMots } from "./captions";
import { Stage, duoProgress, CurioWindow } from "./stage";
import { Grain, SANS, CREAM, FPS, W, H } from "./shared";
import { DUREES, DEUX_MONDES } from "./timing";

// Beat 2 — les deux mondes.
// « D'un côté, le Sahara. Du sable. Presque rien qui pousse. De l'autre...
//   l'Amazonie. À plus de cinq mille kilomètres. »
//
// Curio revient ici, dans la carte du haut, le temps de la première moitié de
// la phrase — celle qui ne parle que du Sahara. Il rend l'écran juste avant
// « de l'autre » : le diptyque Sahara / Amazonie a besoin de toute la hauteur,
// et les deux formats ne peuvent pas cohabiter.
//
// Les deux fenêtres entrent l'une après l'autre, dans l'ordre de la phrase,
// chacune depuis son propre bord. La distance vit sur la ligne qui les sépare :
// c'est l'endroit exact où les deux mondes ne se touchent pas.

// Comme le beat 1, la mécanique ne change pas d'un reel à l'autre — deux
// fenêtres qui entrent l'une après l'autre depuis leur propre bord, et une
// mesure posée sur la ligne qui les sépare. Seules la matière, les deux noms
// et la mesure changent. Le sahara reste la valeur par défaut.
export type DeuxMondesProps = {
  duration?: number;
  segment?: string;
  topIn?: number;
  bottomIn?: number;
  ruleIn?: number;
  topSrc?: string;
  botSrc?: string;
  topLabel?: string;
  botLabel?: string;
  /** La mesure de l'écart, dans la pastille sur la ligne. */
  badge?: string;
  accent?: string;
  curio?: CurioWindow;
};

const Panel: React.FC<{
  src: string;
  label: string;
  from: number;
  frame: number;
  fromTop: boolean;
  showLabel: boolean;
  duration: number;
}> = ({ src, label, from, frame, fromTop, showLabel, duration }) => {
  const enter = interpolate(frame, [from, from + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const offset = (1 - enter) * (fromTop ? -120 : 120);
  const zoom = interpolate(frame, [from, duration], [1.14, 1.03], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  return (
    <div style={{ position: "relative", flex: 1, overflow: "hidden", opacity: enter }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${zoom}) translateY(${offset}px)`,
        }}
      />
      {showLabel ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            [fromTop ? "top" : "bottom"]: 40,
            textAlign: "center",
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 62,
            letterSpacing: 6,
            color: CREAM,
            textShadow: "0 4px 22px rgba(0,0,0,0.95)",
            opacity: interpolate(frame, [from + 14, from + 32], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {label}
        </div>
      ) : null}
    </div>
  );
};

export const DeuxMondes: React.FC<DeuxMondesProps> = ({
  duration: DURATION = DUREES.deuxMondes,
  segment = "mots/02-deux-mondes",
  topIn: TOP_IN = DEUX_MONDES.topIn,
  bottomIn: BOTTOM_IN = DEUX_MONDES.bottomIn, // sahara : « de l'autre », 5,62 s
  ruleIn: RULE_IN = DEUX_MONDES.ruleIn,
  topSrc = "sahara/dune.jpg",
  botSrc = "sahara/canopee.jpg",
  topLabel = "SAHARA",
  botLabel = "AMAZONIE",
  badge = "5 000 km",
  accent = "#8C6B2F",
  curio = DEUX_MONDES.curio,
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  const t = duoProgress(frame, curio);

  const ruleIn = interpolate(frame, [RULE_IN, RULE_IN + 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // La règle et sa pastille n'existent qu'une fois les deux mondes à l'écran,
  // donc jamais pendant que Curio occupe le haut.
  const ruleShown = ruleIn * (1 - t);

  return (
    <Stage
      t={t}
      curio={curio}
      background={<Backdrop frame={frame} accent={accent} />}
      overlay={
        <>
          {/* La distance est posée SUR la ligne, dans une pastille sombre : en
              texte nu elle tombait sur le ciel clair du Sahara. */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: H / 2 - 34,
              display: "flex",
              justifyContent: "center",
              opacity: interpolate(frame, [RULE_IN + 16, RULE_IN + 34], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }) * (1 - t),
            }}
          >
            <div
              style={{
                fontFamily: SANS,
                fontWeight: 700,
                fontSize: 52,
                letterSpacing: 3,
                color: "#F5C77A",
                backgroundColor: "rgba(12,10,8,0.88)",
                border: "2px solid rgba(245,199,122,0.55)",
                borderRadius: 999,
                padding: "10px 34px",
              }}
            >
              {badge}
            </div>
          </div>
          <Grain frame={frame} opacity={0.07} />
          <Captions mots={mots} frame={frame} fps={FPS} />
        </>
      }
    >
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
        <Panel
          src={topSrc}
          label={topLabel}
          from={TOP_IN}
          frame={frame}
          fromTop
          showLabel={t < 0.4}
          duration={DURATION}
        />
        {frame >= BOTTOM_IN ? (
          <Panel
            src={botSrc}
            label={botLabel}
            from={BOTTOM_IN}
            frame={frame}
            fromTop={false}
            showLabel
            duration={DURATION}
          />
        ) : null}
      </div>
      {/* Le trait de séparation vit dans le cadre, il suit donc la carte. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "50%",
          height: 3,
          background: "#F5C77A",
          transform: `scaleX(${ruleShown})`,
          transformOrigin: "50% 50%",
        }}
      />
    </Stage>
  );
};

export const DeuxMondesComposition: React.FC = () => (
  <Composition
    id="sahara-02-deux-mondes"
    component={DeuxMondes}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.deuxMondes}
  />
);
