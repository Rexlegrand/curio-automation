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

// Corps du reel au format « deux carrés » (Curio qui parle en haut,
// illustration en bas), avec raccords animés entre plein écran et deux cartes.
import { DeuxCarresComposition } from "./curio-deux-carres/DeuxCarres";

// Curio découpé qui s'illumine au rythme de la voix (piste 100% locale,
// destinée à remplacer le hook animé Dreamina).
import { SpeakingAvatarComposition } from "./curio-avatar/SpeakingAvatar";

// Reel complet rendu 100% localement (décor + Curio illuminé + sous-titres
// bicolores), sans hook Dreamina.
import { CurioReelComposition } from "./curio-reel/CurioReel";

// Reconstructions de techniques repérées sur la chaîne @craftedbycm
// (une composition par short analysé, cf. motion-catalog.md).
import { VintageTvFrameComposition } from "./craftedbycm/01-VintageTvFrame";
import { CutoutDocComposition } from "./cutout-doc/CutoutDoc";

// Direction motion design retenue parmi les 5 prototypes testés : caméra qui
// se déplace sur une grande surface quadrillée, dézoom final révélant la
// fresque. Les 4 autres prototypes restent en local, non versionnés.
import { CurioCameraJourneyComposition } from "./curio-motion/03-CameraJourney";

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
import { StageDemoComposition } from "./sahara/00-StageDemo";
import { HookComposition } from "./sahara/01-Hook";
import { DeuxMondesComposition } from "./sahara/02-DeuxMondes";
import { DustRouteComposition } from "./sahara/03-DustRoute";
import { CamionsComposition } from "./sahara/04-Camions";
import { DeuxSolsComposition } from "./sahara/05-DeuxSols";
import { RevelationComposition } from "./sahara/06-Revelation";
import { ChuteComposition } from "./sahara/07-Chute";
import { V2OrigineComposition } from "./sahara/v2-Origine";
import { V2AluesComposition } from "./sahara/v2-Algues";
import { Root2Compositions } from "./sahara/Root2";
import { ClipsComposition } from "./sahara/v-Clip";
// Reels de série. Un fichier de compositions par reel, tous bâtis sur les
// composants du sahara paramétrés par props.
import { MariannesCompositions } from "./reels/mariannes";
import { SoleilCompositions } from "./reels/soleil";
import { PoldersCompositions } from "./reels/polders";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MapZoomPinComposition />
      <DeuxCarresComposition />
      <SpeakingAvatarComposition />
      <CurioReelComposition />
      <VintageTvFrameComposition />
      <CutoutDocComposition />
      <CurioCameraJourneyComposition />

      <KenBurnsZoomInComposition />
      <BeforeAfterSlideComposition />
      <PanVerticalComposition />
      <DollyZoomVertigoComposition />
      <TextMaskRevealComposition />

      <VoxLayeredSceneComposition />
      <VoxLayeredScene2Dv2Composition />
      <VoxLayeredScene3DComposition />

      <StageDemoComposition />
      <HookComposition />
      <DeuxMondesComposition />
      <DustRouteComposition />
      <CamionsComposition />
      <DeuxSolsComposition />
      <RevelationComposition />
      <ChuteComposition />

      <V2OrigineComposition />
      <V2AluesComposition />
      <Root2Compositions />
      <ClipsComposition />
      <MariannesCompositions />
      <SoleilCompositions />
      <PoldersCompositions />
    </>
  );
};
