import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Curio « avatar qui parle » — piste 100% locale, zéro appel externe.
//
// Objectif : remplacer le hook animé Dreamina (plateforme externe, tâche
// humaine, ~10 min perdues par reel) par un Curio découpé animé directement
// dans Remotion. Le personnage s'illumine au rythme de la voix, comme
// l'anneau vert autour d'une photo de profil Discord quand quelqu'un parle.
//
// Deux états, enchaînés par un ressort :
//   HOOK     — Curio en grand au centre, fond flouté et assombri derrière lui.
//   CONTENU  — Curio réduit en pastille ronde en bas à droite, fond net,
//              façon vignette d'appel Discord par-dessus le motion design.
//
// L'intensité de la lumière n'est PAS aléatoire : elle suit le niveau réel de
// la voix, extrait image par image côté Python (RMS de l'audio) et passé en
// prop `levels`. Un rendu est donc déterministe et recalé sur n'importe quel
// audio.

const FPS = 30;
const W = 1080;
const H = 1920;

// État HOOK — Curio centré.
// Le cutout source ne fait que 250×314 px : au-delà de ~860 px de haut il
// commence à baver. Voir la note « résolution » dans test_curio_speaking_avatar.py.
const BIG_HEIGHT = 860;
const BIG_CENTER_Y = 900;

// État CONTENU — pastille ronde en bas à droite. Remontée au-dessus de la
// bande de sous-titres (baseline ~79% de la hauteur, cf. CLAUDE.md §3).
const PILL_SIZE = 260;
const PILL_CENTER_X = W - 60 - PILL_SIZE / 2;
const PILL_CENTER_Y = 1160;

// Fond de la pastille : bleu Curio sombre, pour que le personnage bleu clair
// ressorte sans halo blanc.
const PILL_BG = "#132B52";

export type SpeakingAvatarProps = {
  curioSrc: string;
  bgHookSrc: string;
  bgContentSrc: string;
  /** Niveau de voix par image, 0 → 1. Longueur = nombre d'images du rendu. */
  levels: number[];
  /** Image à laquelle Curio passe du centre à la pastille. */
  handoffFrame: number;
  glowColor: string;
  totalFrames: number;
};

/** Niveau de voix de l'image courante, borné (une prop trop courte ne casse rien). */
const levelAt = (levels: number[], frame: number) =>
  levels.length === 0 ? 0 : levels[Math.min(Math.max(frame, 0), levels.length - 1)];

export const SpeakingAvatar: React.FC<SpeakingAvatarProps> = ({
  curioSrc,
  bgHookSrc,
  bgContentSrc,
  levels,
  handoffFrame,
  glowColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const level = levelAt(levels, frame);

  const curio = staticFile(curioSrc);
  const bgHook = staticFile(bgHookSrc);
  const bgContent = staticFile(bgContentSrc);

  // Passage centre → pastille. Ressort amorti : Curio « se range » dans le coin.
  const handoff = spring({
    frame: frame - handoffFrame,
    fps,
    config: { damping: 18, mass: 0.9, stiffness: 110 },
    durationInFrames: 20,
  });

  const centerX = interpolate(handoff, [0, 1], [W / 2, PILL_CENTER_X]);
  const centerY = interpolate(handoff, [0, 1], [BIG_CENTER_Y, PILL_CENTER_Y]);
  // Dans la pastille, le personnage occupe ~78% du diamètre.
  const height = interpolate(handoff, [0, 1], [BIG_HEIGHT, PILL_SIZE * 0.78]);

  // Respiration lente, indépendante de la voix : sans elle le personnage est
  // mort entre deux syllabes.
  const bob = Math.sin((frame / fps) * 1.7) * interpolate(handoff, [0, 1], [10, 3]);

  // Lumière : un noyau serré toujours présent + une nappe large qui enfle avec
  // la voix. Les deux suivent la SILHOUETTE (drop-shadow), pas un cadre. La
  // nappe est empilée deux fois : un seul drop-shadow donne un halo trop pâle
  // pour se voir sur un fond clair.
  const glowCore = 8 + level * 14;
  const glowWide = 26 + level * 74;
  const glowOpacity = 0.35 + level * 0.5;

  // Fond du hook : flouté et assombri pour détacher Curio du décor.
  const hookBlur = interpolate(handoff, [0, 1], [22, 0]);
  const hookDim = interpolate(handoff, [0, 1], [0.62, 0]);
  const contentScale = interpolate(frame, [handoffFrame, handoffFrame + 200], [1, 1.06], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0E1013" }}>
      {/* Décor de l'état CONTENU, net, dessous. */}
      <Img
        src={bgContent}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${contentScale})`,
        }}
      />

      {/* Décor du HOOK, flouté, qui s'efface au passage en pastille. */}
      <AbsoluteFill style={{ opacity: 1 - handoff }}>
        <Img
          src={bgHook}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            // scale 1.5 : un blur de 22px sur une image au format exact fait
            // apparaître une bordure grise sur les 4 bords (le flou échantillonne
            // hors cadre). On agrandit donc avant de flouter.
            filter: `blur(${hookBlur}px) saturate(1.25)`,
            transform: "scale(1.5)",
          }}
        />
        <AbsoluteFill style={{ backgroundColor: "#000", opacity: hookDim }} />
      </AbsoluteFill>

      {/* Pastille ronde — n'apparaît qu'une fois Curio rangé dans le coin. */}
      <div
        style={{
          position: "absolute",
          left: centerX - PILL_SIZE / 2,
          top: centerY - PILL_SIZE / 2,
          width: PILL_SIZE,
          height: PILL_SIZE,
          borderRadius: "50%",
          backgroundColor: PILL_BG,
          opacity: handoff,
          // Anneau Discord : un liseré net qui s'épaissit avec la voix, plus
          // une nappe diffuse par-dessus.
          boxShadow: `0 0 0 ${3 + level * 7}px ${glowColor}, 0 0 ${24 + level * 46}px ${
            8 + level * 10
          }px ${glowColor}`,
        }}
      />

      {/* Curio. Même élément dans les deux états : il se déplace et rétrécit,
          il n'est jamais remplacé — sinon le raccord saute. */}
      <Img
        src={curio}
        style={{
          position: "absolute",
          height,
          left: centerX,
          top: centerY + bob,
          transform: "translate(-50%, -50%)",
          filter:
            `drop-shadow(0 0 ${glowCore}px ${glowColor}) ` +
            `drop-shadow(0 0 ${glowWide}px ${glowColor}) ` +
            `drop-shadow(0 0 ${glowWide}px ${glowColor}) ` +
            `drop-shadow(0 6px 18px rgba(0,0,0,${glowOpacity * 0.6}))`,
        }}
      />
    </AbsoluteFill>
  );
};

export const SpeakingAvatarComposition: React.FC = () => {
  return (
    <Composition
      id="CurioSpeakingAvatar"
      component={SpeakingAvatar}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={300}
      calculateMetadata={({ props }) => ({
        durationInFrames: props.totalFrames,
      })}
      defaultProps={{
        curioSrc: "curio-avatar/curio_flat.png",
        bgHookSrc: "curio-avatar/bg_hook.png",
        bgContentSrc: "curio-avatar/bg_content.png",
        levels: [] as number[],
        handoffFrame: 120,
        glowColor: "rgba(120, 200, 255, 0.85)",
        totalFrames: 300,
      }}
    />
  );
};
