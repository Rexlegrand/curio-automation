import React from "react";
import { AbsoluteFill, Easing, interpolate } from "remotion";

// Éléments communs aux sept beats du reel « le Sahara nourrit l'Amazonie ».
// Tout ce qui se répète d'un beat à l'autre vit ici : hors de ce fichier, deux
// beats finiraient par ne plus écrire leurs sous-titres à la même hauteur.

export const FPS = 30;
export const W = 1080;
export const H = 1920;

// Registre documentaire : une seule sans-serif pour le texte courant, une seule
// serif pour le mot qui porte le sens. Le contraste de fonte fait la
// hiérarchie, pas la couleur.
export const SANS = "Helvetica, Arial, sans-serif";
export const SERIF = 'Georgia, "Times New Roman", serif';
export const OLIVE = "#B8BC94";
export const CREAM = "#EDEAE2";

/** Sous-titre, toujours à la même hauteur d'un beat à l'autre. La boîte sombre
 *  le décolle des fonds clairs — une dune de sable ne pardonne pas du blanc
 *  posé nu.
 *
 *  `mid` le place à mi-hauteur, la position qu'il occupe chez @RyanMusselman
 *  dans les DEUX états : à 250 px du bas il tomberait dans la carte, qui
 *  commence à 1170. C'est lui le point fixe de la bascule, il ne peut pas
 *  dépendre de l'état du plan. */
export const Subtitle: React.FC<{
  text: string;
  from: number;
  frame: number;
  mid?: boolean;
}> = ({ text, from, frame, mid = false }) => {
  const enter = interpolate(frame, [from, from + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  if (enter <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        ...(mid ? { top: 900 } : { bottom: 250 }),
        display: "flex",
        justifyContent: "center",
        padding: "0 60px",
        opacity: enter,
        transform: `translateY(${(1 - enter) * 14}px)`,
      }}
    >
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 46,
          lineHeight: 1.32,
          letterSpacing: 0.4,
          color: "#FFFFFF",
          backgroundColor: "rgba(14,14,16,0.74)",
          borderRadius: 10,
          padding: "14px 26px",
          textAlign: "center",
          maxWidth: 940,
        }}
      >
        {text}
      </div>
    </div>
  );
};

/** Titre à deux registres, réservé aux beats où un mot porte tout : la ligne
 *  courante en sans-serif, le mot en serif deux fois plus gros. */
export const Title: React.FC<{
  line: string;
  keyword: string;
  from: number;
  frame: number;
  top?: number;
}> = ({ line, keyword, from, frame, top = 210 }) => {
  const enter = interpolate(frame, [from, from + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const keyIn = interpolate(frame, [from + 10, from + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  if (enter <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "0 70px",
      }}
    >
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 50,
          color: CREAM,
          textAlign: "center",
          lineHeight: 1.2,
          textShadow: "0 3px 18px rgba(0,0,0,0.95)",
          opacity: enter,
          transform: `translateY(${(1 - enter) * -12}px)`,
        }}
      >
        {line}
      </div>
      <div
        style={{
          fontFamily: SERIF,
          fontSize: 112,
          color: OLIVE,
          textAlign: "center",
          lineHeight: 1.06,
          marginTop: 4,
          textShadow: "0 4px 24px rgba(0,0,0,0.98)",
          opacity: keyIn,
          transform: `scale(${0.94 + 0.06 * keyIn})`,
        }}
      >
        {keyword}
      </div>
    </div>
  );
};

/** Grain de pellicule. Le motif est régénéré tous les deux frames : à chaque
 *  frame il scintille, au-delà de trois il se fige et redevient une texture. */
export const Grain: React.FC<{ frame: number; opacity?: number }> = ({
  frame,
  opacity = 0.09,
}) => {
  const seed = Math.floor(frame / 2);
  return (
    <AbsoluteFill style={{ opacity, mixBlendMode: "overlay", pointerEvents: "none" }}>
      <svg width={W} height={H}>
        <filter id={`grain-${seed}`}>
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.85"
            numOctaves={2}
            seed={seed}
          />
        </filter>
        <rect width={W} height={H} filter={`url(#grain-${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

/** Vignettage. Sur une photo plein cadre il tient le regard au centre ; sans
 *  lui, un 9:16 lu sur téléphone part par les bords. */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(78% 58% at 50% 46%, rgba(0,0,0,0) 40%," +
        `rgba(0,0,0,${strength * 0.5}) 78%, rgba(0,0,0,${strength}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

/** Cadrage d'une photo dans le canvas, avec dérive lente. Les trois plans
 *  plein cadre font 941×1672 : ils sont déjà agrandis 1,15× pour remplir le
 *  cadre, d'où des mouvements amples et lents plutôt qu'un zoom serré. */
export const drift = (
  frame: number,
  duration: number,
  from: number,
  to: number,
): number =>
  interpolate(frame, [0, duration], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
