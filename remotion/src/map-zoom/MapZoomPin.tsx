import React from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { geoMercator, geoPath, ExtendedFeature, ExtendedFeatureCollection } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;
const DURATION_SECONDS = 6;

// Testé 10m vs 50m (demande Benjamin, qualité perçue trop faible au zoom serré) :
// 10m ~4x plus lent à rendre (41s vs 10s pour ce clip de 6s, fichier 3,7 Mo vs
// 756 Ko) ET ne montre PAS plus de détail utile sur la zone visée — au zoom
// serré (fin d'animation), le tracé de côte proche de FOCUS a une forme
// légèrement différente entre les deux résolutions ; Middle Island (l'île
// exacte du lac Hillier) n'apparaît dans AUCUNE des deux résolutions testées
// (île trop petite, exclue du jeu de données "countries" même à 10m — pas
// testé sur le jeu "land", séparé, physique plutôt qu'administratif).
// Conclusion : 50m gardé, le gain 10m est nul ici, seul le coût du rendu augmente.
const MAP_DATA_FILE = "countries-50m.json";

// Sujet validé le 17/08/2026 : lac Hillier, Middle Island (Australie).
const AUSTRALIA_ID = "036"; // ISO 3166-1 numérique, identifiant stable entre les résolutions world-atlas
const FOCUS: [number, number] = [123.2028, -34.0956]; // Lac Hillier
const LABEL_TEXT = "Lac Hillier";
// Le point FOCUS projette toujours exactement sur SCREEN_TARGET, quelle que soit
// l'échelle (center+translate fixes) — c'est ce qui permet un zoom vers un point
// fixe sans recalculer la position à chaque frame.
// Y à 0.42 laissait un cadrage final cassé (feedback Benjamin) : la côte ne
// touchait que le haut de l'écran, ~60% de vide (océan) en dessous — le pin est
// sur la côte SUD de l'Australie, donc la terre est TOUJOURS au-dessus du point
// d'ancrage et l'océan toujours en dessous ; remonter Y descend le point à
// l'écran et fait mécaniquement remonter la proportion de terre visible.
const SCREEN_TARGET: [number, number] = [WIDTH / 2, HEIGHT * 0.58];

// Timing (frames à 30fps, 6s total) : zoom monde → côte, ralenti (feedback
// Benjamin : rythme trop rapide en v1, ZOOM_END passe de 70 à 115 sur une
// durée totale allongée de 5s à 6s pour laisser le nom respirer après le zoom).
const ZOOM_END = 115;
const PIN_START = 100;
const LABEL_START = 122;
const OUTRO_START = 155;

type Props = {
  countries: ExtendedFeatureCollection;
  target: ExtendedFeature | null;
};

// Échelle nécessaire pour que `geo` tienne dans une boîte boxWidth×boxHeight,
// projection centrée sur `center`/`translate` fixes (mesure à scale=1 puis règle de trois).
const scaleToFit = (
  geo: ExtendedFeature | ExtendedFeatureCollection,
  boxWidth: number,
  boxHeight: number,
  center: [number, number],
  translate: [number, number]
) => {
  const probe = geoMercator().center(center).translate(translate).scale(1);
  const path = geoPath(probe);
  const bounds = path.bounds(geo);
  const dx = bounds[1][0] - bounds[0][0];
  const dy = bounds[1][1] - bounds[0][1];
  return Math.min(boxWidth / dx, boxHeight / dy);
};

// Ordre des points SW→NW→NE→SE→SW (horaire en lon/lat) : d3-geo interprète les
// anneaux sur la sphère selon la règle de la main droite — un anneau anti-horaire
// en lon/lat (SW→SE→NE→NW) est lu comme "tout le globe SAUF ce carré" et fait
// exploser scaleToFit (bounds ≈ 2π, un tour complet). Vérifié par calcul direct
// avant ce fix : winding anti-horaire → scale ≈ 92 (faux, dézoome) ; horaire →
// scale ≈ 34000 (correct, zoom serré sur la zone).
const localBoxAround = (center: [number, number], halfDegrees: number): ExtendedFeature => ({
  type: "Feature",
  properties: {},
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [center[0] - halfDegrees, center[1] - halfDegrees],
        [center[0] - halfDegrees, center[1] + halfDegrees],
        [center[0] + halfDegrees, center[1] + halfDegrees],
        [center[0] + halfDegrees, center[1] - halfDegrees],
        [center[0] - halfDegrees, center[1] - halfDegrees],
      ],
    ],
  },
});

export const MapZoomPin: React.FC<Props> = ({ countries }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Départ sur le monde entier (feedback Benjamin — v1 démarrait déjà cadrée
  // sur l'Australie seule) : on fit `countries` en entier, pas juste `target`.
  const scaleWide = scaleToFit(countries, WIDTH * 0.9, HEIGHT * 0.5, FOCUS, SCREEN_TARGET);
  const scaleClose = scaleToFit(localBoxAround(FOCUS, 0.4), WIDTH * 0.6, HEIGHT * 0.3, FOCUS, SCREEN_TARGET);

  const zoomT = interpolate(frame, [0, ZOOM_END], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const scale = scaleWide + (scaleClose - scaleWide) * zoomT;

  const projection = geoMercator().center(FOCUS).translate(SCREEN_TARGET).scale(scale);
  const path = geoPath(projection);

  const pinVisible = frame >= PIN_START;
  const pinProgress = spring({ frame: frame - PIN_START, fps, config: { damping: 12, mass: 0.6 } });

  const labelOpacity = interpolate(frame, [LABEL_START, LABEL_START + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const labelY = interpolate(frame, [LABEL_START, LABEL_START + 15], [10, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const outroOpacity = interpolate(frame, [OUTRO_START, OUTRO_START + 25], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#eaf3fb", opacity: outroOpacity }}>
      <svg width={WIDTH} height={HEIGHT} viewBox={`0 0 ${WIDTH} ${HEIGHT}`}>
        {countries.features.map((f) => (
          <path
            key={f.id as string}
            d={path(f) ?? undefined}
            fill={f.id === AUSTRALIA_ID ? "#3ec1ff" : "#d7e3ea"}
            stroke="#9fb4c2"
            strokeWidth={1}
          />
        ))}
        {pinVisible && (
          <g transform={`translate(${SCREEN_TARGET[0]}, ${SCREEN_TARGET[1]}) scale(${pinProgress})`}>
            <circle r={14} fill="#e63946" stroke="white" strokeWidth={4} />
            <circle r={4} fill="white" />
          </g>
        )}
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: SCREEN_TARGET[1] + 30,
          textAlign: "center",
          opacity: labelOpacity,
          transform: `translateY(${labelY}px)`,
        }}
      >
        <span
          style={{
            fontFamily: "Arial, sans-serif",
            fontWeight: 700,
            fontSize: 56,
            color: "#1d3557",
            background: "white",
            padding: "10px 28px",
            borderRadius: 999,
            boxShadow: "0 4px 14px rgba(0,0,0,0.15)",
          }}
        >
          {LABEL_TEXT}
        </span>
      </div>
    </AbsoluteFill>
  );
};

const calculateMetadata: CalculateMetadataFunction<Props> = async () => {
  const response = await fetch(staticFile(MAP_DATA_FILE));
  const topology = (await response.json()) as Topology;
  const geo = feature(
    topology,
    topology.objects.countries as GeometryCollection
  ) as unknown as ExtendedFeatureCollection;
  const target = geo.features.find((f) => f.id === AUSTRALIA_ID) ?? null;

  return {
    durationInFrames: DURATION_SECONDS * FPS,
    props: { countries: geo, target },
  };
};

export const MapZoomPinComposition: React.FC = () => {
  return (
    <Composition
      id="MapZoomPin"
      component={MapZoomPin}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      durationInFrames={DURATION_SECONDS * FPS}
      defaultProps={{ countries: { type: "FeatureCollection", features: [] }, target: null } as Props}
      calculateMetadata={calculateMetadata}
    />
  );
};
