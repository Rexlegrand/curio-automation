"""Reel 3 de la série — « une partie des Pays-Bas a été prise à la mer ».

Deck des curiosités, ligne 116. Mécanique « Waouh contre-intuitif ».

Même structure que le sahara et que les deux reels précédents. Ce reel est
celui qui réutilise le plus : SEPT beats sur sept sortent de composants
existants, aucun n'est neuf. Le beat de la proportion vient de `Proportion`,
écrit pour le reel 2 et rangé dans `reels/commun/` précisément pour ça.

Le beat-chiffre est de nouveau la flotte du sahara, avec une ferme
néerlandaise à la place du camion : ce qui a été construit sur l'ancien fond
marin, à perte de vue.

Exactitude, vérifiée le 2026-09-03 :
  - l'Afsluitdijk mesure 32 km et a été achevée en 1932 ;
  - les polders du Zuiderzee totalisent environ 1 650 km² — « près de mille
    cinq cents » est une formulation prudente ;
  - Paris fait 105 km², d'où « quatorze fois la surface de Paris »
    (1 500 / 105 = 14,3) ;
  - environ 26 % du territoire est sous le niveau de la mer, d'où « un quart » ;
  - le Flevoland est sorti de l'eau en 1968 et est devenu province en 1986.
"""

from reels import Reel

REEL = Reel(
    slug="polders",
    titre="Les Pays-Bas pris à la mer",
    segments=[
        # Repris MOT POUR MOT du lip-sync Dreamina (règle v2.15).
        ("00-hook", "Attends... ils ont pris leur pays à la mer ?"),
        ("01-hook-suite",
         "Une grande partie des Pays-Bas... était au fond de l'eau."),
        ("02-deux-mondes",
         "D'un côté, la mer du Nord. "
         "De l'autre... des champs, des routes, des villes. Au même endroit."),
        ("03-digue",
         "D'abord, une digue. Trente-deux kilomètres de mur... "
         "qui ferment la baie. Puis des pompes. Pendant des années."),
        ("04-chiffre",
         "Résultat : près de mille cinq cents kilomètres carrés sortis de "
         "l'eau. Quatorze fois la surface de Paris."),
        ("05-niveau",
         "Sans ces digues... la mer reprendrait tout. "
         "Les pompes, elles, ne s'arrêtent jamais."),
        ("06-revelation",
         "Aujourd'hui... un quart du pays est sous le niveau de la mer. "
         "Et une province entière est posée sur l'ancien fond marin. "
         "Le Flevoland."),
        ("07-chute",
         "Il existe un pays où l'on marche... là où nageaient les poissons."),
        ("08-cta", "Envoie CURIO en MP pour recevoir une activité gratuite !"),
    ],
    corrections={
        "curieux": "CURIO",
        "curio": "CURIO",
        "flevoland": "Flevoland",
        "paris": "Paris",
    },
    # « au fond de l'eau » : Whisper entend « l'euro », et le coupe en deux
    # jetons — « l » puis « 'euro. ». La correction porte donc sur le second,
    # et sa valeur commence par une apostrophe : elle est alors recollée au
    # mot précédent, ce qui redonne « l'eau ».
    corrections_segment={"01-hook-suite": {"'euro": "'eau"}},
    # La ferme est instanciée des centaines de fois en 3D : elle a besoin d'un
    # alpha, pas d'un fond.
    decoupe=("ferme",),
    images={
        "mer_du_nord": (
            "The grey-green North Sea seen from just above the waves, choppy "
            "water stretching to a flat horizon under a heavy overcast sky, "
            "cold northern light, empty. Painted 3D render, cinematic, no "
            "text, no boats, no land. Vertical 9:16."
        ),
        "polder_champs": (
            "A flat Dutch polder landscape at ground level: geometric green "
            "fields divided by straight drainage canals, a row of poplars, a "
            "farmhouse in the distance, big cloudy sky taking the upper half "
            "of the frame. Painted 3D render, cinematic, no text. "
            "Vertical 9:16."
        ),
        "carte_zuiderzee": (
            "Satellite view from orbit of the Netherlands and the IJsselmeer, "
            "the North Sea on the left, the great enclosing dyke visible as a "
            "thin straight line across the bay, green polders inland, "
            "realistic satellite imagery look, slight cloud cover. No text, "
            "no labels, no borders. Vertical 9:16."
        ),
        "digue": (
            "Aerial view of a long perfectly straight sea dyke running from "
            "the foreground to the horizon, dark rough sea on the left, calm "
            "flat water on the right, a road along its top, overcast northern "
            "sky. Painted 3D render, cinematic, no text. Vertical 9:16."
        ),
        "polder_sec": (
            "A dry Dutch polder seen from ground level: green pasture, a "
            "straight canal, a small farm, and a high grass dyke wall rising "
            "on the right side holding back water above field level. Painted "
            "3D render, cinematic, no text. Horizontal frame."
        ),
        "polder_noye": (
            "The exact same flat Dutch polder landscape, same camera angle "
            "and same light, but completely flooded: grey water covering the "
            "fields up to the rooftops, only the top of a farm and a line of "
            "trees emerging. Painted 3D render, cinematic, no text. "
            "Horizontal frame."
        ),
        "flevoland": (
            "Aerial view of a modern Dutch polder province: perfectly "
            "rectangular green and brown farm plots in a grid, straight "
            "canals and roads, a small new town with red roofs, wind "
            "turbines in a line. Painted 3D render, cinematic, no text. "
            "Vertical 9:16."
        ),
        # Détourée ensuite : instanciée des centaines de fois au beat 4.
        "ferme": (
            "A single small traditional Dutch farmhouse with a steep red "
            "tiled roof, white walls and green shutters, seen straight from "
            "the side at eye level, isolated on a pure WHITE background, "
            "nothing else in frame, no ground, no shadow. Painted 3D render, "
            "no text. Horizontal frame."
        ),
    },
)
