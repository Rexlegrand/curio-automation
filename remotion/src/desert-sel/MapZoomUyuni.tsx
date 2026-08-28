import React, { useEffect } from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  continueRender,
  delayRender,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { geoMercator, geoPath, ExtendedFeature, ExtendedFeatureCollection } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";

// Scène 3 (localisation) + scène 4 (CTA) du reel "désert de sel miroir géant".
// Même technique map-engine que map-zoom/MapZoomPin.tsx (validée sur le reel
// lac Hillier) : monde entier -> zoom sur le pays -> pin + label. Le CTA
// s'affiche en overlay sur la fin de cette même scène plutôt qu'une scène
// séparée (§3 CLAUDE.md : CTA_TEXTE fixe, logo Curio).

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;

// Durée calée sur audio_v1.mp3 (32.48s) + AUDIO_TAIL (0.2s, config.py) moins
// les 20s déjà couvertes par DesertSelMirrorScenes (10s sol sec+miroir + 10s
// silhouette) : (32.48 + 0.2 - 20) * 30 = 380.4 -> 380 frames.
const DURATION_FRAMES = 380;

const MAP_DATA_FILE = "countries-50m.json";
const WORLD_TEXTURE_WIDTH = 8192;
const WORLD_TEXTURE_HEIGHT = 4096;

const BOLIVIA_ID = "068"; // ISO 3166-1 numérique
const FOCUS: [number, number] = [-67.4891, -20.1338]; // Salar d'Uyuni
const COUNTRY_LABEL_TEXT = "BOLIVIE";
const SITE_LABEL_TEXT = "Salar d'Uyuni";
const SCREEN_TARGET: [number, number] = [WIDTH / 2, HEIGHT * 0.58];
const CTA_TEXTE = "Envoie CURIO en MP pour recevoir une activité/un exercice gratuit !";

// Timing (frames à 30fps) : zoom monde -> pays (frontière allumée en rouge +
// nom du pays), puis pin + nom du site précis, puis CTA en overlay sur les
// ~4 dernières secondes, pendant que la carte reste visible en fond (pas de
// fondu vers du vide, règle §3).
const ZOOM_END = 160;
const BORDER_GLOW_START = 130; // la frontière s'allume avant la fin du zoom
const COUNTRY_LABEL_START = 142; // "BOLIVIE" en grand
const PIN_START = 178; // le pin tombe une fois le pays identifié
const SITE_LABEL_START = 198; // nom du site précis (Salar d'Uyuni)
const CTA_START = 260;

type Props = {
  countries: ExtendedFeatureCollection;
  target: ExtendedFeature | null;
};

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

// Ordre SW->NW->NE->SE->SW obligatoire (winding horaire lon/lat) — voir
// map-zoom/MapZoomPin.tsx pour l'explication complète du piège d3-geo.
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

// L'Antarctique (id "010") fait exploser la hauteur de la bounding box en
// projection Mercator (déformation extrême près des pôles) : le plan large
// se retrouvait dézoomé à l'excès pour caser un continent qu'on ne regarde
// jamais dans ce reel. Exclue du calcul de cadrage ET du rendu (jamais visible
// dans ce reel de toute façon).
const WIDE_SHOT_MAX_LATITUDE_ID_EXCLUDE = "010";

// Cadrer le plan large sur les bounds RÉELS de `countries` s'est révélé fragile :
// un pays traverse l'antiméridien (points à la fois près de -180° et +180°),
// ce qui fait exploser la largeur de la bounding box exactement comme
// l'Antarctique explosait la hauteur (feedback Benjamin : plan large trop
// dézoomé, la carte ne remplit pas l'écran). Fix robuste : cadrer sur une boîte
// lon/lat FIXE, CENTRÉE sur FOCUS (sinon le point d'ancrage à l'écran n'est
// pas au milieu de la boîte -> grand vide d'un côté, coupe de l'autre) et de
// ratio proche du cadre 9:16 (sinon une des deux dimensions ne contraint
// jamais l'échelle et l'autre laisse des bandes vides) : Amériques + bord
// Atlantique seulement, pas le globe entier — un zoom monde parfaitement
// symétrique n'est pas l'objectif, remplir l'écran l'est.
const WORLD_VIEW_LON_HALF_SPAN = 70;
const WORLD_VIEW_LAT_RANGE: [number, number] = [-55, 65];
const WORLD_VIEW_BOX: ExtendedFeature = {
  type: "Feature",
  properties: {},
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [FOCUS[0] - WORLD_VIEW_LON_HALF_SPAN, WORLD_VIEW_LAT_RANGE[0]],
        [FOCUS[0] - WORLD_VIEW_LON_HALF_SPAN, WORLD_VIEW_LAT_RANGE[1]],
        [FOCUS[0] + WORLD_VIEW_LON_HALF_SPAN, WORLD_VIEW_LAT_RANGE[1]],
        [FOCUS[0] + WORLD_VIEW_LON_HALF_SPAN, WORLD_VIEW_LAT_RANGE[0]],
        [FOCUS[0] - WORLD_VIEW_LON_HALF_SPAN, WORLD_VIEW_LAT_RANGE[0]],
      ],
    ],
  },
};

// Le <image> SVG brut (nécessaire pour appliquer la transform affine calculée
// plus bas) ne bloque PAS le rendu Remotion tant qu'il n'est pas chargé,
// contrairement au composant <Img> — bug constaté : au tout premier frame de
// la scène (le cut à 20s), Remotion capturait avant que la texture ait fini
// de décoder, laissant voir un frame quasi vide/glitché. delayRender/
// continueRender force Remotion à attendre le chargement réel avant de
// capturer, exactement comme le fait <Img> en interne.
const useDelayedImagePreload = (src: string) => {
  useEffect(() => {
    const handle = delayRender(`preload-${src}`);
    const img = new Image();
    img.src = src;
    img.onload = () => continueRender(handle);
    img.onerror = () => continueRender(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [src]);
};

export const MapZoomUyuni: React.FC<Props> = ({ countries }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  useDelayedImagePreload(staticFile("desert-sel/map_texture_world.jpg"));

  const renderedFeatures = countries.features.filter((f) => f.id !== WIDE_SHOT_MAX_LATITUDE_ID_EXCLUDE);
  const scaleWide = scaleToFit(WORLD_VIEW_BOX, WIDTH, HEIGHT, FOCUS, SCREEN_TARGET);
  const scaleClose = scaleToFit(localBoxAround(FOCUS, 1.2), WIDTH * 0.6, HEIGHT * 0.3, FOCUS, SCREEN_TARGET);

  const zoomT = interpolate(frame, [0, ZOOM_END], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const scale = scaleWide + (scaleClose - scaleWide) * zoomT;

  const projection = geoMercator().center(FOCUS).translate(SCREEN_TARGET).scale(scale);
  const path = geoPath(projection);

  // La texture (Blue Marble, équirectangulaire : x linéaire en longitude, y
  // linéaire en latitude) doit suivre le même zoom/pan que les frontières
  // vectorielles, sinon les continents affichés par l'image ne correspondent
  // plus aux tracés (bug constaté : Afrique visible sous le contour Bolivie).
  // SVG <image> ne sait faire qu'une transformation AFFINE (pas la vraie
  // déformation non-linéaire du Mercator) : on calcule donc l'affine qui
  // recale exactement l'image sur la projection réelle AUTOUR de FOCUS (2
  // points de repère proches en longitude et en latitude) — précis pile là
  // où ça compte (Bolivie), dérive minime ailleurs, invisible à cette échelle.
  const refA = projection(FOCUS) as [number, number];
  const refLon = projection([FOCUS[0] + 10, FOCUS[1]]) as [number, number];
  const refLat = projection([FOCUS[0], FOCUS[1] + 10]) as [number, number];

  const imgX = (lon: number) => ((lon + 180) / 360) * WORLD_TEXTURE_WIDTH;
  const imgY = (lat: number) => ((90 - lat) / 180) * WORLD_TEXTURE_HEIGHT;

  const textureScaleX = (refLon[0] - refA[0]) / (imgX(FOCUS[0] + 10) - imgX(FOCUS[0]));
  const textureScaleY = (refLat[1] - refA[1]) / (imgY(FOCUS[1] + 10) - imgY(FOCUS[1]));
  const textureTranslateX = refA[0] - textureScaleX * imgX(FOCUS[0]);
  const textureTranslateY = refA[1] - textureScaleY * imgY(FOCUS[1]);

  const bolivia = renderedFeatures.find((f) => f.id === BOLIVIA_ID) ?? null;

  // Halo rouge sur la frontière : intensité qui monte puis pulse doucement
  // (sinus déterministe, pas de hasard) une fois établie — lit "frontière qui
  // s'allume" plutôt qu'un simple à-coup d'opacité.
  const glowRampUp = interpolate(frame, [BORDER_GLOW_START, BORDER_GLOW_START + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const glowPulse = 0.75 + 0.25 * Math.sin((frame - BORDER_GLOW_START) / 9);
  const glowOpacity = glowRampUp * glowPulse;

  const countryLabelOpacity = interpolate(frame, [COUNTRY_LABEL_START, COUNTRY_LABEL_START + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const countryLabelY = interpolate(frame, [COUNTRY_LABEL_START, COUNTRY_LABEL_START + 15], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const pinVisible = frame >= PIN_START;
  const pinProgress = spring({ frame: frame - PIN_START, fps, config: { damping: 12, mass: 0.6 } });

  const labelOpacity = interpolate(frame, [SITE_LABEL_START, SITE_LABEL_START + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const labelY = interpolate(frame, [SITE_LABEL_START, SITE_LABEL_START + 15], [10, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const ctaOpacity = interpolate(frame, [CTA_START, CTA_START + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ctaScale = spring({ frame: frame - CTA_START, fps, config: { damping: 14, mass: 0.6 } });
  const panelOpacity = interpolate(frame, [CTA_START, CTA_START + 15], [0, 0.72], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a1e33" }}>
      <svg width={WIDTH} height={HEIGHT} viewBox={`0 0 ${WIDTH} ${HEIGHT}`}>
        <defs>
          <filter id="border-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Texture monde (NASA Blue Marble, domaine public, Wikimedia),
            recalée sur la projection via l'affine calculée ci-dessus — suit
            le zoom/pan au lieu de rester fixe à l'écran (la version fixe
            précédente affichait de mauvais continents sous les frontières,
            et le calque sombre appliqué en plus rendait tout terne). Cette
            image a déjà la bonne séparation terre/océan/glace en couleurs
            réalistes : plus besoin d'aucune teinte de fond, les pays restent
            seulement contourés (stroke), sans remplissage. */}
        <image
          href={staticFile("desert-sel/map_texture_world.jpg")}
          x={0}
          y={0}
          width={WORLD_TEXTURE_WIDTH}
          height={WORLD_TEXTURE_HEIGHT}
          transform={`translate(${textureTranslateX}, ${textureTranslateY}) scale(${textureScaleX}, ${textureScaleY})`}
        />

        {renderedFeatures.map((f) => (
          <path
            key={f.id as string}
            d={path(f) ?? undefined}
            fill={f.id === BOLIVIA_ID ? "#e8c98a" : "transparent"}
            fillOpacity={f.id === BOLIVIA_ID ? 0.3 : 1}
            stroke="rgba(255,255,255,0.35)"
            strokeWidth={1}
          />
        ))}
        {/* Frontière allumée en rouge — pays identifié avant le pin précis */}
        {bolivia && (
          <path
            d={path(bolivia) ?? undefined}
            fill="none"
            stroke="#ff3b3b"
            strokeWidth={5}
            opacity={glowOpacity}
            filter="url(#border-glow)"
          />
        )}
        {pinVisible && (
          <g transform={`translate(${SCREEN_TARGET[0]}, ${SCREEN_TARGET[1]}) scale(${pinProgress})`}>
            <circle r={14} fill="#e63946" stroke="white" strokeWidth={4} />
            <circle r={4} fill="white" />
          </g>
        )}
      </svg>

      {/* Nom du pays — grand, apparaît quand la frontière s'allume */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: SCREEN_TARGET[1] - 90,
          textAlign: "center",
          opacity: countryLabelOpacity,
          transform: `translateY(${countryLabelY}px)`,
        }}
      >
        <span
          style={{
            fontFamily: "Arial, sans-serif",
            fontWeight: 800,
            fontSize: 68,
            letterSpacing: 4,
            color: "white",
            textShadow: "0 0 18px rgba(255,59,59,0.85), 0 2px 10px rgba(0,0,0,0.6)",
          }}
        >
          {COUNTRY_LABEL_TEXT}
        </span>
      </div>

      {/* Nom du site précis — plus petit, apparaît après le pin */}
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
            fontSize: 44,
            color: "#1d3557",
            background: "white",
            padding: "10px 28px",
            borderRadius: 999,
            boxShadow: "0 4px 14px rgba(0,0,0,0.15)",
          }}
        >
          {SITE_LABEL_TEXT}
        </span>
      </div>

      {/* CTA final — overlay sur la carte, jamais de fondu vers du vide */}
      <AbsoluteFill style={{ backgroundColor: `rgba(10, 30, 51, ${panelOpacity})` }} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          opacity: ctaOpacity,
          transform: `scale(${ctaScale})`,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 28, padding: "0 80px" }}>
          <Img src={staticFile("desert-sel/logo_curio.png")} style={{ width: 180, height: 180, borderRadius: 999 }} />
          <span
            style={{
              fontFamily: "Arial, sans-serif",
              fontWeight: 700,
              fontSize: 46,
              lineHeight: 1.3,
              color: "white",
              textAlign: "center",
              textShadow: "0 2px 10px rgba(0,0,0,0.5)",
            }}
          >
            {CTA_TEXTE}
          </span>
        </div>
      </AbsoluteFill>
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
  const target = geo.features.find((f) => f.id === BOLIVIA_ID) ?? null;

  return {
    durationInFrames: DURATION_FRAMES,
    props: { countries: geo, target },
  };
};

export const MapZoomUyuniComposition: React.FC = () => {
  return (
    <Composition
      id="MapZoomUyuni"
      component={MapZoomUyuni}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      durationInFrames={DURATION_FRAMES}
      defaultProps={{ countries: { type: "FeatureCollection", features: [] }, target: null } as Props}
      calculateMetadata={calculateMetadata}
    />
  );
};
