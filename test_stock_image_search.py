"""Test manuel POC — recherche + téléchargement d'image stock (Pexels / Wikimedia).

Isolé du pipeline réel. Ne touche à rien dans output/. Sauvegarde dans
testing_stock_images/.

Usage :
    python test_stock_image_search.py "child playing football"
    python test_stock_image_search.py "école enfant" wikimedia
"""

import sys
from pathlib import Path

from generators.stock_image_search import download_image, image_search, select_best

OUTPUT_DIR = Path(__file__).resolve().parent / "testing_stock_images"


def run_test(query, provider="pexels"):
    print(f"1. Appel API {provider} — requête : \"{query}\"")
    options = {"orientation": "portrait"} if provider == "pexels" else {}
    results = image_search(provider, query, **options)

    print(f"2. {len(results)} résultat(s) reçu(s)")
    for r in results:
        print(f"   - id={r['id']} {r['width']}x{r['height']} auteur={r.get('author')}")

    if not results:
        print("Aucun résultat, arrêt.")
        return None

    best = select_best(results)
    print(f"3. Sélection : id={best['id']} ({best['width']}x{best['height']}) auteur={best.get('author')}")

    dest = OUTPUT_DIR / f"{provider}_{best['id']}.jpg"
    meta = download_image(best, dest)
    print(f"4. Téléchargée localement : {meta['local_path']} ({meta['size_bytes']} octets)")

    print("5. Métadonnées exploitables par le workflow :")
    for key, value in meta.items():
        print(f"   {key}: {value}")

    return meta


if __name__ == "__main__":
    query_arg = sys.argv[1] if len(sys.argv) > 1 else "child playing football"
    provider_arg = sys.argv[2] if len(sys.argv) > 2 else "pexels"
    run_test(query_arg, provider_arg)
