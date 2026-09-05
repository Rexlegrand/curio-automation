import React from "react";
import {
  AbsoluteFill,
  Easing,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
} from "remotion";
import { W, H } from "./shared";

// Le cadre du reel : un plan qui passe du plein écran au format « deux carrés »,
// où Curio parle dans la carte du haut pendant que le plan tient celle du bas.
//
// C'est LA raison d'être du format : faire revenir Curio à l'écran de temps en
// temps pendant le reel, comme sur le reel manchot. Une première version
// mettait une simple vignette de preuve en bas sans rien au-dessus — contresens,
// la carte n'est pas là pour rétrécir une image mais pour faire de la place au
// personnage.
//
// Le mouvement lui-même vient de @RyanMusselman (short tr5KG38n1A8), relevé
// image par image :
//
//   1. le plan ne se coupe ni ne se fond — il RÉTRÉCIT. Position, taille et
//      coins sont interpolés ensemble, en un seul mouvement ;
//   2. le mouvement dure 10 à 12 images, pas plus. Au-delà il traîne ;
//   3. il décélère fort — les cinq premières images font 70 % du chemin ;
//   4. le fond est DÉJÀ derrière avant que le mouvement commence. Rien ne
//      s'allume : quelque chose se dégage.
//
// Géométrie reprise de CurioDeuxCarres, validée sur le reel manchot : deux
// cartes de 940×855, marges de 70 et 80, symétriques.

export const CARD_W = 940;
export const CARD_H = 855;
export const CARD_R = 36;
export const CARD_X = (W - CARD_W) / 2; // 70
export const CARD_TOP_Y = 80;
export const CARD_BOT_Y = 985;

export const CARD = { x: CARD_X, y: CARD_BOT_Y, width: CARD_W, height: CARD_H, radius: CARD_R };
export const FULL = { x: 0, y: 0, width: W, height: H, radius: 0 };

/** 11 images : la valeur mesurée chez lui, à 30 images par seconde. */
export const TRANSITION = 11;

export type Rect = { x: number; y: number; width: number; height: number; radius: number };

export const rectAt = (t: number): Rect => {
  const mix = (a: number, b: number) => a + (b - a) * t;
  return {
    x: mix(FULL.x, CARD.x),
    y: mix(FULL.y, CARD.y),
    width: mix(FULL.width, CARD.width),
    height: mix(FULL.height, CARD.height),
    radius: mix(FULL.radius, CARD.radius),
  };
};

/** Avancement de la bascule, avec la décélération relevée sur le short. */
export const stageProgress = (
  frame: number,
  from: number,
  to: 0 | 1,
  duration = TRANSITION,
): number =>
  interpolate(frame, [from, from + duration], [to === 1 ? 0 : 1, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

/** Fenêtre pendant laquelle Curio est à l'écran, bascules comprises. */
export type CurioWindow = { src: string; from: number; to: number };

/** Avancement du format deux carrés sur une fenêtre : montée, tenue, descente. */
export const duoProgress = (frame: number, w: CurioWindow | undefined): number => {
  if (!w) return 0;
  if (frame < w.to - TRANSITION) return stageProgress(frame, w.from, 1);
  return stageProgress(frame, w.to - TRANSITION, 0);
};

/** Carte du haut : Curio, qui parle sans qu'on l'entende — la piste audio des
 *  clips n'est jamais montée, une seule voix porte le reel (règle v2.15).
 *
 *  Le clip est enveloppé dans une Sequence pour que sa lecture reparte de zéro
 *  à l'ouverture de la fenêtre : OffthreadVideo lit sur l'horloge absolue de la
 *  composition, sans quoi Curio apparaîtrait au milieu de son geste. Les clips
 *  font 4 s, les fenêtres ne dépassent pas cette durée. */
const CurioCard: React.FC<{ src: string; t: number; from: number }> = ({ src, t, from }) => {
  if (t <= 0.01) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: CARD_X,
        top: CARD_TOP_Y - (1 - t) * 90,
        width: CARD_W,
        height: CARD_H,
        borderRadius: CARD_R,
        overflow: "hidden",
        opacity: t,
        boxShadow: `0 0 0 2px rgba(255,255,255,0.22), 0 26px 54px rgba(0,0,0,0.5)`,
      }}
    >
      <Sequence from={from} layout="none">
        <OffthreadVideo
          src={staticFile(src)}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </Sequence>
    </div>
  );
};

export const Stage: React.FC<{
  /** 0 = plein écran, 1 = carte basse du format deux carrés. */
  t: number;
  /** Le fond, toujours monté, jamais mis en fondu : il doit être derrière
   *  AVANT que le plan se rétracte. */
  background: React.ReactNode;
  children: React.ReactNode;
  /** Sous-titres et titres : hors du cadre mobile, ils ne bougent jamais. */
  overlay?: React.ReactNode;
  /** Curio dans la carte du haut, quand le beat lui fait une place. */
  curio?: CurioWindow;
}> = ({ t, background, children, overlay, curio }) => {
  const r = rectAt(t);
  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0D10" }}>
      <AbsoluteFill>{background}</AbsoluteFill>
      {curio ? <CurioCard src={curio.src} t={t} from={curio.from} /> : null}
      <div
        style={{
          position: "absolute",
          left: r.x,
          top: r.y,
          width: r.width,
          height: r.height,
          borderRadius: r.radius,
          overflow: "hidden",
          // La bordure n'existe que sur la carte : à plein écran elle ferait un
          // liseré parasite sur le bord de l'image.
          boxShadow:
            t > 0.02
              ? `0 0 0 ${2 * t}px rgba(255,255,255,${0.22 * t}), 0 ${26 * t}px ${54 * t}px rgba(0,0,0,${0.5 * t})`
              : "none",
        }}
      >
        {children}
      </div>
      {overlay}
    </AbsoluteFill>
  );
};
