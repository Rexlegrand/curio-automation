import "./index.css";
import { TikTokCaptionsComposition } from "./tiktok-captions/TikTokCaptions";
import { MapZoomPinComposition } from "./map-zoom/MapZoomPin";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <TikTokCaptionsComposition />
      <MapZoomPinComposition />
    </>
  );
};
