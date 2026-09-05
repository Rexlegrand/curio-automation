import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { Captions, useMots } from "../../sahara/captions";
import { Grain, SANS, SERIF, CREAM, OLIVE, FPS, W } from "../../sahara/shared";

// Beat 4 — le chiffre. C'est le pic du reel, l'équivalent exact du beat des
// camions dans le sahara : un ordre de grandeur qu'on ne peut pas se
// représenter, ramené à un objet qu'on connaît.
// « Onze kilomètres. Pose l'Everest tout au fond... et il reste encore deux
//   kilomètres d'eau au-dessus du sommet. »
//
// Tout est dessiné, rien n'est photographié. Une photo de montagne aurait sa
// propre perspective et son propre horizon, et la comparaison ne tiendrait
// plus : ici une seule échelle verticale gouverne la colonne d'eau, la
// graduation et la montagne, donc les proportions à l'écran SONT les
// proportions réelles. C'est la seule façon d'avoir le droit de dire « il
// reste deux kilomètres ».
//
// La montagne tombe, elle n'apparaît pas : « pose l'Everest tout au fond » est
// un geste, et le voir s'accomplir vaut mieux qu'un fondu. Elle décélère fort
// en arrivant, pour qu'on lise un poids.

export type EchelleVerticaleProps = {
  duration: number;
  segment: string;
  /** Profondeur de la fosse, en mètres. Gouverne toute la géométrie. */
  fond: number;
  /** Hauteur de la montagne posée au fond, en mètres. */
  montagne: number;
  /** Image où le chiffre s'affiche, où la montagne tombe, où l'écart se
   *  mesure. Tous calés sur les mots. */
  chiffreIn: number;
  chuteFrom: number;
  ecartFrom: number;
};

// La colonne d'eau occupe une bande fixe du cadre : la surface assez bas pour
// laisser le chiffre respirer, le fond assez haut pour laisser passer les
// sous-titres.
const SURFACE_Y = 470;
const FOND_Y = 1560;

export const EchelleVerticale: React.FC<EchelleVerticaleProps> = ({
  duration,
  segment,
  fond,
  montagne,
  chiffreIn,
  chuteFrom,
  ecartFrom,
}) => {
  const frame = useCurrentFrame();
  const mots = useMots(segment);

  // L'unique échelle : mètres vers pixels. Tout ce qui suit en dépend.
  const echelle = (FOND_Y - SURFACE_Y) / fond;
  const sommetY = FOND_Y - montagne * echelle;
  const ecartMetres = fond - montagne;

  const chute = interpolate(frame, [chuteFrom, chuteFrom + 42], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    // Décélération forte : la montagne arrive lourdement, elle ne se pose pas.
    easing: Easing.out(Easing.cubic),
  });
  // Elle part au-dessus du cadre et vient s'asseoir sur le fond.
  const montagneY = interpolate(chute, [0, 1], [-(FOND_Y - sommetY) - 200, 0]);

  const chiffre = interpolate(frame, [chiffreIn, chiffreIn + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const ecart = interpolate(frame, [ecartFrom, ecartFrom + 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Graduations tous les 2 000 m, plus le fond. Elles donnent l'échelle sans
  // qu'on ait à la lire : c'est leur régularité qui fait la profondeur.
  const graduations: number[] = [];
  for (let m = 2000; m < fond; m += 2000) graduations.push(m);

  const largeur = 560; // largeur de la base de la montagne

  return (
    <AbsoluteFill style={{ backgroundColor: "#03070C" }}>
      {/* La colonne d'eau : claire en surface, noire au fond. Le dégradé fait
          tout le travail d'ambiance, il n'y a aucune image dans ce plan. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: SURFACE_Y,
          height: FOND_Y - SURFACE_Y,
          background:
            "linear-gradient(180deg, #2E6E8E 0%, #12405C 26%, #072335 58%, #030F19 100%)",
        }}
      />

      {/* Le ciel au-dessus de la surface, pour que la ligne d'eau se lise. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 0,
          height: SURFACE_Y,
          background: "linear-gradient(180deg, #0B1620 0%, #16384B 100%)",
        }}
      />

      {/* Graduations. */}
      {graduations.map((m) => {
        const y = SURFACE_Y + m * echelle;
        return (
          <div key={m} style={{ position: "absolute", left: 0, right: 0, top: y }}>
            <div style={{ height: 1, background: "rgba(255,255,255,0.13)" }} />
            <div
              style={{
                position: "absolute",
                left: 30,
                top: -34,
                fontFamily: SANS,
                fontWeight: 700,
                fontSize: 26,
                letterSpacing: 2,
                color: "rgba(237,234,226,0.5)",
              }}
            >
              -{m.toLocaleString("fr-FR").replace(/ | /g, " ")} m
            </div>
          </div>
        );
      })}

      {/* La montagne. Un triangle, pas une silhouette dessinée : la moindre
          fantaisie de contour ferait douter des proportions, et ce sont elles
          l'argument du plan. */}
      <div
        style={{
          position: "absolute",
          left: (W - largeur) / 2,
          top: 0,
          width: largeur,
          height: FOND_Y,
          transform: `translateY(${montagneY}px)`,
        }}
      >
        <svg
          width={largeur}
          height={FOND_Y}
          style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}
        >
          <defs>
            <linearGradient id="roche" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#E7EDF2" />
              <stop offset="14%" stopColor="#93A3B0" />
              <stop offset="100%" stopColor="#2A3641" />
            </linearGradient>
          </defs>
          <polygon
            points={`${largeur / 2},${sommetY} ${largeur},${FOND_Y} 0,${FOND_Y}`}
            fill="url(#roche)"
          />
        </svg>
      </div>

      {/* Le sol de la fosse, posé PAR-DESSUS la base de la montagne : elle est
          dedans, pas devant. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: FOND_Y,
          bottom: 0,
          background: "linear-gradient(180deg, #4A4235 0%, #241F18 100%)",
        }}
      />
      <div
        style={{ position: "absolute", left: 0, right: 0, top: FOND_Y, height: 3, background: "#6B5F4A" }}
      />

      {/* L'écart : la bande d'eau qui reste au-dessus du sommet. C'est la
          phrase du beat, rendue mesurable. */}
      {ecart > 0 ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: SURFACE_Y,
            height: (sommetY - SURFACE_Y) * chute + (1 - chute) * 0,
            opacity: ecart,
            background: "rgba(245,199,122,0.16)",
            borderTop: "2px solid rgba(245,199,122,0.85)",
            borderBottom: "2px solid rgba(245,199,122,0.85)",
          }}
        >
          <div
            style={{
              position: "absolute",
              right: 34,
              top: "50%",
              transform: "translateY(-50%)",
              fontFamily: SANS,
              fontWeight: 700,
              fontSize: 46,
              letterSpacing: 2,
              color: "#F5C77A",
              textShadow: "0 3px 16px rgba(0,0,0,0.9)",
              textAlign: "right",
              lineHeight: 1.1,
            }}
          >
            {(ecartMetres / 1000).toFixed(1).replace(".", ",")} km
            <div style={{ fontSize: 26, letterSpacing: 5, color: CREAM, opacity: 0.85 }}>
              ENCORE D'EAU
            </div>
          </div>
        </div>
      ) : null}

      {/* Ligne de surface, toujours au-dessus de tout le reste. */}
      <div
        style={{ position: "absolute", left: 0, right: 0, top: SURFACE_Y, height: 3, background: "#7FC7E8" }}
      />
      <div
        style={{
          position: "absolute",
          left: 30,
          top: SURFACE_Y - 42,
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 6,
          color: "#7FC7E8",
        }}
      >
        SURFACE
      </div>

      {/* Le chiffre, en haut, dès le premier mot. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 150,
          textAlign: "center",
          opacity: chiffre,
          transform: `scale(${0.94 + 0.06 * chiffre})`,
        }}
      >
        <div style={{ fontFamily: SERIF, fontSize: 128, color: OLIVE, lineHeight: 1 }}>
          {(fond / 1000).toFixed(0)} km
        </div>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 34,
            letterSpacing: 7,
            color: CREAM,
            marginTop: 6,
          }}
        >
          DE PROFONDEUR
        </div>
      </div>

      <Grain frame={frame} opacity={0.08} />
      <Captions mots={mots} frame={frame} fps={FPS} />
    </AbsoluteFill>
  );
};
