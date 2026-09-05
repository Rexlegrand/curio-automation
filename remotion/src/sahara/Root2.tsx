import React from "react";
import { Composition } from "remotion";
import { Camions } from "./04-Camions";
import { DustRoute } from "./03-DustRoute";
import { DeuxSols } from "./05-DeuxSols";
import { Chute } from "./07-Chute";
import { FPS, W, H } from "./shared";
import { DUREES2, V2_CHIFFRE, V2_VOYAGE, V2_PHOSPHORE, V2_CHUTE } from "./timing2";

// Compositions du SECOND montage. Elles réutilisent les composants du premier,
// paramétrés par props : la flotte de camions, le globe, le diptyque des sols
// et la chute sont les mêmes objets, avec d'autres durées, un autre calage et
// d'autres fenêtres pour Curio. Dupliquer les fichiers aurait dupliqué la
// flotte instanciée, son bruit déterministe et les réglages de brume — et
// garanti qu'un correctif n'atteigne jamais qu'une moitié du travail.
//
// Les deux beats propres au second montage — l'origine et les algues — ont
// leurs propres fichiers, v2-Origine.tsx et v2-Algues.tsx : ils n'ont pas
// d'équivalent dans le premier.

export const Root2Compositions: React.FC = () => (
  <>
    <Composition
      id="sahara2-01-chiffre"
      component={Camions}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES2.chiffre}
      defaultProps={{
        duration: DUREES2.chiffre,
        numberIn: V2_CHIFFRE.numberIn,
        segment: "mots2/01-chiffre",
        curio: V2_CHIFFRE.curio,
      }}
    />
    <Composition
      id="sahara2-04-voyage"
      component={DustRoute}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES2.voyage}
      defaultProps={{ duration: DUREES2.voyage, segment: "mots2/04-voyage", ...V2_VOYAGE }}
    />
    <Composition
      id="sahara2-05-phosphore"
      component={DeuxSols}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES2.phosphore}
      defaultProps={{
        duration: DUREES2.phosphore,
        segment: "mots2/05-phosphore",
        wordIn: V2_PHOSPHORE.wordIn,
        split: V2_PHOSPHORE.split,
        rainFrom: V2_PHOSPHORE.rainFrom,
        curio: V2_PHOSPHORE.curio,
      }}
    />
    <Composition
      id="sahara2-06-chute"
      component={Chute}
      fps={FPS}
      width={W}
      height={H}
      durationInFrames={DUREES2.chute}
      defaultProps={{ duration: DUREES2.chute, segment: "mots2/06-chute", cut: V2_CHUTE.cut }}
    />
  </>
);
