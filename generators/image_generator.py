"""Génération des 5 images PNG — GPT Image 2 (référence injectée) ou code_render (ADDENDUM v2.6).

Routage par image : hook_frame et miniature restent toujours GPT Image 2
(Curio y apparaît, pas de calcul à représenter). Les 3 illustrations d'un
Reel compétence maths passent par generators/math_renderers/ (0€, 0 risque
de chiffre halluciné) quand script["image_route"] == "code_render" ;
sinon comportement GPT Image 2 existant, inchangé.
"""

import base64
from contextlib import ExitStack

from openai import BadRequestError, OpenAI

from config import (
    COST_IMAGE,
    ENV,
    IMAGE_SIZE,
    IMAGE_SIZE_FALLBACK,
    LOGO_PATH,
    OPENAI_IMAGE_MODEL,
    REFERENCE_DIR,
    check_references,
    log_api_call,
)
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


def build_image_plan(script):
    """Retourne la liste ordonnée des images à produire, chacune avec sa route.

    Chaque entrée : {"name", "route": "gpt_image"|"code_render", ...}
    - gpt_image : "prompt", "quality", "extra" (références supplémentaires)
    - code_render : "render_type", "operation_data"
    """
    theme = script.get("theme", "default")
    plan = [{
        "name": "hook_frame.png",
        "route": "gpt_image",
        "prompt": curiosity_prompts.build_hook_frame_prompt(theme),
        "quality": QUALITY_STANDARD,
        "extra": [],
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
            elif script.get("matiere") and "math" in script["matiere"].lower():
                prompt = competence_prompts.build_concept_prompt(illus["description_visuelle"], script["niveau"])
            else:
                data = dict(illus)
                data["niveau"] = script["niveau"]
                prompt = competence_prompts.build_francais_prompt(data)
            plan.append({"name": f"illus_{i}.png", "route": "gpt_image", "prompt": prompt, "quality": QUALITY_STANDARD, "extra": []})

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
    })
    return plan


def build_image_prompts(script):
    """Compat : liste [(nom_fichier, prompt, qualité, refs_extra)] pour les entrées gpt_image uniquement.

    Utilisé par main.py pour écrire prompts_all.txt (rien à copier-coller pour code_render).
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
        else:
            _generate_gpt_image(client, entry, output_dir)

        print(f"  [ok] {entry['name']} ({entry['route']})")
        generated.append(target)

    return generated
