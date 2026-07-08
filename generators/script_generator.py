"""Génération du script JSON horodaté via Claude API (+ lecture Excel Type B)."""

import datetime
import json
import random
import sys

import anthropic

from config import CLAUDE_MODEL, DATA_XLSX, ELEVENLABS_CONFIG, ENV

WORD_MIN, WORD_MAX = ELEVENLABS_CONFIG["word_count_target"]

SCHEMA_TYPE_A = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "un parmi: sport, nature, histoire, maths, science, transport, meteo, default",
  "hook": "Attends... [fait surprenant en question ou affirmation choc]",
  "narration": "texte complet parlé, commence par la phrase hook, 65-75 mots au total",
  "segments": [
    {"start": 0, "end": 4, "role": "hook", "texte": "..."},
    {"start": 4, "end": 9, "role": "illustration_1", "texte": "..."},
    {"start": 9, "end": 13, "role": "curio_a", "texte": "..."},
    {"start": 13, "end": 18, "role": "illustration_2", "texte": "..."},
    {"start": 18, "end": 22, "role": "curio_b", "texte": "..."},
    {"start": 22, "end": 25, "role": "illustration_3", "texte": "..."},
    {"start": 25, "end": 30, "role": "cta", "texte": "..."}
  ],
  "illustrations": [
    {"description_visuelle": "description hyper-réaliste illustration 1 (photo style Wikipédia/magazine, jamais de personnage Curio, jamais de cartoon)"},
    {"description_visuelle": "illustration 2"},
    {"description_visuelle": "illustration 3"}
  ]
}"""

SCHEMA_TYPE_B_MATHS = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "maths",
  "hook": "Attends... tu sais vraiment comment [compétence] ?",
  "narration": "texte complet parlé, commence par la phrase hook, 65-75 mots au total",
  "segments": [ même découpage 0-4/4-9/9-13/13-18/18-22/22-25/25-30 que Type A ],
  "illustrations": [
    {
      "type_operation": "ex: addition posée avec retenue",
      "operation_complete": "l'opération posée complète, chaque chiffre exact, avec le résultat",
      "etapes_numerotees": "étapes numérotées avec les valeurs exactes",
      "operation_resume": "ex: 347 + 285 = 632"
    },
    { "illustration 2, mêmes clés": "..." },
    { "illustration 3, mêmes clés": "..." }
  ]
}"""

SCHEMA_TYPE_B_FRANCAIS = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "default",
  "hook": "Attends... tu sais vraiment comment [compétence] ?",
  "narration": "texte complet parlé, commence par la phrase hook, 65-75 mots au total",
  "segments": [ même découpage 0-4/4-9/9-13/13-18/18-22/22-25/25-30 que Type A ],
  "illustrations": [
    {
      "regle_exacte": "la règle de grammaire exacte",
      "exemple_correct": "phrase exemple correcte",
      "test_substitution_ok": "test de substitution qui marche",
      "conclusion_ok": "conclusion",
      "exemple_incorrect": "phrase exemple incorrecte",
      "test_substitution_ko": "test de substitution qui ne marche pas",
      "conclusion_ko": "conclusion"
    },
    { "illustration 2, mêmes clés": "..." },
    { "illustration 3, mêmes clés": "..." }
  ]
}"""


def pick_competence(niveau, matiere):
    """Choisit une compétence dans data/Competences_Curio.xlsx (onglet = niveau).

    L'en-tête (Matière | Difficulté | Compétence) n'est pas forcément en ligne 1
    (l'onglet CP a des lignes de statut au-dessus) : on filtre sur le contenu.
    """
    if not DATA_XLSX.exists():
        sys.exit(f"Erreur : {DATA_XLSX} introuvable. Dépose le fichier Excel puis relance.")
    import openpyxl

    wb = openpyxl.load_workbook(DATA_XLSX, read_only=True)
    if niveau not in wb.sheetnames:
        sys.exit(f"Erreur : onglet '{niveau}' absent du Excel. Onglets : {wb.sheetnames}")
    ws = wb[niveau]
    candidates = []
    for r in ws.iter_rows(values_only=True):
        if not r or len(r) < 3 or not r[0] or not r[2]:
            continue
        col_matiere = str(r[0]).strip().lower()
        if col_matiere == "matière":
            continue
        if matiere.strip().lower() in col_matiere:
            candidates.append(r)
    if not candidates:
        sys.exit(f"Erreur : aucune compétence '{matiere}' dans l'onglet {niveau}.")
    row = random.choice(candidates)
    competence = {"matiere": str(row[0]), "difficulte": str(row[1]), "competence": str(row[2])}
    print(f"Compétence choisie : [{niveau}] {competence['matiere']} — {competence['competence']} (difficulté {competence['difficulte']})")
    return competence


CTA_INSTRUCTIONS = {
    "abonnement": (
        "Le dernier segment (role cta) est un appel à s'abonner, court et naturel "
        "(variante de : Abonne-toi pour une nouvelle curiosité chaque jour !)."
    ),
    "commentaire": (
        "Le dernier segment (role cta) demande de commenter un MOT-CLÉ en majuscules "
        "lié au sujet pour recevoir une activité pédagogique gratuite "
        "(ex : Commente VELO et je t'envoie une activité gratuite !). "
        "Ajoute aussi un champ \"cta_mot\" dans le JSON avec ce mot-clé exact."
    ),
}


def _build_prompt(reel_type, sujet, niveau, matiere, cta_type):
    if reel_type == "curiosite":
        schema = SCHEMA_TYPE_A
        contexte = f"Sujet du Reel (Type A — Curiosité du jour) : {sujet}"
        regles = (
            "- Les descriptions d'illustrations doivent être 100% photoréalistes, "
            "comme des photos Wikipédia ou de magazine. Jamais de personnage Curio, jamais de cartoon.\n"
            "- Si un schéma est nécessaire : flèches + chiffres simples, minimaliste."
        )
    elif matiere and "math" in matiere.lower():
        schema = SCHEMA_TYPE_B_MATHS
        contexte = f"Sujet du Reel (Type B — Compétence maths, niveau {niveau}) : {sujet}"
        regles = (
            "- EXACTITUDE PÉDAGOGIQUE STRICTE : chaque chiffre mathématiquement correct, "
            "méthode Éducation Nationale uniquement. Vérifie chaque calcul deux fois."
        )
    else:
        schema = SCHEMA_TYPE_B_FRANCAIS
        contexte = f"Sujet du Reel (Type B — Compétence français, niveau {niveau}) : {sujet}"
        regles = (
            "- EXACTITUDE PÉDAGOGIQUE STRICTE : chaque mot correctement orthographié, "
            "tous les accents présents, règle conforme aux programmes officiels."
        )
    cta_instruction = CTA_INSTRUCTIONS[cta_type]
    return f"""Tu écris le script d'un Reel Instagram de 25-30 secondes pour @curio.education,
compte éducatif français pour enfants de primaire (CP-CM2) et leurs parents.
Le narrateur est Curio, un pingouin curieux et enthousiaste. Ton : simple, vivant,
phrases courtes, vocabulaire accessible à un enfant de 8 ans.

{contexte}

Contraintes :
- La narration fait STRICTEMENT entre {WORD_MIN} et {WORD_MAX} mots (la voix lit ~180 mots/minute : cible 28-35 secondes, jamais plus de 35).
- La narration commence par la phrase hook exacte.
- Les segments suivent le découpage timecode imposé et la somme des textes = la narration.
- AUCUNE DIGRESSION : chaque phrase sert directement le sujet principal. Si une info est
  seulement cousine du sujet (autre règle, autre récompense, anecdote hors sujet), ne pas l'inclure.
- {cta_instruction}
{regles}

Réponds UNIQUEMENT avec un objet JSON valide (aucun texte autour, pas de bloc markdown) suivant ce schéma :
{schema}"""


def _count_words(text):
    return len(text.split())


def generate_script(reel_type, sujet, niveau=None, matiere=None, cta_type="abonnement"):
    """Appelle Claude, valide le nombre de mots, retourne le dict script."""
    client = anthropic.Anthropic(api_key=ENV["ANTHROPIC_API_KEY"])
    prompt = _build_prompt(reel_type, sujet, niveau, matiere, cta_type)
    feedback = ""
    for attempt in range(3):
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt + feedback}],
        )
        raw = "".join(b.text for b in response.content if b.type == "text").strip()
        if "{" not in raw:
            raise ValueError(f"Réponse Claude sans JSON : {raw[:200]}")
        raw = raw[raw.index("{"):raw.rindex("}") + 1]
        script = json.loads(raw)
        wc = _count_words(script["narration"])
        if WORD_MIN <= wc <= WORD_MAX:
            break
        print(f"Narration à {wc} mots (cible {WORD_MIN}-{WORD_MAX}), régénération...")
        feedback = (
            f"\n\nTa réponse précédente faisait {wc} mots. "
            f"Réécris avec STRICTEMENT entre {WORD_MIN} et {WORD_MAX} mots dans la narration."
        )
    script["genere_le"] = datetime.datetime.now().isoformat(timespec="seconds")
    script["type"] = reel_type
    script["sujet"] = sujet
    script["niveau"] = niveau
    script["matiere"] = matiere
    script["cta_type"] = cta_type
    script["word_count"] = _count_words(script["narration"])
    return script


def save_script(script, output_dir):
    path = output_dir / "script.json"
    path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    return path
