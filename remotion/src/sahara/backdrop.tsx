import React from "react";
import { AbsoluteFill } from "remotion";
import { W, H } from "./shared";

// Le fond de l'état « carte ». Chez @RyanMusselman : une grille sombre, et des
// carrés d'accent qui s'allument et s'éteignent en fondu, lentement et sans
// fin. Ce fond n'est jamais figé — c'est ce qui empêche l'état carte de
// ressembler à une image posée sur un aplat.
//
// Il est toujours monté, jamais mis en fondu : il doit être derrière AVANT que
// le plan se rétracte (cf. stage.tsx).

const CELL = 62;
const GAP = 6;
const COLS = Math.ceil(W / CELL) + 1;
const ROWS = Math.ceil(H / CELL) + 1;

// Bruit déterministe : un Math.random() par image ferait grouiller la grille
// entière d'une frame à l'autre. Hash entier et non sin(i) : sur des indices
// consécutifs, un sinus repasse par les mêmes valeurs et les carrés allumés
// s'alignaient en bandes horizontales au lieu de se disperser.
const noise = (i: number, seed: number) => {
  let x = (i * 374761393 + seed * 668265263) | 0;
  x = (x ^ (x >>> 13)) * 1274126177;
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
};

export const Backdrop: React.FC<{ frame: number; accent?: string }> = ({
  frame,
  accent = "#C9A227",
}) => {
  const cells = [];
  for (let i = 0; i < COLS * ROWS; i++) {
    const col = i % COLS;
    const row = Math.floor(i / COLS);
    // Un carré sur sept environ s'allume, chacun avec sa propre période et son
    // propre décalage : aucun rythme commun ne doit se lire.
    if (noise(i, 1) > 0.11) continue;
    const periode = 150 + noise(i, 2) * 190;
    const phase = noise(i, 3) * periode;
    const cycle = ((frame + phase) % periode) / periode;
    const alpha = Math.sin(cycle * Math.PI) ** 2;
    cells.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: col * CELL,
          top: row * CELL,
          width: CELL - GAP,
          height: CELL - GAP,
          borderRadius: 6,
          backgroundColor: accent,
          opacity: alpha * 0.34,
        }}
      />,
    );
  }
  return (
    <AbsoluteFill style={{ backgroundColor: "#14161A", overflow: "hidden" }}>
      {/* La grille elle-même, à peine visible : elle donne la matière, les
          carrés d'accent donnent le mouvement. */}
      <AbsoluteFill
        style={{
          backgroundImage:
            `linear-gradient(to right, rgba(255,255,255,0.028) 1px, transparent 1px),` +
            `linear-gradient(to bottom, rgba(255,255,255,0.028) 1px, transparent 1px)`,
          backgroundSize: `${CELL}px ${CELL}px`,
        }}
      />
      {cells}
      {/* Assombrissement des bords : le regard doit rester au centre, là où
          vivent le sous-titre et la carte. */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(86% 62% at 50% 46%, rgba(0,0,0,0) 30%," +
            "rgba(0,0,0,0.42) 78%, rgba(0,0,0,0.66) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
