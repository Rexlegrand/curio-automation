import "./index.css";
import { TikTokCaptionsComposition } from "./tiktok-captions/TikTokCaptions";
import { MapZoomPinComposition } from "./map-zoom/MapZoomPin";
import { BrowserSearchCTAComposition } from "./browser-search-cta/BrowserSearchCTA";
import { CurioPageFlipComposition } from "./curio-motion/01-PageFlip";
import { CurioFlipbookComposition } from "./curio-motion/02-Flipbook";
import { CurioCameraJourneyComposition } from "./curio-motion/03-CameraJourney";
import { CurioPageRevealComposition } from "./curio-motion/04-PageReveal";
import { CurioChaosToNotebookComposition } from "./curio-motion/05-ChaosToNotebook";
import { CutoutDocComposition } from "./cutout-doc/CutoutDoc";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <TikTokCaptionsComposition />
      <MapZoomPinComposition />
      <BrowserSearchCTAComposition />
      <CurioPageFlipComposition />
      <CurioFlipbookComposition />
      <CurioCameraJourneyComposition />
      <CurioPageRevealComposition />
      <CurioChaosToNotebookComposition />
      <CutoutDocComposition />
    </>
  );
};
