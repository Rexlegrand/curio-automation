"""Génération des 5 images PNG — GPT Image 2, code_render (ADDENDUM v2.6), asset_copy (v2.11)
ou stock_search (Pexels/Wikimedia, NOUVEAU).

Routage par image : hook_frame reste GPT Image 2 uniquement pour les Reels
curiosité (le fond thématique doit varier selon le sujet) ; pour un Reel
compétence (français ET maths), hook_frame.png est copié depuis un asset fixe
(assets/hook_frames/) — zéro appel API, zéro régénération (v2.11 §hook frame
compétence). La miniature reste toujours GPT Image 2 (Curio y apparaît, pas
de calcul à représenter). Les 3 illustrations d'un Reel compétence maths
passent par generators/math_renderers/ (0€, 0 risque de chiffre halluciné)
quand script["image_route"] == "code_render" ; sinon comportement GPT Image 2
existant, inchangé.

NOUVEAU — recherche stock avant GPT Image (illustrations Type A curiosité
uniquement) : hook_frame/miniature/Type B gardent toujours GPT Image 2 (texte,
schéma ou personnage Curio requis — non transférable à une photo stock). Pour
une illustration curiosité dont la description ne mentionne ni texte, ni
schéma, ni Curio, le pipeline tente d'abord Pexels puis Wikimedia Commons
(generators/stock_image_search.py, 0€, 0 appel GPT Image) sur stock_query_en
(champ anglais rédigé par Claude dans le même appel que le reste du script,
script_generator.py). Un résultat n'est accepté que si son titre/texte
descriptif (result["title"] — alt Pexels ou vrai titre de fichier Wikimedia)
contient au moins un terme clé de la requête (§ validé sur le terrain le
17/08 : un premier essai "tout résultat non vide accepté" avait laissé passer
un manchot à crête au premier plan sur une requête "emperor penguin..." — le
mot générique "penguin" seul dans le titre reste une limite connue de ce
filtre, à resserrer si le problème se reproduit). Aucun résultat pertinent
sur les deux sources gratuites → bascule sur GPT Image 2. La photo stock
retenue est composée sur le fond cahier Curio (generators/math_renderers/compose.py,
même compositing que le rendu code — bordure magazine-clip, rotation
aléatoire, 30% de zone basse vide pour les sous-titres) : jamais utilisée
brute, pour respecter la charte graphique (CLAUDE.md §5) au même titre que
toute autre illustration.
"""

import base64
import re
import shutil
from contextlib import ExitStack

from openai import BadRequestError, OpenAI
from PIL import Image

from config import (
    COST_IMAGE,
    ENV,
    HOOK_FRAME_FRANCAIS,
    HOOK_FRAME_MATHS,
    IMAGE_SIZE,
    IMAGE_SIZE_FALLBACK,
    LOGO_PATH,
    OPENAI_IMAGE_MODEL,
    REFERENCE_DIR,
    check_references,
    log_api_call,
)
from generators import stock_image_search
from generators.math_renderers import addition_colonnes, astuce_chaine, division_posee, multiplication_posee, soustraction_colonnes
from generators.math_renderers.compose import compose_illustration
from prompts import competence_prompts, curiosity_prompts

QUALITY_STANDARD = "medium"
QUALITY_HIGH = "high"

MATH_RENDERERS = {
    "division_posee": division_posee.render,
    "soustraction_colonnes": soustraction_colonnes.render,
    "addition_colonnes": addition_colonnes.render,
    "multiplication_posee": multiplication_posee.render,
    "astuce_chaine": astuce_chaine.render,
}

# Une photo stock ne peut jamais reproduire du texte/chiffres imposés ni le
# personnage Curio (les illustrations curiosité n'en contiennent jamais — §5 —
# mais le terme reste un garde-fou si un sujet_photo dérivait un jour) : toute
# description qui mentionne un de ces signaux reste sur GPT Image 2 d'office,
# le stock n'est même pas tenté.
STOCK_DISQUALIFY_TERMS = [
    "texte", "légende", "chiffre", "nombre", "flèche", "schéma",
    "diagramme", "annotation", "étiquette", "encadré", "curio",
]

_QUERY_STOPWORDS = {"a", "an", "the", "of", "in", "on", "at", "with", "and", "or", "for"}
_WORD_RE = re.compile(r"[a-zà-öø-ÿ]+")


def _stock_eligible(description_visuelle):
    desc = description_visuelle.lower()
    return not any(term in desc for term in STOCK_DISQUALIFY_TERMS)


def _query_keywords(query):
    return {w for w in _WORD_RE.findall(query.lower()) if w not in _QUERY_STOPWORDS and len(w) > 2}


def _result_is_relevant(result, keywords):
    """Vrai si le titre/texte descriptif du résultat contient au moins un terme clé de la requête.

    Pexels expose un texte alt descriptif (pas de vrai titre) ; Wikimedia
    expose le vrai titre du fichier. stock_image_search.py normalise les deux
    dans result["title"]. Limite connue : un terme trop générique (ex.
    "penguin") peut faire matcher un résultat dont le sujet PRINCIPAL diffère
    (mauvaise espèce au premier plan) — validé sur le terrain le 17/08, à
    resserrer si le problème se reproduit malgré ce filtre.
    """
    haystack = (result.get("title") or "").lower()
    return any(kw in haystack for kw in keywords)


def build_image_plan(script):
    """Retourne la liste ordonnée des images à produire, chacune avec sa route.

    Chaque entrée : {"name", "route": "gpt_image"|"code_render"|"asset_copy", ...}
    - gpt_image : "prompt", "quality", "extra" (références supplémentaires),
      "stock_eligible"/"stock_query" (illustrations curiosité uniquement —
      tentative stock avant l'appel GPT Image réel, voir generate_images)
    - code_render : "render_type", "operation_data", "stage"
    - asset_copy : "asset_path" (fichier source à copier tel quel, 0€)
    """
    is_maths = bool(script.get("matiere")) and "math" in script["matiere"].lower()

    if script.get("type") == "competence":
        # v2.11 — hook fixe par matière, jamais régénéré (assets/hook_frames/).
        asset_path = HOOK_FRAME_MATHS if is_maths else HOOK_FRAME_FRANCAIS
        plan = [{"name": "hook_frame.png", "route": "asset_copy", "asset_path": asset_path}]
    else:
        # v2.17 — hook_background résolu une fois par script_generator.py
        # (fond fixe pour une sous-catégorie réutilisable, ou texte spécifique
        # au sujet réel) : même champ que celui utilisé par le prompt Seedance.
        # Curio y apparaît toujours : jamais éligible au stock.
        plan = [{
            "name": "hook_frame.png",
            "route": "gpt_image",
            "prompt": curiosity_prompts.build_hook_frame_prompt(script["hook_background"]),
            "quality": QUALITY_STANDARD,
            "extra": [],
            "stock_eligible": False,
            "stock_query": None,
        }]

    illus_route = script.get("image_route", "gpt_image")
    if illus_route == "code_render":
        # Une opération n'a qu'un seul résultat : 3 illustrations identiques
        # seraient redondantes. stage (1/2/3) fait varier le rendu — révélation
        # progressive pour les opérations posées, frame différent (principe/
        # exemple 1/exemple 2) pour astuce_chaine (voir chaque renderer).
        for i in range(1, 4):
            plan.append({
                "name": f"illus_{i}.png",
                "route": "code_render",
                "render_type": script["render_type"],
                "operation_data": script["operation_data"],
                "stage": i,
            })
    else:
        for i, illus in enumerate(script["illustrations"], start=1):
            if script["type"] == "curiosite":
                prompt = curiosity_prompts.build_illustration_prompt(illus["description_visuelle"])
                stock_query = illus.get("stock_query_en")
                # Bascule GPT Image direct si stock_query_en absent (script.json
                # généré avant ce champ, v2.19) : le français comme requête de
                # repli a produit de faux positifs sur le terrain (17/08) — un
                # mot court français ("eau") matche par pur hasard une sous-chaîne
                # anglaise ("beautiful"), le filtre de pertinence passe alors qu'il
                # n'y a aucun rapport. Mieux vaut le comportement d'avant (GPT
                # Image direct) que ce filtre non fiable en anglais/français mêlés.
                stock_eligible = bool(stock_query) and _stock_eligible(illus["description_visuelle"])
            else:
                # Type B : mot_cle/lettre_cle (français) ou diagramme pédagogique
                # (maths concept) toujours imprimés sur l'image — jamais éligible au stock.
                if is_maths:
                    prompt = competence_prompts.build_concept_prompt(illus["description_visuelle"], script["niveau"])
                else:
                    data = dict(illus)
                    data["niveau"] = script["niveau"]
                    prompt = competence_prompts.build_francais_prompt(data)
                stock_eligible = False
                stock_query = None
            plan.append({
                "name": f"illus_{i}.png",
                "route": "gpt_image",
                "prompt": prompt,
                "quality": QUALITY_STANDARD,
                "extra": [],
                "stock_eligible": stock_eligible,
                "stock_query": stock_query,
            })

    # code_render : illus_1.png contient des chiffres exacts calculés par code.
    # Ne jamais le repasser dans une génération GPT Image (image-to-image) qui
    # pourrait halluciner un chiffre différent sur la miniature publiée.
    reuse_illustration = illus_route != "code_render"
    plan.append({
        "name": "miniature.png",
        "route": "gpt_image",
        "prompt": curiosity_prompts.build_miniature_prompt(script["titre"], reuse_illustration=reuse_illustration),
        "quality": QUALITY_HIGH,
        "extra": ["illus_1.png", "logo"] if reuse_illustration else ["logo"],
        "stock_eligible": False,
        "stock_query": None,
    })
    return plan


def build_image_prompts(script):
    """Compat : liste [(nom_fichier, prompt, qualité, refs_extra)] pour les entrées gpt_image uniquement.

    Utilisé par main.py pour écrire prompts_all.txt (rien à copier-coller pour code_render/asset_copy).
    """
    return [(e["name"], e["prompt"], e["quality"], e["extra"]) for e in build_image_plan(script) if e["route"] == "gpt_image"]


def _reference_paths(target_name):
    """Références injectées selon l'image cible (règle 6 du brief : toujours au moins une).

    v2.8 : style_illustration_01/02.png retirés des références d'illustration —
    ce sont en réalité des visuels d'anciens reels (canicule, drakkar viking),
    pas des exemples de style neutres, et leur contenu se retrouvait recopié
    tel quel dans des illustrations sans rapport (bug systémique GPT Image 2
    image-to-image). Seul style_fond_cahier.png (fond Seyès pur, sans sujet)
    reste utilisé pour les illustrations.
    """
    if target_name == "hook_frame.png":
        return [REFERENCE_DIR / "curio_character_ref.png"]
    if target_name == "miniature.png":
        return [REFERENCE_DIR / "miniature_exemple.png"]
    return [REFERENCE_DIR / "style_fond_cahier.png"]


def _call_api(client, images, prompt, quality):
    try:
        return client.images.edit(
            model=OPENAI_IMAGE_MODEL,
            image=images,
            prompt=prompt,
            size=IMAGE_SIZE,
            quality=quality,
            n=1,
        )
    except BadRequestError as exc:
        if "size" not in str(exc).lower():
            raise
        print(f"Taille {IMAGE_SIZE} refusée par l'API, bascule sur {IMAGE_SIZE_FALLBACK}.")
        return client.images.edit(
            model=OPENAI_IMAGE_MODEL,
            image=images,
            prompt=prompt,
            size=IMAGE_SIZE_FALLBACK,
            quality=quality,
            n=1,
        )


def _generate_gpt_image(client, entry, output_dir):
    target = output_dir / entry["name"]
    input_paths = list(_reference_paths(entry["name"]))
    for item in entry["extra"]:
        input_paths.append(LOGO_PATH if item == "logo" else output_dir / item)
    missing = [p for p in input_paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Images d'entrée manquantes pour {entry['name']} : {missing}")

    with ExitStack() as stack:
        files = [stack.enter_context(open(p, "rb")) for p in input_paths]
        result = _call_api(client, files, entry["prompt"], entry["quality"])

    target.write_bytes(base64.b64decode(result.data[0].b64_json))
    log_api_call(output_dir, f"gpt-image ({entry['quality']})", COST_IMAGE, target)


def _generate_code_render(entry, output_dir):
    target = output_dir / entry["name"]
    renderer = MATH_RENDERERS[entry["render_type"]]
    content_img = renderer(**entry["operation_data"], stage=entry["stage"])
    compose_illustration(content_img, str(target))
    log_api_call(output_dir, f"code_render ({entry['render_type']})", 0.0, target)


def _generate_asset_copy(entry, output_dir):
    target = output_dir / entry["name"]
    source = entry["asset_path"]
    if not source.exists():
        raise FileNotFoundError(f"Asset hook frame manquant : {source}")
    shutil.copyfile(source, target)
    log_api_call(output_dir, f"asset_copy ({source.name})", 0.0, target)


def _try_stock_search(entry, output_dir):
    """Tente Pexels puis Wikimedia Commons sur entry["stock_query"].

    Un résultat n'est retenu que s'il passe _result_is_relevant (titre/texte
    descriptif contient un terme clé de la requête) — filtre plus strict que
    "premier résultat non vide" après le bug constaté sur le terrain le 17/08
    (mauvaise espèce de manchot au premier plan). La photo retenue est
    téléchargée dans un fichier temporaire puis composée sur le fond cahier
    Curio (compose_illustration, même compositing que le rendu code) avant
    d'écrire entry["name"] — jamais la photo brute. Retourne True si une
    image a été produite (GPT Image jamais appelé), False sinon (bascule GPT
    Image dans generate_images).
    """
    target = output_dir / entry["name"]
    keywords = _query_keywords(entry["stock_query"])
    for provider in ("pexels", "wikimedia"):
        try:
            results = stock_image_search.image_search(provider, entry["stock_query"])
        except Exception as exc:
            print(f"  [stock] {provider} erreur ({exc}), source suivante")
            continue

        relevant = [r for r in results if _result_is_relevant(r, keywords)]
        if not relevant:
            print(f"  [stock] {provider} : {len(results)} résultat(s), aucun pertinent pour '{entry['stock_query']}', source suivante")
            continue

        best = stock_image_search.select_best(relevant)
        raw_path = output_dir / f"_stock_raw_{entry['name']}"
        try:
            meta = stock_image_search.download_image(best, raw_path)
            with Image.open(raw_path) as img:
                compose_illustration(img.convert("RGBA"), str(target))
        finally:
            raw_path.unlink(missing_ok=True)

        log_api_call(output_dir, f"stock_{provider}", 0.0, target)
        print(f"  [ok] {entry['name']} (stock_{provider}, auteur {meta['author'] or 'inconnu'}, titre '{meta['title']}')")
        return True
    return False


def generate_images(script, output_dir):
    """Génère les 5 images. Skip si le fichier existe déjà. Bloque sans références GPT Image."""
    check_references()
    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])
    generated = []

    for entry in build_image_plan(script):
        target = output_dir / entry["name"]
        if target.exists():
            print(f"  [skip] {entry['name']} existe déjà")
            generated.append(target)
            continue

        if entry["route"] == "code_render":
            _generate_code_render(entry, output_dir)
            print(f"  [ok] {entry['name']} (code_render)")
        elif entry["route"] == "asset_copy":
            _generate_asset_copy(entry, output_dir)
            print(f"  [ok] {entry['name']} (asset_copy)")
        elif entry.get("stock_eligible") and _try_stock_search(entry, output_dir):
            pass  # image gratuite trouvée (Pexels/Wikimedia), print déjà fait dans _try_stock_search
        else:
            _generate_gpt_image(client, entry, output_dir)
            print(f"  [ok] {entry['name']} (gpt_image)")

        generated.append(target)

    return generated
