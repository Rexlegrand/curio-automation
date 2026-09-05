import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Corps du reel au format « deux carrés » — alternance plein écran / deux
// cartes arrondies (Curio qui parle en haut, illustration du sujet en bas).
//
// Remplace le découpage FFmpeg bloc par bloc (cut sec) : le raccord entre les
// deux états est désormais animé. Le RYTHME ne change pas — une coupe toutes
// les ~2,92s — seul le raccord est adouci.
//
// Deux styles de raccord, choisis par la prop transitionStyle :
//   overshoot — les deux cartes glissent depuis le haut et le bas, ressort
//               légèrement amorti : elles dépassent d'un cheveu puis se posent.
//   crossfade — les cartes ne bougent pas, les deux états se fondent l'un dans
//               l'autre. Plus doux, moins dessiné.
//
// Règle de durée : une transition ne s'ajoute jamais au montage, elle consomme
// les TRANSITION_FRAMES premières images du bloc qui arrive. Le corps garde donc
// exactement la durée que lui laisse l'audio (total − hook − CTA).
//
// Hook et CTA ne sont pas ici : ils restent des clips FFmpeg collés autour de
// ce rendu (voir test_deux_carres_manchot.py).

const FPS = 30;
const W = 1080;
const H = 1920;

// Géométrie des cartes — identique au montage FFmpeg validé le 30/08.
const CARD_W = 940;
const CARD_H = 855;
const CARD_R = 36;
const CARD_X = (W - CARD_W) / 2; // 70
const TOP_Y = 80;
const GAP = 50;
const BOT_Y = TOP_Y + CARD_H + GAP; // 985 → marge basse 80, symétrique
const BG_COLOR = "#0E1013";

// Cadrages verticaux des deux cartes, en objectPosition CSS.
//
// PIÈGE : un pourcentage CSS ne se lit PAS comme le focus de la fonction cover()
// du montage FFmpeg. FFmpeg centrait la fenêtre visible sur focus × hauteur ;
// CSS répartit le DÉBORDEMENT (décalage = P × (hauteur_redimensionnée − carte)).
// Reprendre les valeurs FFmpeg telles quelles descend le cadrage d'une trentaine
// de pixels — c'est ce qui rognait l'enseigne néon « curio.education » en haut
// de la carte de Curio. Équivalences calculées pour une carte de 940×855 :
//   Curio  (source 720×1280)  FFmpeg 43,45% → CSS 36,6%
//   Illus  (source 1024×1792) FFmpeg 42,00% → CSS 33,3%
//
// Curio est réglé un cran plus haut que l'équivalence stricte (32% au lieu de
// 36,6%) : l'enseigne commence à 230 px du haut de la source et garde ainsi
// 30 px de marge, au lieu des 2 px de l'ancien réglage. L'illustration reprend
// l'équivalence exacte du montage validé (les 30% du bas restent vides, zone
// réservée aux sous-titres côté charte).
const CURIO_FOCUS_Y = "32%";
const ILLUS_FOCUS_Y = "33.3%";

// Dérive lente sur les plans plein écran, pour qu'ils ne soient pas figés
// (CLAUDE.md §10 : aucun beat sans motion). Mettre à 0 pour des plans fixes.
const KEN_BURNS = 0.045;

// Échelle de départ des cartes en style overshoot : elles arrivent très
// légèrement réduites et se posent à 1. Sans ça, la translation seule fait
// « panneau qui tombe ».
const CARD_SCALE_FROM = 0.955;

export type TransitionStyle = "overshoot" | "crossfade";

export type DeuxCarresBlock = {
  start: number;
  duration: number;
  isSplit: boolean;
  /** Index (0-2) de l'illustration affichée en fond plein écran. */
  bgIllus: number;
  /** Index (0-2) de l'illustration affichée dans la carte du bas. */
  cardIllus: number;
  /** Seconde du clip Curio à laquelle démarre ce bloc. */
  curioOffset: number;
  /** Premier bloc du corps : arrive en cut sec depuis le hook, sans transition. */
  isFirst: boolean;
};

export type DeuxCarresProps = {
  curioSrc: string;
  illusSrcs: string[];
  blocks: DeuxCarresBlock[];
  transitionFrames: number;
  transitionStyle: TransitionStyle;
  totalFrames: number;
};

const Card: React.FC<{
  y: number;
  scale: number;
  opacity: number;
  children: React.ReactNode;
}> = ({ y, scale, opacity, children }) => (
  <div
    style={{
      position: "absolute",
      left: CARD_X,
      top: 0,
      width: CARD_W,
      height: CARD_H,
      borderRadius: CARD_R,
      overflow: "hidden",
      opacity,
      transform: `translateY(${y}px) scale(${scale})`,
      boxShadow: "0 24px 60px rgba(0,0,0,0.45)",
    }}
  >
    {children}
  </div>
);

/** Un bloc du corps : son état (plein écran ou deux carrés) et sa transition d'entrée. */
const Block: React.FC<{
  block: DeuxCarresBlock;
  curioSrc: string;
  illusSrcs: string[];
  transitionFrames: number;
  transitionStyle: TransitionStyle;
}> = ({ block, curioSrc, illusSrcs, transitionFrames, transitionStyle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Avancement du raccord, 0 → 1, quel que soit le style : 1 = état « deux
  // carrés » atteint, 0 = état « plein écran ».
  let progress: number;
  if (block.isFirst) {
    progress = 0;
  } else if (block.isSplit) {
    progress =
      transitionStyle === "overshoot"
        ? // Ressort légèrement amorti : les cartes dépassent d'un cheveu puis
          // se posent. C'est ce dépassement qui rend le raccord vivant.
          spring({
            frame,
            fps,
            config: { damping: 16, mass: 0.7, stiffness: 130 },
            durationInFrames: transitionFrames,
          })
        : interpolate(frame, [0, transitionFrames], [0, 1], {
            easing: Easing.inOut(Easing.quad),
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
  } else {
    // Sortie : pas de rebond, même en overshoot. Les cartes tiennent puis
    // s'échappent vite (ou se fondent, en crossfade).
    progress = interpolate(frame, [0, transitionFrames], [1, 0], {
      easing:
        transitionStyle === "overshoot"
          ? Easing.in(Easing.cubic)
          : Easing.inOut(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // En crossfade les cartes restent en place et c'est l'opacité qui travaille ;
  // en overshoot elles glissent et restent pleinement opaques.
  const slide = transitionStyle === "overshoot" ? progress : 1;
  const cardsOpacity = transitionStyle === "crossfade" ? progress : 1;

  const topY = TOP_Y - (1 - slide) * (TOP_Y + CARD_H);
  const botY = BOT_Y + (1 - slide) * (H - BOT_Y);
  const cardScale = interpolate(slide, [0, 1], [CARD_SCALE_FROM, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const kenBurns = interpolate(frame, [0, block.duration], [1, 1 + KEN_BURNS], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const curioStart = Math.round(block.curioOffset * fps);

  return (
    <AbsoluteFill style={{ backgroundColor: BG_COLOR }}>
      {/* Fond : le plan plein écran, masqué par le fond sombre au fur et à
          mesure que l'état deux carrés s'installe. */}
      <Img
        src={illusSrcs[block.bgIllus]}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${block.isSplit ? 1 : kenBurns})`,
        }}
      />
      <AbsoluteFill style={{ backgroundColor: BG_COLOR, opacity: progress }} />

      {/* Carte du haut — Curio qui parle. Sequence à décalage négatif : le clip
          démarre à curioOffset sans dépendre de startFrom/trimBefore. */}
      <Card y={topY} scale={cardScale} opacity={cardsOpacity}>
        <Sequence from={-curioStart} layout="none">
          <OffthreadVideo
            src={curioSrc}
            muted
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: `50% ${CURIO_FOCUS_Y}`,
            }}
          />
        </Sequence>
      </Card>

      {/* Carte du bas — illustration du sujet. */}
      <Card y={botY} scale={cardScale} opacity={cardsOpacity}>
        <Img
          src={illusSrcs[block.cardIllus]}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: `50% ${ILLUS_FOCUS_Y}`,
          }}
        />
      </Card>
    </AbsoluteFill>
  );
};

export const DeuxCarres: React.FC<DeuxCarresProps> = ({
  curioSrc,
  illusSrcs,
  blocks,
  transitionFrames,
  transitionStyle,
}) => {
  const curio = staticFile(curioSrc);
  const illus = illusSrcs.map((s) => staticFile(s));

  return (
    <AbsoluteFill style={{ backgroundColor: BG_COLOR }}>
      {blocks.map((block, i) => (
        <Sequence key={i} from={block.start} durationInFrames={block.duration}>
          <Block
            block={block}
            curioSrc={curio}
            illusSrcs={illus}
            transitionFrames={transitionFrames}
            transitionStyle={transitionStyle}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const DeuxCarresComposition: React.FC = () => {
  return (
    <Composition
      id="CurioDeuxCarres"
      component={DeuxCarres}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={876}
      calculateMetadata={({ props }) => ({
        durationInFrames: props.totalFrames,
      })}
      defaultProps={{
        curioSrc: "deux-carres/curio_talk.mp4",
        illusSrcs: [
          "deux-carres/illus_1.png",
          "deux-carres/illus_2.png",
          "deux-carres/illus_3.png",
        ],
        blocks: [] as DeuxCarresBlock[],
        transitionFrames: 11,
        transitionStyle: "overshoot" as TransitionStyle,
        totalFrames: 876,
      }}
    />
  );
};
