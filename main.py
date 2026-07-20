"""CLI point d'entrée du pipeline Curio — voir CLAUDE.md (source de vérité)."""

import argparse
import datetime
import json
import sys
import threading
from pathlib import Path

from config import (
    COST_AUDIO_VERSION,
    COST_DESCRIPTION,
    COST_IMAGE,
    COST_SCRIPT,
    ELEVENLABS_CONFIG,
    OUTPUT_DIR,
    confirm,
    confirm_cost,
    retry_loop,
    slugify,
)
from generators import (
    audio_generator,
    image_generator,
    instagram_generator,
    script_generator,
    subtitle_generator,
    video_assembler,
)
from prompts.seedance_prompts import build_seedance_prompt

OPERATION_DESCRIPTIONS = {
    "division_posee": lambda d: f"{d['dividende']} ÷ {d['diviseur']}",
    "soustraction_colonnes": lambda d: f"{d['nombre1']} - {d['nombre2']}",
    "addition_colonnes": lambda d: f"{d['nombre1']} + {d['nombre2']}",
    "multiplication_posee": lambda d: f"{d['multiplicande']} × {d['multiplicateur']}",
    "astuce_chaine": lambda d: f"{d['titre']} : " + " / ".join(d["etapes"]),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Pipeline Reels Curio (@curio.education)")
    parser.add_argument("--type", choices=["curiosite", "competence"], help="Type de Reel")
    parser.add_argument("--sujet", help="Sujet du Reel (obligatoire pour curiosite)")
    parser.add_argument("--niveau", choices=["CP", "CE1", "CE2", "CM1", "CM2"], help="Niveau (Type B)")
    parser.add_argument("--matiere", help="maths ou francais (Type B)")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="Date YYYY-MM-DD")
    parser.add_argument("--only", choices=["images", "audio"], help="Relance une seule étape")
    parser.add_argument("--assemble", action="store_true", help="Relance uniquement le montage")
    parser.add_argument("--output-dir", help="Dossier output existant (pour --only / --assemble)")
    parser.add_argument("--audio", type=int, choices=[1, 2], help="Version audio pour le montage")
    parser.add_argument("--cta", choices=["abonnement", "commentaire"], help="Type de CTA (défaut : alternance automatique)")
    return parser.parse_args()


def next_cta():
    """Alternance 50-50 : l'opposé du CTA du dernier script généré."""
    scripts = sorted(OUTPUT_DIR.glob("*/*/script.json"), key=lambda p: p.stat().st_mtime)
    if scripts:
        last = json.loads(scripts[-1].read_text()).get("cta_type", "abonnement")
        return "commentaire" if last == "abonnement" else "abonnement"
    return "abonnement"


def load_existing(output_dir):
    output_dir = Path(output_dir).resolve()
    script_path = output_dir / "script.json"
    if not script_path.exists():
        sys.exit(f"Erreur : {script_path} introuvable. Lance d'abord le pipeline complet.")
    return output_dir, json.loads(script_path.read_text())


def write_prompt_files(script, output_dir):
    seedance = build_seedance_prompt(script["hook"], script.get("theme", "default"))
    (output_dir / "seedance_prompt.txt").write_text(seedance)

    blocks = [f"=== SEEDANCE (hook animé) ===\n{seedance}"]
    for name, prompt, quality, _ in image_generator.build_image_prompts(script):
        blocks.append(f"=== {name} (qualité {quality}) ===\n{prompt}")
    (output_dir / "prompts_all.txt").write_text("\n\n".join(blocks))


def checkpoint(number, label):
    print(f"\n{'=' * 60}\nCHECKPOINT {number} — {label}\n{'=' * 60}")


def _images_todo(script, output_dir):
    """Images manquantes, séparées gpt_image (payant) / code_render (0€, ADDENDUM v2.6)."""
    missing = [e for e in image_generator.build_image_plan(script) if not (output_dir / e["name"]).exists()]
    n_gpt = sum(1 for e in missing if e["route"] == "gpt_image")
    n_code = sum(1 for e in missing if e["route"] == "code_render")
    return missing, n_gpt, n_code


def run_images(script, output_dir):
    missing, n_gpt, n_code = _images_todo(script, output_dir)
    if not missing:
        print("Toutes les images existent déjà, rien à générer.")
        return
    label = f"Génération de {n_gpt} image(s) GPT Image 2" + (f" + {n_code} rendu(s) code (0€)" if n_code else "")
    if not confirm_cost(label, n_gpt * COST_IMAGE):
        sys.exit("Génération images annulée.")
    retry_loop("images", lambda: image_generator.generate_images(script, output_dir))


def run_audio(script, output_dir):
    todo = sum(
        1 for v in range(1, ELEVENLABS_CONFIG["versions_to_generate"] + 1)
        if not (output_dir / f"audio_v{v}.mp3").exists()
    )
    if todo == 0:
        print("Tous les audios existent déjà, rien à générer.")
        return
    if not confirm_cost(f"Génération de {todo} version(s) audio ElevenLabs", todo * COST_AUDIO_VERSION):
        sys.exit("Génération audio annulée.")
    retry_loop("audio", lambda: audio_generator.generate_audio_versions(script, output_dir))


def run_parallel_generation(script, output_dir):
    """Étape 1 : Thread A images + Thread B audio, coût affiché avant lancement."""
    missing_images, n_gpt, n_code = _images_todo(script, output_dir)
    n_audios = sum(
        1 for v in range(1, ELEVENLABS_CONFIG["versions_to_generate"] + 1)
        if not (output_dir / f"audio_v{v}.mp3").exists()
    )
    total = n_gpt * COST_IMAGE + n_audios * COST_AUDIO_VERSION
    if not missing_images and n_audios == 0:
        print("Images et audios déjà présents, étape 1 sautée.")
        return
    label = f"Étape 1 — {n_gpt} image(s) GPT Image" + (f" + {n_code} rendu(s) code (0€)" if n_code else "") + f" + {n_audios} audio(s) en parallèle"
    if not confirm_cost(label, total):
        sys.exit("Étape 1 annulée.")

    errors = []

    def thread_a():
        try:
            image_generator.generate_images(script, output_dir)
        except Exception as exc:
            errors.append(("images", exc))

    def thread_b():
        try:
            audio_generator.generate_audio_versions(script, output_dir)
        except Exception as exc:
            errors.append(("audio", exc))

    while True:
        errors.clear()
        threads = [threading.Thread(target=thread_a), threading.Thread(target=thread_b)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if not errors:
            return
        for step, exc in errors:
            print(f"\nERREUR — {step} : {exc}")
        if not confirm("Réessayer les étapes en échec ?"):
            sys.exit("Pipeline arrêté à l'étape 1.")


def choose_audio(output_dir, preselected):
    if preselected in (1, 2):
        return output_dir / f"audio_v{preselected}.mp3"
    while True:
        choice = input("Quelle version audio pour le montage ? (1/2) : ").strip()
        if choice in ("1", "2"):
            return output_dir / f"audio_v{choice}.mp3"


def wait_for_hook(output_dir):
    hook = output_dir / "hook_video.mp4"
    print("\nÉTAPE 2 — HOOK ANIMÉ (manuel)")
    print(f"1. Copie le prompt : {output_dir / 'seedance_prompt.txt'}")
    print("2. Génère le hook dans Dreamina / Seedance 2.0")
    print(f"3. Dépose le MP4 ici : {hook}")
    while not hook.exists():
        if not confirm("hook_video.mp4 déposé ?"):
            sys.exit("Pipeline en pause. Relance avec : python main.py --assemble --output-dir " + str(output_dir))
        if not hook.exists():
            print(f"Toujours introuvable : {hook}")
    print("  [ok] hook_video.mp4 détecté")


def run_assembly(script, output_dir, audio_choice):
    audio_path = choose_audio(output_dir, audio_choice)
    if not audio_path.exists():
        sys.exit(f"Erreur : {audio_path} introuvable.")
    retry_loop("sous-titres", lambda: subtitle_generator.generate_subtitles(audio_path, output_dir, script["narration"]))
    return retry_loop("montage", lambda: video_assembler.assemble_reel(output_dir, audio_path))


def run_description(script, output_dir):
    if not (output_dir / "description_instagram.txt").exists():
        if not confirm_cost("Description Instagram (Claude API)", COST_DESCRIPTION):
            return
    path = retry_loop("description", lambda: instagram_generator.generate_description(script, output_dir))
    print("\n--- DESCRIPTION INSTAGRAM ---\n")
    print(path.read_text())


def run_full_pipeline(args):
    if args.type == "curiosite" and not args.sujet:
        sys.exit("Erreur : --sujet obligatoire pour un Reel curiosité.")
    if args.type == "competence" and (not args.niveau or not args.matiere):
        sys.exit("Erreur : --niveau et --matiere obligatoires pour un Reel compétence.")

    sujet = args.sujet
    if args.type == "competence" and not sujet:
        competence = script_generator.pick_competence(args.niveau, args.matiere)
        sujet = competence["competence"]

    output_dir = OUTPUT_DIR / args.date / slugify(sujet)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Dossier de travail : {output_dir}")

    script_path = output_dir / "script.json"
    if script_path.exists():
        print("  [skip] script.json existe déjà")
        script = json.loads(script_path.read_text())
    else:
        if not confirm_cost("Génération du script (Claude API)", COST_SCRIPT):
            sys.exit("Pipeline annulé.")
        cta_type = args.cta or next_cta()
        print(f"CTA de ce reel : {cta_type}")
        script = retry_loop(
            "script",
            lambda: script_generator.generate_script(args.type, sujet, args.niveau, args.matiere, cta_type),
        )
        script_generator.save_script(script, output_dir)
    write_prompt_files(script, output_dir)

    checkpoint(1, "Validation sujet")
    print(json.dumps(script, ensure_ascii=False, indent=2))
    if script.get("image_route") == "code_render":
        describe = OPERATION_DESCRIPTIONS[script["render_type"]]
        print(f"\nIllustrations : rendu code ({script['render_type']}, 0€) — {describe(script['operation_data'])}")
    elif script.get("image_route") == "gpt_image" and script.get("matiere") and "math" in str(script.get("matiere", "")).lower():
        print("\nIllustrations : GPT Image 2 (concept sans calcul exact, pas d'opération à vérifier)")
    print(f"\nTous les prompts : {output_dir / 'prompts_all.txt'}")
    print((output_dir / "prompts_all.txt").read_text())
    if not confirm("Script et prompts validés ?"):
        sys.exit("Pipeline arrêté au checkpoint 1. Supprime script.json pour regénérer.")

    run_parallel_generation(script, output_dir)

    checkpoint(2, "Validation visuelle + audio")
    for name in ["hook_frame.png", "illus_1.png", "illus_2.png", "illus_3.png", "miniature.png",
                 "audio_v1.mp3", "audio_v2.mp3", "seedance_prompt.txt"]:
        print(f"  {output_dir / name}")
    if not confirm("Images et audios validés ?"):
        sys.exit("Pipeline arrêté au checkpoint 2. Supprime les fichiers à regénérer puis relance --only images ou --only audio.")

    wait_for_hook(output_dir)

    checkpoint(3, "Confirmation hook + choix audio v1/v2")
    audio_path = choose_audio(output_dir, args.audio)
    retry_loop("sous-titres", lambda: subtitle_generator.generate_subtitles(audio_path, output_dir, script["narration"]))
    reel = retry_loop("montage", lambda: video_assembler.assemble_reel(output_dir, audio_path))

    checkpoint(4, "Visionnage reel final")
    print(f"Reel final : {reel}")
    if not confirm("Reel validé ?"):
        sys.exit("Pipeline arrêté au checkpoint 4. Supprime reel_final.mp4 puis relance --assemble.")

    run_description(script, output_dir)
    print(f"\nTerminé. Publication manuelle sur @curio.education depuis : {output_dir}")


def main():
    args = parse_args()

    if args.only or args.assemble:
        if not args.output_dir:
            sys.exit("Erreur : --output-dir obligatoire avec --only / --assemble.")
        output_dir, script = load_existing(args.output_dir)
        write_prompt_files(script, output_dir)
        if args.only == "images":
            run_images(script, output_dir)
        elif args.only == "audio":
            run_audio(script, output_dir)
        else:
            reel = run_assembly(script, output_dir, args.audio)
            print(f"Reel final : {reel}")
            run_description(script, output_dir)
        return

    if not args.type:
        sys.exit("Erreur : --type obligatoire (ou utilise --only / --assemble).")
    run_full_pipeline(args)


if __name__ == "__main__":
    main()
