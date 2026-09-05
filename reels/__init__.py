"""Specs des reels produits en série.

Un module par reel. Le sahara, lui, garde ses scripts dédiés
(`gen_narration_sahara.py`, `build_reel_sahara.py`, ...) : il a servi de
prototype et rien ne gagne à le réécrire — mais tout ce qui suit en est la
généralisation, script pour script.

Un spec décrit UNIQUEMENT ce qui change d'un reel à l'autre : la narration
segment par segment, le plan vidéo qui porte chaque segment, et les
corrections d'orthographe à appliquer à la sortie de Whisper. Le reste — la
voix, la pause, le format, le style des sous-titres — est commun et vit dans
les scripts.
"""

from dataclasses import dataclass, field
from importlib import import_module


@dataclass(frozen=True)
class Reel:
    slug: str
    titre: str
    # (clé de segment, texte dit). La clé nomme le mp3, le JSON de mots et la
    # composition Remotion — un seul nom du début à la fin de la chaîne.
    segments: list
    # Corrections Whisper globales. Clé : ce que Whisper écrit, en minuscules
    # sans ponctuation. Valeur : ce qui est réellement dit, ou None pour
    # fusionner le mot dans le précédent.
    corrections: dict = field(default_factory=dict)
    # Corrections qui ne valent que dans un segment donné.
    corrections_segment: dict = field(default_factory=dict)
    # Images à générer : nom de fichier -> prompt GPT Image 2. Le nom sert
    # aussi de nom d'asset côté Remotion (public/reels/<slug>/<nom>.jpg).
    images: dict = field(default_factory=dict)
    # Images reprises telles quelles d'une source libre : nom -> (url, crédit).
    sources_libres: dict = field(default_factory=dict)
    # Plans à détourer en PNG alpha plutôt qu'à aplatir en JPEG. Réservé aux
    # objets instanciés en 3D : le matériau utilise `alphaTest`, un fond
    # opaque ferait des vignettes carrées.
    decoupe: tuple = ()

    @property
    def cles(self) -> list:
        return [k for k, _ in self.segments]


def charger(slug: str) -> Reel:
    try:
        return import_module(f"reels.{slug}").REEL
    except ModuleNotFoundError:
        raise SystemExit(f"reel inconnu : {slug} (attendu reels/{slug}.py)")
