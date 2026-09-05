import React from "react";
import { Composition, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Backdrop } from "./backdrop";
import { Captions, useMots } from "./captions";
import { Stage, duoProgress } from "./stage";
import { Grain, Vignette, SANS, SERIF, OLIVE, CREAM, FPS, W, H } from "./shared";
import { DUREES2, V2_ORIGINE } from "./timing2";

// Montage 2, beat « l'origine ».
// « Et tout ce sable vient d'un seul endroit. La dépression du Bodélé, au
//   Tchad. Un lac immense... asséché depuis des milliers d'années. »
//
// Curio pose la question dans la carte du haut ; la vue satellite répond en
// plein écran, une fois le lieu nommé. C'est le principe de tout ce montage :
// la parole en carte, la preuve en grand.
//
// L'image est une vraie prise MODIS de la NASA au-dessus du Bodélé — on y voit
// le lac Tchad et le panache de poussière qui s'en élève.

const DURATION = DUREES2.origine;

export const V2Origine: React.FC = () => {
  const frame = useCurrentFrame();
  const mots = useMots("mots2/02-origine");
  const t = duoProgress(frame, V2_ORIGINE.curio);

  // Le zoom court sur tout le plan, sans se soucier de la bascule : c'est lui
  // qui relie les deux états.
  const zoom = interpolate(frame, [0, DURATION], [1.0, 1.34], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  const label = interpolate(
    frame,
    [V2_ORIGINE.labelIn, V2_ORIGINE.labelIn + 22, DURATION - 50, DURATION - 24],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) },
  );

  return (
    <Stage
      t={t}
      curio={V2_ORIGINE.curio}
      background={<Backdrop frame={frame} accent="#8C6B2F" />}
      overlay={
        <>
          {/* Le nom du lieu n'apparaît qu'une fois le plein écran repris : sur
              une carte de 940 px il aurait mangé la moitié de l'image. */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 250,
              textAlign: "center",
              opacity: label * (1 - t),
            }}
          >
            <div
              style={{
                fontFamily: SANS,
                fontWeight: 700,
                fontSize: 44,
                letterSpacing: 8,
                color: CREAM,
                textShadow: "0 3px 18px rgba(0,0,0,0.95)",
              }}
            >
              TCHAD
            </div>
            <div
              style={{
                fontFamily: SERIF,
                fontSize: 112,
                color: OLIVE,
                marginTop: 2,
                textShadow: "0 5px 26px rgba(0,0,0,0.98)",
              }}
            >
              Bodélé
            </div>
          </div>
          <Vignette strength={0.58} />
          <Grain frame={frame} opacity={0.09} />
          <Captions mots={mots} frame={frame} fps={FPS} />
        </>
      }
    >
      <Img
        src={staticFile("sahara/bodele.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${zoom})`,
        }}
      />
    </Stage>
  );
};

export const V2OrigineComposition: React.FC = () => (
  <Composition
    id="sahara2-02-origine"
    component={V2Origine}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={DURATION}
  />
);
