import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Captions, useMots } from "../../sahara/captions";
import { Grain, Vignette, SANS, SERIF, CREAM, OLIVE, FPS, W, H } from "../../sahara/shared";

// Beat 3 — la descente. Le « mécanisme » du reel, l'équivalent du voyage de la
// poussière au-dessus de l'Atlantique dans le sahara.
// « Tu descends. À deux cents mètres... les couleurs disparaissent. À mille...
//   il fait nuit noire. Et tu n'es qu'au dixième du chemin. »
//
// Un seul geste, comme le beat 6 du sahara, mais une TRANSLATION et non un
// zoom : le sujet est qu'on s'enfonce, et un zoom donnerait qu'on s'approche.
// Les trois plans sont empilés dans une colonne de trois hauteurs d'écran que
// la caméra remonte d'un mouvement continu — c'est le seul moyen d'avoir un
// raccord invisible entre eux, un fondu trahirait trois images séparées.
//
// Le compteur de profondeur ne file pas à vitesse constante : il est calé sur
// les mots, 200 m quand la voix dit « deux cents mètres », 1 000 m quand elle
// dit « mille ». Un compteur qui avance tout seul dans son coin serait un
// élément décoratif ; calé, il devient la preuve de ce qu'on entend.
//
// La graduation du fond (11 000 m) reste visible et hors d'atteinte pendant
// toute la descente. C'est elle qui porte la chute du beat — « tu n'es qu'au
// dixième du chemin » — sans qu'aucun texte n'ait à le dire.

export type DescenteProps = {
  duration: number;
  segment: string;
  /** Les trois plans, du plus clair au plus noir. */
  layers: string[];
  /** (image, profondeur en mètres) — le compteur passe par ces points. */
  paliers: [number, number][];
  /** Image où la graduation du fond apparaît. */
  fondFrom: number;
  /** Profondeur totale, celle qu'on n'atteint pas. */
  fondMetres: number;
};

const Palier: React.FC<{ frame: number; from: number; texte: string; sous: string }> = ({
  frame,
  from,
  texte,
  sous,
}) => {
  // Le palier entre vite et repart : il marque un passage, il ne s'installe
  // pas. Au-delà d'une seconde à l'écran il concurrence le sous-titre.
  const enter = interpolate(frame, [from, from + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const exit = interpolate(frame, [from + 46, from + 62], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const o = enter * exit;
  if (o <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 640,
        textAlign: "center",
        opacity: o,
        transform: `translateY(${(1 - enter) * 26}px)`,
      }}
    >
      <div style={{ fontFamily: SERIF, fontSize: 104, color: CREAM, textShadow: "0 4px 24px rgba(0,0,0,0.9)" }}>
        {texte}
      </div>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 38,
          letterSpacing: 5,
          color: OLIVE,
          marginTop: 2,
          textShadow: "0 3px 16px rgba(0,0,0,0.95)",
        }}
      >
        {sous}
      </div>
    </div>
  );
};

export const Descente: React.FC<DescenteProps> = ({
  duration,
  segment,
  layers,
  paliers,
  fondFrom,
  fondMetres,
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);

  // La colonne fait trois hauteurs d'écran et remonte de deux : la caméra
  // traverse les trois plans exactement une fois, sans temps mort au départ ni
  // à l'arrivée.
  const travel = interpolate(frame, [0, duration], [0, -(layers.length - 1) * H], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  // Compteur calé sur les mots : les images et les profondeurs des paliers
  // sont les points de passage, le reste est interpolé entre eux.
  const profondeur = interpolate(
    frame,
    [0, ...paliers.map(([f]) => f), duration],
    [0, ...paliers.map(([, m]) => m), paliers[paliers.length - 1][1] * 1.1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const fondIn = interpolate(frame, [fondFrom, fondFrom + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#03070C" }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: W,
            height: H * layers.length,
            transform: `translateY(${travel}px)`,
          }}
        >
          {layers.map((src, i) => (
            <Img
              key={i}
              src={staticFile(src)}
              style={{
                position: "absolute",
                left: 0,
                top: i * H,
                width: W,
                height: H,
                objectFit: "cover",
              }}
            />
          ))}
        </div>
      </AbsoluteFill>

      {/* Assombrissement progressif : la lumière meurt avec la descente, sur
          le plan comme dans le texte. */}
      <AbsoluteFill
        style={{
          backgroundColor: "#000",
          opacity: interpolate(frame, [0, duration], [0, 0.42], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />

      <Vignette strength={0.68} />
      <Grain frame={frame} opacity={0.09} />

      {/* Le compteur, colonne de droite. Chiffres tabulaires : sans eux la
          largeur du nombre change à chaque centaine et le bloc tressaute. */}
      <div
        style={{
          position: "absolute",
          right: 54,
          top: 210,
          textAlign: "right",
          fontFamily: SANS,
          fontWeight: 700,
          color: CREAM,
          textShadow: "0 3px 18px rgba(0,0,0,0.95)",
        }}
      >
        <div style={{ fontSize: 96, letterSpacing: 1, fontVariantNumeric: "tabular-nums" }}>
          -{(Math.round(profondeur / 10) * 10).toLocaleString("fr-FR").replace(/ | /g, " ")}
        </div>
        <div style={{ fontSize: 34, letterSpacing: 8, color: OLIVE, marginTop: -6 }}>MÈTRES</div>
      </div>

      {/* La graduation du fond : atteinte par aucun plan du beat. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 430,
          opacity: fondIn,
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "0 54px",
        }}
      >
        <div style={{ flex: 1, height: 2, background: "rgba(245,199,122,0.5)" }} />
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 40,
            letterSpacing: 3,
            color: "#F5C77A",
            whiteSpace: "nowrap",
          }}
        >
          FOND : -{fondMetres.toLocaleString("fr-FR").replace(/ | /g, " ")} M
        </div>
        <div style={{ flex: 1, height: 2, background: "rgba(245,199,122,0.5)" }} />
      </div>

      {paliers.map(([f, m], i) => (
        <Palier
          key={i}
          frame={frame}
          from={f}
          texte={`-${m.toLocaleString("fr-FR").replace(/ | /g, " ")} m`}
          sous={i === 0 ? "PLUS DE COULEURS" : "NUIT NOIRE"}
        />
      ))}

      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};
