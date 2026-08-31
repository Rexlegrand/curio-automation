import "./index.css";
import { TikTokCaptionsComposition } from "./tiktok-captions/TikTokCaptions";

// Root de PRODUCTION — volontairement minimal.
//
// Seule TikTokCaptions est enregistrée ici : c'est la seule composition
// consommée par le pipeline (generators/video_assembler.py, constante
// REMOTION_COMPOSITION). Ce fichier ne doit importer QUE des modules
// versionnés dans le repo et QUE des dépendances non optionnelles, pour
// qu'un clone neuf puisse rendre les sous-titres sans installer quoi que ce
// soit de plus.
//
// Tout le reste (prototypes, motion design, tests) vit dans
// Root.experiments.tsx, servi par une entrée séparée — voir
// docs/EXPERIMENTS.md. Ne jamais rajouter d'import de prototype ici : un
// import cassé dans ce fichier casse le build Remotion, donc l'incrustation
// des sous-titres, donc tout le montage.

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <TikTokCaptionsComposition />
    </>
  );
};
