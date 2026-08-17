"""Recherche + téléchargement d'images stock (Pexels, Wikimedia Commons).

Branché dans generators/image_generator.py (étape de décision avant tout
appel GPT Image, illustrations Type A curiosité uniquement) : le résultat
brut d'ici est ensuite filtré sur pertinence (result['title'] contient un
terme clé de la requête) et composé sur le fond cahier Curio par
image_generator._try_stock_search(), jamais utilisé tel quel.

Wikimedia : vérifié dans la doc officielle (mediawiki.org/wiki/API:Search,
API:Etiquette) — aucune clé API requise pour la recherche/téléchargement
anonyme, uniquement un header User-Agent descriptif obligatoire (sinon risque
d'IP-block). Pas de variable d'env Wikimedia pour ce POC.

Pexels : clé requise via variable d'env PEXELS_API_KEY (voir .env.example),
jamais hardcodée. Le champ 'alt' de l'API (texte descriptif généré par
Pexels, ex: "Vertical close-up of a penguin from a low angle, highlighting
its beak and plumage.") est la seule métadonnée textuelle disponible côté
Pexels — il n'y a pas de vrai titre. Utilisé comme result['title'] pour
rester homogène avec Wikimedia (vrai titre de fichier) côté filtrage
pertinence en aval.
"""

import re
from pathlib import Path

import requests
from PIL import Image

from config import ENV

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text):
    """extmetadata Artist/Credit revient parfois en HTML (lien vers la page utilisateur) — texte brut seul utile en métadonnée."""
    if not text:
        return text
    return _HTML_TAG_RE.sub("", text).strip()

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
WIKIMEDIA_USER_AGENT = "CurioAutomationPOC/1.0 (test interne, contact via Benjamin Petry-Hummel)"

# Wikimedia Commons mélange photos, diagrammes, logos, cartes, icônes sous le
# même filetype:bitmap (un PNG de diagramme compte comme "bitmap" au même
# titre qu'une vraie photo). Ces mots-clés sont exclus de la recherche
# (CirrusSearch, opérateur "-terme") ET revérifiés après coup sur le titre/
# les catégories/la description de chaque résultat, au cas où Commons les
# aurait mal catégorisés.
WIKIMEDIA_EXCLUDE_TERMS = [
    "diagram", "chart", "graph", "logo", "icon", "map", "screenshot",
    "poster", "illustration", "drawing", "clipart", "clip art",
    "infographic", "silhouette", "flag", "coat of arms", "emblem",
]


def search_pexels(query, per_page=10, orientation="portrait"):
    api_key = ENV.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY manquante dans .env")

    response = requests.get(
        PEXELS_SEARCH_URL,
        headers={"Authorization": api_key},
        params={"query": query, "per_page": per_page, "orientation": orientation},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = []
    for photo in data.get("photos", []):
        results.append({
            "provider": "pexels",
            "id": str(photo["id"]),
            "url": photo["url"],
            "download_url": photo["src"]["large2x"],
            "title": photo.get("alt"),
            "author": photo.get("photographer"),
            "author_url": photo.get("photographer_url"),
            "width": photo.get("width"),
            "height": photo.get("height"),
        })
    return results


def _wikimedia_exclude_clause(term):
    # CirrusSearch : "-mot1 mot2" exclut mot1 mais exige mot2 comme terme
    # positif séparé — un terme d'exclusion à plusieurs mots doit être cité
    # ("-\"coat of arms\"") pour rester une seule négation groupée.
    return f'-"{term}"' if " " in term else f"-{term}"


def _wikimedia_query_string(query, phrase):
    exclude = " ".join(_wikimedia_exclude_clause(term) for term in WIKIMEDIA_EXCLUDE_TERMS)
    core = f'"{query}"' if phrase else query
    # filemime:image/jpeg exclut les PNG/SVG (très majoritairement diagrammes,
    # logos, cartes, captures d'écran sur Commons) — garde le format quasi
    # systématique des vraies photos.
    return f"{core} filetype:bitmap filemime:image/jpeg {exclude}"


def _wikimedia_raw_search(query_string, limit):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query_string,
        "gsrnamespace": 6,  # namespace File:
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime",
    }
    response = requests.get(
        WIKIMEDIA_API_URL,
        headers={"User-Agent": WIKIMEDIA_USER_AGENT},
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("query", {}).get("pages", {})


def _wikimedia_is_real_photo(title, info, extmeta):
    if info.get("mime") != "image/jpeg":
        return False
    haystack = " ".join([
        title,
        extmeta.get("ObjectName", {}).get("value", ""),
        extmeta.get("Categories", {}).get("value", ""),
        extmeta.get("ImageDescription", {}).get("value", ""),
    ]).lower()
    return not any(term in haystack for term in WIKIMEDIA_EXCLUDE_TERMS)


def search_wikimedia(query, limit=10):
    # Phrase exacte d'abord (précision) ; repli sur les mots libres si trop
    # peu de résultats (la phrase exacte est parfois trop stricte sur Commons,
    # dont l'indexation des titres/descriptions est inégale).
    pages = _wikimedia_raw_search(_wikimedia_query_string(query, phrase=True), limit * 2)
    if len(pages) < 3:
        pages = _wikimedia_raw_search(_wikimedia_query_string(query, phrase=False), limit * 2)

    results = []
    for page in pages.values():
        infos = page.get("imageinfo")
        if not infos:
            continue
        info = infos[0]
        extmeta = info.get("extmetadata", {})
        title = page.get("title", "").removeprefix("File:")
        if not _wikimedia_is_real_photo(title, info, extmeta):
            continue
        results.append({
            "provider": "wikimedia",
            "id": str(page.get("pageid")),
            "url": "https://commons.wikimedia.org/wiki/" + page.get("title", "").replace(" ", "_"),
            "download_url": info["url"],
            "title": title,
            "author": _strip_html(extmeta.get("Artist", {}).get("value")),
            "author_url": None,
            "width": info.get("width"),
            "height": info.get("height"),
        })
        if len(results) >= limit:
            break
    return results


PROVIDERS = {
    "pexels": search_pexels,
    "wikimedia": search_wikimedia,
}


def image_search(provider, query, **options):
    """image_search(provider, query, **options) -> liste de résultats bruts (métadonnées, pas encore téléchargés)."""
    if provider not in PROVIDERS:
        raise ValueError(f"Provider inconnu : {provider} (disponibles : {list(PROVIDERS)})")
    return PROVIDERS[provider](query, **options)


def select_best(results):
    """Sélection MVP : privilégie le format portrait (9:16), puis la plus grande hauteur."""
    candidates = [r for r in results if r.get("width") and r.get("height")]
    if not candidates:
        raise ValueError("Aucun résultat exploitable (dimensions manquantes)")
    portrait = [r for r in candidates if r["height"] > r["width"]]
    pool = portrait if portrait else candidates
    return max(pool, key=lambda r: r["height"])


def download_image(result, dest_path):
    """Télécharge result['download_url'] vers dest_path, retourne les métadonnées exploitables."""
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": WIKIMEDIA_USER_AGENT} if result["provider"] == "wikimedia" else {}
    response = requests.get(result["download_url"], headers=headers, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)

    # Dimensions réelles du fichier téléchargé, pas celles annoncées par l'API :
    # l'URL Pexels src.large2x embarque des params de resize (w/h/dpr) qui ne
    # correspondent pas à la résolution originale renvoyée par /v1/search.
    with Image.open(dest_path) as img:
        actual_width, actual_height = img.size

    return {
        "provider": result["provider"],
        "source_url": result["url"],
        "download_url": result["download_url"],
        "title": result.get("title"),
        "author": result.get("author"),
        "local_path": str(dest_path),
        "width": actual_width,
        "height": actual_height,
        "size_bytes": dest_path.stat().st_size,
    }
