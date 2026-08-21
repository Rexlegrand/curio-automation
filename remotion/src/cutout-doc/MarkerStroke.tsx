import React from "react";

// Astuce contour marqueur : empile des drop-shadow(dx dy blur color) autour
// d'un cercle de rayon strokeWidth — chaque drop-shadow calque la silhouette
// alpha du contenu (le cutout détouré), donc le résultat est un contour plein
// qui épouse la forme exacte, pas un rectangle. Un décalage global
// (offsetX/offsetY) pousse ce contour derrière et de travers, comme un trait
// de marqueur tracé à la main derrière le sujet plutôt qu'un liseré parfait.
const ANGLE_STEPS = 12;

export const MarkerStroke: React.FC<{
  color: string;
  strokeWidth: number;
  offsetX: number;
  offsetY: number;
  blur?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ color, strokeWidth, offsetX, offsetY, blur = 0, children, style }) => {
  const shadows: string[] = [];

  if (strokeWidth > 0) {
    for (let i = 0; i < ANGLE_STEPS; i++) {
      const angle = (i / ANGLE_STEPS) * Math.PI * 2;
      const dx = offsetX + Math.cos(angle) * strokeWidth;
      const dy = offsetY + Math.sin(angle) * strokeWidth;
      shadows.push(`drop-shadow(${dx}px ${dy}px ${blur}px ${color})`);
    }
  }

  return (
    <div style={{ filter: shadows.join(" "), ...style }}>{children}</div>
  );
};
