import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile } from "remotion";

// Sous-titres du reel, au style TikTok déjà utilisé en production
// (remotion/src/tiktok-captions/TikTokCaptions.tsx) : une seule ligne à la
// fois, blanche à contour noir, et le mot en cours de prononciation en bleu.
// Mêmes valeurs exactement — Arial 76 gras, bleu #3ec1ff, contour 3 px,
// baseline à 32 % du bas — pour que ce reel ne parle pas une autre langue
// visuelle que les autres.
//
// Une différence, et elle est en mieux : la production approxime le timing mot
// à mot en répartissant la durée d'un bloc SRT proportionnellement à la
// longueur des mots (subtitle_generator.py lit les vrais timestamps Whisper
// puis les jette). Ici ce sont les VRAIS timestamps, mot par mot, exportés par
// export_mots_sahara.py. Sur une narration qui marque de vraies pauses,
// l'approximation décalait le surlignage d'un demi-mot.
//
// L'orthographe est corrigée à l'export : Whisper donne les temps, pas les
// noms propres — il écrivait « beau délai » pour Bodélé.

const MAX_CHARS = 28; // MAX_LINE_CHARS du pipeline
const ACTIF = "#3ec1ff";

export type Mot = { mot: string; start: number; end: number };
type Ligne = { mots: Mot[]; start: number; end: number };

/** Découpe en lignes courtes, jamais deux à l'écran, jamais de retour à la
 *  ligne. Une ponctuation forte ferme la ligne. */
const decouper = (mots: Mot[]): Ligne[] => {
  const out: Ligne[] = [];
  let courant: Mot[] = [];
  const pousser = () => {
    if (!courant.length) return;
    out.push({
      mots: courant,
      start: courant[0].start,
      end: courant[courant.length - 1].end,
    });
    courant = [];
  };
  for (const m of mots) {
    const longueur = courant.map((x) => x.mot).join(" ").length + m.mot.length + 1;
    if (longueur > MAX_CHARS) pousser();
    courant.push(m);
    if (/[.!?]$/.test(m.mot)) pousser();
  }
  pousser();
  return out;
};

/** Chemin du fichier de mots sous `public/`.
 *
 *  Le sahara nomme ses segments depuis SON dossier — « mots/03-route » pour le
 *  premier montage, « mots2/04-voyage » pour le second — et ces noms-là sont
 *  complétés par le préfixe historique. Les reels de série passent au
 *  contraire un chemin complet (« reels/mariannes/mots/03-descente ») : leurs
 *  mots ne vivent pas sous public/sahara/, et les préfixer les envoyait
 *  chercher un fichier qui n'existe pas. */
const cheminMots = (segment: string): string =>
  segment.startsWith("mots") ? `sahara/${segment}.json` : `${segment}.json`;

export const useMots = (segment: string): Mot[] | null => {
  const [mots, setMots] = useState<Mot[] | null>(null);
  useEffect(() => {
    // delayRender : sans lui, Remotion capture avant que le JSON soit lu et les
    // premières images sortent sans sous-titre.
    const handle = delayRender(`mots-${segment}`);
    const chemin = cheminMots(segment);
    fetch(staticFile(chemin))
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => {
        setMots(d);
        continueRender(handle);
      })
      .catch((e) => {
        // Un fichier manquant ne doit PAS passer inaperçu : le rendu sortait
        // simplement sans sous-titres, sans la moindre erreur, et le défaut ne
        // se voyait qu'à l'œil sur la vidéo finale.
        // eslint-disable-next-line no-console
        console.error(`[captions] mots illisibles : ${chemin} — ${e}`);
        continueRender(handle);
      });
  }, [segment]);
  return mots;
};

export const Captions: React.FC<{
  mots: Mot[] | null;
  frame: number;
  fps: number;
  /** Décalage si le segment ne commence pas à la première image du beat. */
  offset?: number;
}> = ({ mots, frame, fps, offset = 0 }) => {
  if (!mots || !mots.length) return null;
  const t = (frame - offset) / fps;
  const lignes = decouper(mots);
  // Une ligne tient jusqu'à la suivante : sans ça, les silences de respiration
  // laisseraient le bas du cadre vide entre deux phrases.
  const index = lignes.findIndex(
    (l, i) => t >= l.start - 0.15 && (i === lignes.length - 1 || t < lignes[i + 1].start - 0.15),
  );
  if (index < 0) return null;
  const ligne = lignes[index];
  if (t > ligne.end + 0.6) return null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: "32%",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: "Arial, sans-serif",
          fontWeight: 700,
          fontSize: 76,
          whiteSpace: "nowrap",
        }}
      >
        {ligne.mots.map((m, i) => {
          const actif = t >= m.start && t < m.end;
          return (
            <span
              key={i}
              style={{
                color: actif ? ACTIF : "white",
                WebkitTextStroke: "3px black",
                paintOrder: "stroke fill",
                textShadow: "0 2px 6px rgba(0,0,0,0.6)",
                marginRight: 10,
              }}
            >
              {m.mot}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
