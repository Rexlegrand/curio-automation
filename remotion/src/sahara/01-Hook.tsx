import React from "react";
import {
  AbsoluteFill,
  Composition,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Grain, Title, Vignette, drift, FPS, W, H } from "./shared";
import { Captions, useMots } from "./captions";
import { DUREES, HOOK } from "./timing";

// Beat 1 — le hook.
// « Attends... le plus grand désert du monde nourrit la plus grande forêt du
//   monde. »
//
// La phrase tient les deux mondes, l'image doit les tenir aussi : la dune
// occupe la première moitié du beat, puis un raccord sec sur la canopée, sur
// le mot « forêt ». Un fondu enchaîné adoucirait le contraste, or c'est le
// contraste qui est le sujet — et la règle de rythme du projet interdit le
// fondu.
//
// Le mouvement de caméra ne s'interrompt PAS au raccord : il continue dans le
// même sens et à la même vitesse d'un plan à l'autre. C'est ce qui fait lire
// les deux images comme un seul geste plutôt que comme deux photos collées.

// Le beat est le même d'un reel à l'autre — deux plans opposés, un raccord sec
// au milieu d'un mouvement de caméra continu — seule sa matière change. Tout
// ce qui est propre au sahara est ici une valeur par défaut : les
// compositions du sahara n'ont rien à passer, les autres reels surchargent.
export type HookProps = {
  duration?: number;
  segment?: string;
  cut?: number;
  /** Les deux plans, dans l'ordre de la phrase. */
  srcA?: string;
  srcB?: string;
  /** Matière soufflée sur le PREMIER plan seulement, en fondu avant le
   *  raccord : la voir survivre sur le second trahirait le calque. */
  overlaySrc?: string;
  line?: string;
  keyword?: string;
};

export const Hook: React.FC<HookProps> = ({
  duration: DURATION = DUREES.hook,
  segment = "mots/01-hook-suite",
  cut: CUT = HOOK.cut, // sahara : sur le mot « forêt », relevé à 3,76 s
  srcA = "sahara/dune.jpg",
  srcB = "sahara/canopee.jpg",
  overlaySrc = "sahara/poussiere.jpg",
  line = "Le plus grand désert du monde",
  keyword = "nourrit",
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);
  const desert = frame < CUT;

  // Une seule course de zoom sur toute la durée, dont chaque plan prend sa
  // part : le raccord tombe au milieu d'un mouvement, jamais à son départ.
  const zoom = drift(frame, DURATION, 1.06, 1.2);
  const slide = drift(frame, DURATION, -26, 26);

  // La poussière ne souffle que sur le désert, et elle s'éteint avant le
  // raccord — la voir survivre sur la canopée trahirait le calque.
  const dust = interpolate(frame, [10, 40, CUT - 14, CUT], [0, 0.5, 0.5, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0A09" }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={staticFile(desert ? srcA : srcB)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${zoom}) translateX(${slide}px)`,
          }}
        />
      </AbsoluteFill>

      {desert && overlaySrc ? (
        <AbsoluteFill
          style={{ opacity: dust, mixBlendMode: "screen", pointerEvents: "none" }}
        >
          <Img
            src={staticFile(overlaySrc)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(1.5) translateX(${drift(frame, CUT, 60, -60)}px)`,
            }}
          />
        </AbsoluteFill>
      ) : null}

      <Vignette strength={0.62} />
      <Grain frame={frame} />

      <Title line={line} keyword={keyword} from={12} frame={frame} />
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};

export const HookComposition: React.FC = () => (
  <Composition
    id="sahara-01-hook"
    component={Hook}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DUREES.hook}
  />
);
