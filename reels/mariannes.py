"""Reel 1 de la série — « la fosse des Mariannes ».

Deck des curiosités, ligne 92 : « L'endroit le plus profond de l'océan fait
près de 11 kilomètres. » Mécanique « Record ».

Structure calquée sur `reel_sahara` : hook, deux mondes opposés, mécanisme,
chiffre massif visualisé, conséquence, révélation d'origine, chute qui
retourne le hook.

Le beat-chiffre est celui de l'Everest englouti — l'équivalent des vingt-sept
millions de tonnes du sahara : un ordre de grandeur qu'on ne peut pas se
représenter, ramené à un objet qu'on connaît.

Exactitude, vérifiée le 2026-09-03 :
  - Challenger Deep : ~10 935 m, d'où « près de onze kilomètres » ;
  - Everest : 8 849 m. 10 935 - 8 849 = 2 086 m, d'où « deux kilomètres
    d'eau au-dessus du sommet » ;
  - la couleur s'efface vers 200 m, l'obscurité est totale sous 1 000 m ;
  - pression au fond ~1 086 bar, soit ~1 071 fois celle de la surface, d'où
    « mille fois » ; la comparaison des cinquante avions est celle retenue
    par la NOAA ;
  - poisson-limace filmé à 8 336 m dans la fosse d'Izu-Ogasawara en 2022,
    d'où « on en a filmé à plus de huit mille mètres ».
"""

from reels import Reel

REEL = Reel(
    slug="mariannes",
    titre="La fosse des Mariannes",
    # La ponctuation est hachée volontairement — points de suspension, phrases
    # courtes. eleven_v3 la suit de près, c'est le seul levier pour faire
    # respirer la voix et empêcher le montage de couper sec.
    segments=[
        # Repris MOT POUR MOT du lip-sync Dreamina : la piste native du hook
        # n'est jamais montée, c'est cette voix-ci qu'on entend (règle v2.15).
        ("00-hook", "Attends... une montagne entière tiendrait là-dedans ?"),
        ("01-hook-suite",
         "L'endroit le plus profond de la Terre... est si creux "
         "qu'on pourrait y faire disparaître l'Everest."),
        ("02-deux-mondes",
         "D'un côté, la surface. Le soleil, les vagues. "
         "De l'autre... onze kilomètres plus bas. La fosse des Mariannes."),
        ("03-descente",
         "Tu descends. À deux cents mètres... les couleurs disparaissent. "
         "À mille... il fait nuit noire. Et tu n'es qu'au dixième du chemin."),
        ("04-chiffre",
         "Onze kilomètres. Pose l'Everest tout au fond... "
         "et il reste encore deux kilomètres d'eau au-dessus du sommet."),
        ("05-pression",
         "Là-bas, l'eau écrase tout. Mille fois la pression de la surface. "
         "L'équivalent... de cinquante avions posés sur toi."),
        ("06-revelation",
         "Et pourtant... il y a de la vie. Des poissons transparents. "
         "Des bêtes qui n'ont jamais vu le jour. "
         "On en a filmé à plus de huit mille mètres."),
        ("07-chute",
         "L'endroit le plus noir de la planète... "
         "n'est pas un endroit mort."),
        # Le CTA écrit porte une barre oblique (« une activité/un exercice »)
        # qu'ElevenLabs lit comme une syllabe parasite : ce qui est DIT s'en
        # passe.
        ("08-cta", "Envoie CURIO en MP pour recevoir une activité gratuite !"),
    ],
    corrections={
        "curieux": "CURIO",
        "curio": "CURIO",
        "mariane": "Mariannes",
        "marianne": "Mariannes",
        "mariannes": "Mariannes",
        "everest": "Everest",
    },
    # « est si creux » : Whisper entend « et ». Le mot est juste partout
    # ailleurs, la correction est donc locale à ce segment.
    corrections_segment={"01-hook-suite": {"et": "est"}},
    # Les plans plein cadre. Style commun : rendu 3D peint, pas photo — même
    # registre que les plans du sahara, pour que les deux reels ne parlent pas
    # deux langues visuelles. Cadrage vertical, et pour les plans qui portent
    # un titre, du vide en haut.
    images={
        "surface": (
            "Ocean surface seen from just below the waterline, bright turquoise "
            "water, sunlight breaking through the swell into visible god rays, "
            "small bubbles rising, warm and alive. Empty open water in the upper "
            "third of the frame. Painted 3D render, cinematic, no text, no "
            "characters, no boats. Vertical 9:16."
        ),
        "abysse": (
            "The deep ocean abyss, almost total darkness, a single faint cold "
            "blue glow far above dying out into black, suspended white marine "
            "snow particles drifting. Empty, vast, silent. Painted 3D render, "
            "cinematic, no text, no creatures. Vertical 9:16."
        ),
        "particules": (
            "Marine snow: hundreds of small white and pale grey organic "
            "particles of different sizes drifting in water, isolated on a pure "
            "black background, soft focus on the nearest ones. No text. "
            "Horizontal frame."
        ),
        "penombre": (
            "The ocean twilight zone at two hundred metres deep, deep indigo "
            "blue water, the last of the daylight fading from the top of the "
            "frame, colours almost gone, a few particles catching the dim light. "
            "Painted 3D render, cinematic, no text, no creatures. Vertical 9:16."
        ),
        "fond_fosse": (
            "The floor of a deep ocean trench: pale grey-beige fine sediment "
            "stretching away, gentle ripples, a few scattered small rocks, lit "
            "by a single cold artificial light from above that falls off into "
            "black. Painted 3D render, cinematic, no text, no creatures. "
            "Vertical 9:16."
        ),
        "poisson": (
            "A small translucent pink-white deep sea snailfish with a soft "
            "tadpole-shaped body, large delicate fins and tiny eyes, hovering "
            "just above pale grey sediment in a cold beam of light, everything "
            "behind it pure black. Painted 3D render, scientific but warm, no "
            "text. Vertical 9:16."
        ),
        "gobelet_avant": (
            "A single plain white polystyrene foam cup, standing upright, "
            "isolated on a pure black background, evenly lit, seen from the "
            "side, full normal size. Product photograph look, sharp, no text, "
            "no logo. Horizontal frame."
        ),
        "gobelet_apres": (
            "A single plain white polystyrene foam cup that has been crushed "
            "and shrunk by deep sea pressure to about one third of its size, "
            "wrinkled and dense but still cup-shaped, standing upright, "
            "isolated on a pure black background, evenly lit, seen from the "
            "side, exactly the same camera angle and lighting as a normal cup. "
            "Product photograph look, sharp, no text, no logo. Horizontal frame."
        ),
    },
)
