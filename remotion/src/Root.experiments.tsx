import "./index.css";

// Root des EXPÉRIMENTATIONS — entrée séparée de la production.
//
//   npx remotion studio src/index.experiments.ts
//   npx remotion render src/index.experiments.ts <CompositionId> <sortie.mp4>
//
// Rien de ce qui est enregistré ici n'est utilisé par le pipeline de
// production : `generators/video_assembler.py` passe par src/index.ts, qui ne
// connaît que TikTokCaptions. On peut donc casser ce fichier sans casser la
// génération de reels.
//
// Contrainte à respecter : n'importer ici que des modules RÉELLEMENT versionnés
// dans le repo. Les prototypes gardés en local uniquement (remotion/src/curio-motion/,
// remotion/src/browser-search-cta/) sont volontairement absents — les
// enregistrer ici casserait le build sur un clone neuf.
//
// VoxLayeredScene3D dépend des paquets 3D déclarés en optionalDependencies
// (three, @react-three/fiber, @react-three/drei, @remotion/three). Sur une
// installation faite avec `npm install --omit=optional`, retirer son import
// ci-dessous. Détails dans docs/EXPERIMENTS.md.

import { MapZoomPinComposition } from "./map-zoom/MapZoomPin";
import { CutoutDocComposition } from "./cutout-doc/CutoutDoc";

// Techniques de caméra du motion-catalog (une composition par technique)
import { KenBurnsZoomInComposition } from "./camera-techniques/KenBurnsZoomIn";
import { BeforeAfterSlideComposition } from "./camera-techniques/BeforeAfterSlide";
import { PanVerticalComposition } from "./camera-techniques/PanVertical";
import { DollyZoomVertigoComposition } from "./camera-techniques/DollyZoomVertigo";
import { TextMaskRevealComposition } from "./camera-techniques/TextMaskReveal";

// Scènes « Vox » en couches
import { VoxLayeredSceneComposition } from "./vox-test/VoxLayeredScene";
import { VoxLayeredScene2Dv2Composition } from "./vox-test/VoxLayeredScene2D_v2";
import { VoxLayeredScene3DComposition } from "./vox-test/VoxLayeredScene3D";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MapZoomPinComposition />
      <CutoutDocComposition />

      <KenBurnsZoomInComposition />
      <BeforeAfterSlideComposition />
      <PanVerticalComposition />
      <DollyZoomVertigoComposition />
      <TextMaskRevealComposition />

      <VoxLayeredSceneComposition />
      <VoxLayeredScene2Dv2Composition />
      <VoxLayeredScene3DComposition />
    </>
  );
};
