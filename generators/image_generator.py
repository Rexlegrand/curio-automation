"""Génération des 5 images PNG via GPT Image 2, références visuelles injectées."""

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
from prompts import competence_prompts, curiosity_prompts

QUALITY_STANDARD = "medium"
QUALITY_HIGH = "high"


def build_image_prompts(script):
    """Retourne la liste ordonnée [(nom_fichier, prompt, qualité, refs_extra)]."""
    theme = script.get("theme", "default")
    prompts = [("hook_frame.png", curiosity_prompts.build_hook_frame_prompt(theme), QUALITY_STANDARD, [])]

    for i, illus in enumerate(script["illustrations"], start=1):
        if script["type"] == "curiosite":
            prompt = curiosity_prompts.build_illustration_prompt(illus["description_visuelle"])
        elif script.get("matiere") and "math" in script["matiere"].lower():
            data = dict(illus)
            data["niveau"] = script["niveau"]
            prompt = competence_prompts.build_maths_prompt(data)
        else:
            data = dict(illus)
            data["niveau"] = script["niveau"]
            prompt = competence_prompts.build_francais_prompt(data)
        prompts.append((f"illus_{i}.png", prompt, QUALITY_STANDARD, []))

    prompts.append(("miniature.png", curiosity_prompts.build_miniature_prompt(script["titre"]), QUALITY_HIGH, ["illus_1.png", "logo"]))
    return prompts


def _reference_paths(target_name):
    """Références injectées selon l'image cible (règle 6 du brief : toujours au moins une)."""
    if target_name == "hook_frame.png":
        return [REFERENCE_DIR / "curio_character_ref.png"]
    if target_name == "miniature.png":
        return [REFERENCE_DIR / "miniature_exemple.png"]
    return [
        REFERENCE_DIR / "style_fond_cahier.png",
        REFERENCE_DIR / "style_illustration_01.png",
        REFERENCE_DIR / "style_illustration_02.png",
    ]


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


def generate_images(script, output_dir):
    """Génère les 5 images. Skip si le fichier existe déjà. Bloque sans références."""
    check_references()
    client = OpenAI(api_key=ENV["OPENAI_API_KEY"])
    generated = []

    for name, prompt, quality, extra in build_image_prompts(script):
        target = output_dir / name
        if target.exists():
            print(f"  [skip] {name} existe déjà")
            generated.append(target)
            continue

        input_paths = list(_reference_paths(name))
        for item in extra:
            input_paths.append(LOGO_PATH if item == "logo" else output_dir / item)
        missing = [p for p in input_paths if not p.exists()]
        if missing:
            raise FileNotFoundError(f"Images d'entrée manquantes pour {name} : {missing}")

        with ExitStack() as stack:
            files = [stack.enter_context(open(p, "rb")) for p in input_paths]
            result = _call_api(client, files, prompt, quality)

        target.write_bytes(base64.b64decode(result.data[0].b64_json))
        log_api_call(output_dir, f"gpt-image ({quality})", COST_IMAGE, target)
        print(f"  [ok] {name}")
        generated.append(target)

    return generated
