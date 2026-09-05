import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Reconstruction — @craftedbycm, short Cw_521ifpT8
// « Cadre-dans-l'écran (TV vintage) », motion-catalog.md catégorie 7.
//
// Relevé sur le short, image par image :
//
//   1. le plan démarre PLEIN CADRE, puis la caméra RECULE et découvre le poste
//      autour. Le poste ne se fond pas par-dessus l'image : il est là depuis le
//      début, simplement hors champ. Un fondu donnerait une télé transparente
//      posée sur la photo.
//   2. le poste CHANGE de modèle, en coupe sèche, pendant que le plan continue.
//      C'est le propos même de la vidéo d'origine — auditionner des cadres — et
//      ça tient tout seul comme figure de style : le sujet ne bouge pas, son
//      cadre oui.
//   3. le texte reste DEHORS. Titre au-dessus des postes, sous-titre en
//      dessous. La vitre ne porte jamais que l'image — c'est ce qui fait qu'on
//      regarde une télé au lieu de lire un habillage.
//   4. le titre a deux registres : une ligne courante en sans-serif, et le mot
//      qui porte le sens en serif, beaucoup plus gros.
//   5. les scanlines sont franches, pas discrètes.
//
// Le recul est un vrai mouvement de caméra : un seul conteneur porte le poste,
// la vitre et son contenu, et c'est LUI qui est mis à l'échelle. Les couches ne
// peuvent donc pas se désolidariser. Contrepartie : tout ce qui est réglé en
// pixels à l'intérieur (scanlines, décalage RVB) est agrandi d'autant — ces
// deux valeurs sont divisées par l'échelle pour rester constantes à l'écran.
//
// Ordre des couches, de l'arrière vers l'avant :
//   1. le noir de studio, avec un halo très doux au centre
//   2. la lueur de l'écran, qui déborde sur le meuble
//   3. le plan et son habillage de tube
//   4. le reflet de la vitre, qui recolle le plan au verre
//   5. le poste détouré, dont le perçage découpe tout ce qui précède
//   6. les deux blocs de texte, hors des postes et hors du mouvement de caméra

const FPS = 30;
const W = 1080;
const H = 1920;

// Le plan reste plein cadre le temps qu'on le lise, puis la caméra recule.
const REVEAL_FROM = 14;
const REVEAL_TO = 56;
const TITLE_FROM = 58;
const CAPTION_FROM = 70;
// Décrochage de tube sur les premières images d'un changement de poste : le
// tube d'un autre téléviseur ne reprend pas l'image proprement. Deux images
// suffisent — au-delà ça devient un effet, pas un raccord.
const CUT_GLITCH = 2;

export type ScreenRect = { x: number; y: number; width: number; height: number };

export type TvPlate = {
  plate: string;
  screenRect: ScreenRect;
};

export type Shot = { tv: number; duration: number };

export type VintageTvFrameProps = {
  src: string;
  tvs: TvPlate[];
  shots: Shot[];
  textTop: number;
  textBottom: number;
  title: string;
  keyword: string;
  caption: string;
  rgbSplit: number;
  zoomFrom: number;
  zoomTo: number;
};

/** Plan courant et nombre d'images écoulées depuis sa première. */
const shotAt = (shots: Shot[], frame: number) => {
  let start = 0;
  for (let i = 0; i < shots.length; i++) {
    if (frame < start + shots[i].duration || i === shots.length - 1) {
      return { index: i, tv: shots[i].tv, since: frame - start };
    }
    start += shots[i].duration;
  }
  return { index: 0, tv: shots[0].tv, since: frame };
};

export const VintageTvFrame: React.FC<VintageTvFrameProps> = ({
  src,
  tvs,
  shots,
  textTop,
  textBottom,
  title,
  keyword,
  caption,
  rgbSplit,
  zoomFrom,
  zoomTo,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const shot = shotAt(shots, frame);
  const tv = tvs[shot.tv];
  const { screenRect } = tv;

  // Le zoom du plan court sur toute la durée, sans se soucier des coupes :
  // c'est lui qui tient l'ensemble, un poste chasse l'autre mais l'image
  // continue.
  const zoom = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  // Le recul de caméra n'appartient qu'au premier plan : les suivants sont des
  // coupes sèches sur un dispositif déjà posé.
  const reveal =
    shot.index === 0
      ? interpolate(frame, [REVEAL_FROM, REVEAL_TO], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.inOut(Easing.cubic),
        })
      : 1;
  const lerp = (a: number, b: number) => a + (b - a) * reveal;

  const startScale = Math.max(W / screenRect.width, H / screenRect.height);
  const cx = screenRect.x + screenRect.width / 2;
  const cy = screenRect.y + screenRect.height / 2;
  const targetX = lerp(W / 2, cx);
  const targetY = lerp(H / 2, cy);
  const scale = lerp(startScale, 1);
  const tx = targetX - cx * scale;
  const ty = targetY - cy * scale;

  // Compensations d'échelle : sans elles, les scanlines font 17 px de haut et
  // le décalage RVB 8 px au premier plan.
  const glitching = shot.index > 0 && shot.since < CUT_GLITCH;
  const split = (glitching ? rgbSplit * 3.5 : rgbSplit) / scale;
  const scanPeriod = 5 / scale;
  const scanGap = 2 / scale;
  const scanOffset = ((frame * 0.55) % 5) / scale;
  const rollY = glitching ? 12 : ((frame % 100) / 100) * 140 - 20;
  const flicker = (1 + Math.sin(frame * 0.9) * 0.014) * (glitching ? 1.12 : 1);

  const titleIn = interpolate(frame, [TITLE_FROM, TITLE_FROM + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const captionIn = interpolate(frame, [CAPTION_FROM, CAPTION_FROM + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Rectangle PLEIN, sans coins arrondis : le contour du tube est découpé par
  // le boîtier lui-même, qui est opaque et posé par-dessus. Reproduire ici un
  // rayon approché laisserait apparaître le fond dans les coins.
  const screenBox: React.CSSProperties = {
    position: "absolute",
    left: screenRect.x,
    top: screenRect.y,
    width: screenRect.width,
    height: screenRect.height,
  };

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Filtre de décalage RVB : canaux rouge et bleu écartés, vert en place. */}
      <svg width="0" height="0" style={{ position: "absolute" }}>
        <defs>
          <filter id="crt-rgb-split" colorInterpolationFilters="sRGB">
            <feOffset in="SourceGraphic" dx={-split} dy="0" result="rShift" />
            <feColorMatrix
              in="rShift"
              type="matrix"
              values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"
              result="rOnly"
            />
            <feOffset in="SourceGraphic" dx={split} dy="0" result="bShift" />
            <feColorMatrix
              in="bShift"
              type="matrix"
              values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0"
              result="bOnly"
            />
            <feColorMatrix
              in="SourceGraphic"
              type="matrix"
              values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0"
              result="gOnly"
            />
            <feBlend in="rOnly" in2="gOnly" mode="screen" result="rg" />
            <feBlend in="rg" in2="bOnly" mode="screen" />
          </filter>
        </defs>
      </svg>

      {/* 1 — le noir de studio. Un halo à peine perceptible au centre évite
          l'aplat mort et pose les postes dans un volume. Hors caméra : le fond
          d'un studio ne recule pas avec le sujet. */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(64% 44% at 50% 46%, #1A1714 0%, #0B0A09 58%, #000 100%)",
        }}
      />

      {/* Le poste et son image, solidaires, portés par le mouvement de caméra. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: W,
          height: H,
          transformOrigin: "0 0",
          transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
        }}
      >
        {/* 2 — la lueur de l'écran qui déborde sur le meuble. C'est ce débord
            qui fait qu'un tube allumé dans le noir n'a pas l'air d'un
            autocollant. Volontairement discrète : au-delà, elle bave entre les
            pieds du poste et trahit le montage. */}
        <div
          style={{
            ...screenBox,
            left: screenRect.x - 60,
            top: screenRect.y - 60,
            width: screenRect.width + 120,
            height: screenRect.height + 120,
            overflow: "hidden",
            opacity: 0.32,
          }}
        >
          <Img
            src={staticFile(src)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${zoom * 1.1})`,
              filter: "blur(46px) saturate(0.6) brightness(0.75)",
            }}
          />
        </div>

        {/* 3 — le plan et son habillage de tube */}
        <div style={{ ...screenBox, overflow: "hidden" }}>
          <Img
            src={staticFile(src)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${zoom})`,
              filter:
                `url(#crt-rgb-split) saturate(0.5) contrast(1.16) sepia(0.16) ` +
                `brightness(${flicker})`,
            }}
          />
          <AbsoluteFill
            style={{
              backgroundImage:
                "repeating-linear-gradient(to bottom," +
                `rgba(0,0,0,0) 0px, rgba(0,0,0,0) ${scanGap}px,` +
                `rgba(0,0,0,0.32) ${scanGap}px, rgba(0,0,0,0.32) ${scanPeriod}px)`,
              transform: `translateY(${scanOffset}px)`,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: `${rollY}%`,
              height: "18%",
              background:
                "linear-gradient(to bottom, rgba(255,255,255,0) 0%," +
                `rgba(255,255,255,${glitching ? 0.22 : 0.08}) 45%,` +
                "rgba(255,255,255,0) 100%)",
            }}
          />
          <AbsoluteFill
            style={{
              background:
                "radial-gradient(116% 96% at 50% 48%," +
                "rgba(0,0,0,0) 44%, rgba(0,0,0,0.42) 84%, rgba(0,0,0,0.74) 100%)",
            }}
          />
        </div>

        {/* 4 — reflet de la vitre. Sans lui, l'image a l'air peinte sur le
            meuble au lieu d'être derrière un verre. Il passe SOUS le boîtier :
            le verre est au fond du trou, pas devant le bois, et c'est le
            boîtier qui lui découpe ses coins. */}
        <div
          style={{
            ...screenBox,
            background:
              "linear-gradient(122deg, rgba(255,255,255,0.15) 0%," +
              "rgba(255,255,255,0.045) 26%, rgba(255,255,255,0) 50%)",
            pointerEvents: "none",
          }}
        />

        {/* 5 — le poste, par-dessus tout le reste */}
        <Img
          src={staticFile(tv.plate)}
          style={{ position: "absolute", left: 0, top: 0, width: W, height: H }}
        />
      </div>

      {/* 6a — titre AU-DESSUS des postes. Sa place ne dépend d'AUCUN poste en
          particulier : `textTop` est l'enveloppe commune à tous ceux de la
          séquence. Se caler sur le poste courant ferait sauter le texte à
          chaque coupe, alors que c'est justement lui le point fixe. Ligne
          courante en sans-serif, mot porteur en serif deux fois plus gros : le
          contraste de fonte fait la hiérarchie, pas la couleur. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 0,
          height: textTop,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-end",
          padding: "0 70px",
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * -14}px)`,
        }}
      >
        <div
          style={{
            fontFamily: "Helvetica, Arial, sans-serif",
            fontWeight: 700,
            fontSize: 50,
            color: "#EDEAE2",
            textAlign: "center",
            lineHeight: 1.2,
            textShadow: "0 3px 14px rgba(0,0,0,0.9)",
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: 108,
            color: "#B8BC94",
            textAlign: "center",
            lineHeight: 1.06,
            marginTop: 6,
            textShadow: "0 4px 20px rgba(0,0,0,0.95)",
          }}
        >
          {keyword}
        </div>
      </div>

      {/* 6b — sous-titre EN DESSOUS des postes, sur le noir. Petite boîte sombre
          comme dans le short : elle décolle le texte du fond sans jamais mordre
          sur la vitre. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: textBottom,
          display: "flex",
          justifyContent: "center",
          opacity: captionIn,
          transform: `translateY(${(1 - captionIn) * 12}px)`,
        }}
      >
        <div
          style={{
            fontFamily: "Helvetica, Arial, sans-serif",
            fontWeight: 700,
            fontSize: 46,
            letterSpacing: 0.5,
            color: "#FFFFFF",
            backgroundColor: "rgba(18,18,18,0.72)",
            borderRadius: 8,
            padding: "10px 22px",
            textAlign: "center",
            maxWidth: 900,
          }}
        >
          {caption}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Poste officiel : le premier téléviseur généré, retenu comme le plus naturel.
// Un seul poste, pas de séquence — c'est la version de référence. Les autres
// postes et l'enchaînement sont fournis en props par test_craftedbycm.py, qui
// les construit depuis assets/craftedbycm/tv_plates.json.
const DEFAULT_TV: TvPlate = {
  plate: "craftedbycm/tv_plate_officiel.png",
  screenRect: { x: 173, y: 606, width: 736, height: 564 },
};

export const VintageTvFrameComposition: React.FC = () => {
  return (
    <Composition
      id="craftedbycm-01"
      component={VintageTvFrame}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={150}
      // La durée est la somme des plans : elle change avec les props, elle ne
      // peut donc pas être une constante.
      calculateMetadata={({ props }) => ({
        durationInFrames: props.shots.reduce((n, s) => n + s.duration, 0),
      })}
      defaultProps={{
        src: "craftedbycm/plate.jpg",
        tvs: [DEFAULT_TV],
        shots: [{ tv: 0, duration: 150 }],
        textTop: 450,
        textBottom: 1480,
        title: "Il existe un lac entièrement",
        keyword: "Rose",
        caption: "ET SA COULEUR EST BIEN RÉELLE.",
        rgbSplit: 2.4,
        zoomFrom: 1.04,
        zoomTo: 1.14,
      }}
    />
  );
};
