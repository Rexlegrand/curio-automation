"""Reel 2 de la série — « le Soleil, c'est presque tout le système solaire ».

Deck des curiosités, ligne 17. Mécanique « Record ».

Même structure que `reel_sahara` et que le reel 1 : hook, deux mondes opposés,
mécanisme, chiffre massif visualisé, conséquence, révélation, chute qui
retourne le hook.

Le beat-chiffre est celui du million trois cent mille Terres. Il réutilise tel
quel le composant de la flotte de camions du sahara : un champ d'objets
identiques qui fuit vers l'horizon jusqu'à ce que le cadre n'en montre plus la
fin. C'est la même idée — un nombre qu'on ne peut pas se représenter, rendu
visible par l'étendue et non par les chiffres.

Exactitude, vérifiée le 2026-09-03 :
  - le Soleil représente 99,86 % de la masse du système solaire, d'où
    « quatre-vingt-dix-neuf virgule huit » (arrondi par défaut) ;
  - environ 1,3 million de Terres tiennent dans son volume ;
  - Jupiter pèse 1/1047 de la masse du Soleil, d'où « mille fois moins », et
    représente à elle seule ~71 % de la masse de toutes les planètes, d'où
    « les deux tiers » (formulation prudente) ;
  - le Soleil est une naine jaune, étoile de type G de la séquence
    principale ; les plus grandes étoiles connues dépassent 1 500 fois son
    rayon, d'où « mille fois plus larges ».
"""

from reels import Reel

REEL = Reel(
    slug="soleil",
    titre="Le Soleil, c'est presque tout",
    segments=[
        # Repris MOT POUR MOT du lip-sync Dreamina (règle v2.15).
        ("00-hook", "Attends... toutes les planètes réunies, c'est que des miettes ?"),
        ("01-hook-suite",
         "Le système solaire... c'est le Soleil. Et presque rien d'autre."),
        ("02-deux-mondes",
         "D'un côté, huit planètes. Des lunes, des astéroïdes, des comètes. "
         "De l'autre... une seule étoile."),
        ("03-balance",
         "Mets tout ça sur une balance. Le Soleil pèse "
         "quatre-vingt-dix-neuf virgule huit pour cent du total. "
         "Tout le reste... c'est zéro virgule deux."),
        ("04-chiffre",
         "Et à l'intérieur du Soleil... "
         "tu pourrais ranger un million trois cent mille Terres."),
        ("05-jupiter",
         "Jupiter est la plus grosse planète. "
         "Elle pèse mille fois moins que le Soleil. "
         "Et à elle seule... elle fait les deux tiers de toutes les planètes."),
        ("06-revelation",
         "Et pourtant... le Soleil n'est même pas une grosse étoile. "
         "C'est une naine jaune. Une étoile banale. "
         "Il en existe de mille fois plus larges."),
        ("07-chute",
         "L'astre qui écrase tout notre système... "
         "est une étoile ordinaire."),
        ("08-cta", "Envoie CURIO en MP pour recevoir une activité gratuite !"),
    ],
    corrections={
        "curieux": "CURIO",
        "curio": "CURIO",
        "jupiter": "Jupiter",
        "terres": "Terres",
        "soleil": "Soleil",
    },
    corrections_segment={},
    # La Terre est instanciée des centaines de fois en 3D : elle a besoin
    # d'un alpha, pas d'un fond.
    decoupe=("terre",),
    images={
        "planetes": (
            "The eight planets of the solar system lined up side by side "
            "against deep black space, correct relative sizes, Jupiter and "
            "Saturn largest, Earth small and blue, soft rim lighting from the "
            "left. Painted 3D render, cinematic, no text, no labels, no orbit "
            "lines. Vertical 9:16."
        ),
        "soleil_plein": (
            "The surface of the Sun filling the entire frame, seething orange "
            "and yellow plasma granulation, dark sunspots, bright flares "
            "curling at the edge, intense glow. Painted 3D render, cinematic, "
            "no text, no planets. Vertical 9:16."
        ),
        "soleil_disque": (
            "The whole Sun as a single glowing orange sphere centred against "
            "pure black empty space, seen from far away, soft corona halo "
            "around it, nothing else in frame. Painted 3D render, cinematic, "
            "no text, no planets, no stars. Vertical 9:16."
        ),
        "granulation": (
            "Extreme close-up of the Sun's photosphere granulation: a mosaic "
            "of bright convection cells separated by dark lanes, glowing "
            "orange and white, filling the whole frame. Scientific look, "
            "painted 3D render, no text. Vertical 9:16."
        ),
        "geante_rouge": (
            "A colossal deep red supergiant star filling most of the frame "
            "against black space, and beside it, for scale, a tiny yellow dot "
            "barely visible. Painted 3D render, cinematic, dramatic scale "
            "difference, no text, no labels. Vertical 9:16."
        ),
        "jupiter": (
            "The planet Jupiter alone, isolated on a pure black background, "
            "its banded orange and cream cloud belts and the Great Red Spot "
            "clearly visible, lit from the left. Painted 3D render, no text, "
            "no moons, no stars. Horizontal frame."
        ),
        # Détourée ensuite : elle est instanciée des centaines de fois en 3D au
        # beat du chiffre, exactement comme le camion du sahara.
        "terre": (
            "The planet Earth as a single complete sphere, seen from space, "
            "blue oceans, white clouds, green continents, lit from the left "
            "with a crescent of night on the right, isolated on a pure WHITE "
            "background, centred, nothing else in frame. Painted 3D render, "
            "no text, no stars, no atmosphere glow. Horizontal frame."
        ),
    },
)
