"""Génération du script JSON horodaté via Claude API (+ lecture Excel Type B).

Type B maths (ADDENDUM v2.6) : Claude classe aussi le sujet en image_route
(code_render / gpt_image) dans le même appel, sans coût API supplémentaire.
Le render_type et l'operation_data sont revérifiés en Python avant écriture
du script.json — aucun chiffre n'est fait confiance sans contrôle.
"""

import datetime
import json
import random
import re
import sys

import anthropic

from config import CLAUDE_MODEL, DATA_XLSX, ELEVENLABS_CONFIG, ENV

WORD_MIN, WORD_MAX = ELEVENLABS_CONFIG["word_count_target"]

SCHEMA_TYPE_A = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "un parmi: sport, combat, velo, nature, histoire, maths, science, transport, meteo, default",
  "hook": "Attends... [fait surprenant en question ou affirmation choc]",
  "narration": "texte complet parlé, commence par la phrase hook, 85-100 mots au total",
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

# ADDENDUM v2.6 §3 — classification image_route faite par Claude, même appel.
SCHEMA_TYPE_B_MATHS = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "maths",
  "hook": "Attends... tu sais vraiment comment [compétence] ?",
  "narration": "texte complet parlé, commence par la phrase hook, 85-100 mots au total",
  "segments": [ même découpage 0-4/4-9/9-13/13-18/18-22/22-25/25-30 que Type A ],
  "image_route": "code_render" ou "gpt_image",
  "render_type": "division_posee | soustraction_colonnes | addition_colonnes | multiplication_posee | astuce_chaine, ou null si gpt_image",
  "operation_data": {
    "// si division_posee": "",
    "dividende": "int", "diviseur": "int (1 chiffre ; 2 chiffres autorisé seulement si niveau CM2)",
    "// si soustraction_colonnes ou addition_colonnes (clés identiques)": "",
    "nombre1": "int (nombre1 >= nombre2 pour la soustraction)", "nombre2": "int",
    "// si multiplication_posee": "",
    "multiplicande": "int", "multiplicateur": "int 1 chiffre (0-9)",
    "// si astuce_chaine": "",
    "titre": "ex: Multiplier par 5",
    "etapes": ["ligne 1 (ex: 46 × 5)", "ligne 2 avec =", "... dernière ligne = résultat final avec ="],
    "// si gpt_image (null operation_data)": "ne pas inclure operation_data"
  },
  "illustrations": [
    {"description_visuelle": "SEULEMENT si image_route=gpt_image : diagramme pédagogique clair du concept (ex: axe de symétrie, parts de fraction, unité de mesure), fond cahier, pas de personnage Curio, pas de chiffre inventé"},
    { "illustration 2, même clé, vide [] si image_route=code_render": "..." },
    { "illustration 3, même clé": "..." }
  ]
}"""

SCHEMA_TYPE_B_FRANCAIS = """\
{
  "titre": "titre court pour la miniature (6 mots max)",
  "theme": "default",
  "hook": "Attends... tu sais vraiment comment [compétence] ?",
  "narration": "texte complet parlé, commence par la phrase hook, 85-100 mots au total",
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

# ADDENDUM v2.6 §3 — règle de classification pour Claude (Type B maths uniquement)
CLASSIFICATION_RULES = """
Règle de classification image_route (obligatoire pour ce sujet maths) :
- Si le sujet implique une opération posée avec retenue/emprunt/potence
  → image_route = "code_render", choisir render_type parmi :
    division_posee | soustraction_colonnes | addition_colonnes | multiplication_posee
  → remplir operation_data avec les clés exactes de ce render_type (voir schéma),
    illustrations = [] (tableau vide, non utilisé pour code_render)
- Si le sujet est une astuce de calcul mental présentable comme une chaîne
  d'égalités (ex: ×5 = ×10÷2, ×4 = ×2×2)
  → image_route = "code_render", render_type = "astuce_chaine"
  → operation_data = {"titre": ..., "etapes": [...]}, illustrations = []
  → FORMAT STRICT de chaque ligne d'etapes (chaque ligne vérifiée automatiquement) :
    - la première ligne est une expression seule, SANS signe = (ex: "46 × 5")
    - chaque ligne suivante est une égalité COMPLÈTE "valeur = valeur" avec un
      nombre explicite des DEUX côtés (ex: "46 × 10 = 460", PAS "= 460")
    - jamais de ligne commençant par "=", jamais de "?", jamais de variable :
      uniquement des chiffres et opérateurs (+ - × ÷) des deux côtés du "="
- Sinon (notion, concept visuel, règle sans calcul chiffré : symétrie,
  fractions en parts, unités de mesure)
  → image_route = "gpt_image", render_type = null, ne pas inclure operation_data,
  → remplir illustrations avec 3 description_visuelle (diagramme pédagogique)
Vérifie toi-même chaque valeur numérique d'operation_data avant de répondre :
le résultat doit être mathématiquement exact.
"""


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
        "Le dernier segment (role cta) demande de commenter le mot CURIO (toujours CURIO, "
        "jamais un autre mot) pour recevoir une activité pédagogique gratuite "
        "(ex : Commente CURIO et je t'envoie une activité gratuite !). "
        "Ajoute aussi un champ \"cta_mot\": \"CURIO\" dans le JSON."
    ),
}


def _build_prompt(reel_type, sujet, niveau, matiere, cta_type):
    is_maths = reel_type == "competence" and matiere and "math" in matiere.lower()
    if reel_type == "curiosite":
        schema = SCHEMA_TYPE_A
        contexte = f"Sujet du Reel (Type A — Curiosité du jour) : {sujet}"
        regles = (
            "- Les descriptions d'illustrations doivent être 100% photoréalistes, "
            "comme des photos Wikipédia ou de magazine. Jamais de personnage Curio, jamais de cartoon.\n"
            "- Si un schéma est nécessaire : flèches + chiffres simples, minimaliste."
        )
    elif is_maths:
        schema = SCHEMA_TYPE_B_MATHS
        contexte = f"Sujet du Reel (Type B — Compétence maths, niveau {niveau}) : {sujet}"
        regles = (
            "- EXACTITUDE PÉDAGOGIQUE STRICTE : chaque chiffre mathématiquement correct, "
            "méthode Éducation Nationale uniquement. Vérifie chaque calcul deux fois.\n"
            + CLASSIFICATION_RULES
        )
    else:
        schema = SCHEMA_TYPE_B_FRANCAIS
        contexte = f"Sujet du Reel (Type B — Compétence français, niveau {niveau}) : {sujet}"
        regles = (
            "- EXACTITUDE PÉDAGOGIQUE STRICTE : chaque mot correctement orthographié, "
            "tous les accents présents, règle conforme aux programmes officiels."
        )
    cta_instruction = CTA_INSTRUCTIONS[cta_type]
    return f"""Tu écris le script d'un Reel Instagram de 28-35 secondes pour @curio.education,
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


_SAFE_EXPR = re.compile(r"^[0-9+\-*/(). ]+$")


def _safe_eval_arithmetic(expr):
    """Évalue une expression arithmétique simple (chiffres/+-*/()) sans exec de code arbitraire."""
    normalized = expr.replace("×", "*").replace("x", "*").replace("X", "*").replace("÷", "/").replace(",", ".")
    normalized = normalized.strip()
    if not _SAFE_EXPR.match(normalized):
        raise ValueError(f"expression non numérique : {expr!r}")
    return eval(normalized, {"__builtins__": {}}, {})  # noqa: S307 — charset restreint à [0-9+-*/(). ] ci-dessus


def _validate_astuce_chaine(operation_data):
    """Vérifie que chaque ligne 'a = b' de l'astuce est arithmétiquement exacte."""
    etapes = operation_data.get("etapes")
    if not etapes or not isinstance(etapes, list):
        raise ValueError("astuce_chaine : operation_data.etapes manquant ou invalide")
    for ligne in etapes:
        if "=" not in ligne:
            continue
        gauche, droite = ligne.rsplit("=", 1)
        try:
            valeur_gauche = _safe_eval_arithmetic(gauche)
            valeur_droite = _safe_eval_arithmetic(droite)
        except (ValueError, SyntaxError, ZeroDivisionError) as exc:
            raise ValueError(f"astuce_chaine : ligne illisible '{ligne}' ({exc})") from exc
        if abs(valeur_gauche - valeur_droite) > 1e-6:
            raise ValueError(f"astuce_chaine : ligne fausse '{ligne}' ({valeur_gauche} != {valeur_droite})")


def _validate_operation_data(render_type, operation_data):
    """Vérifie les opérandes fournis par Claude avant toute écriture (ADDENDUM v2.6 §3).

    Pour les opérations posées, le résultat est de toute façon recalculé par le
    renderer (jamais celui de Claude) : on vérifie seulement le TYPE et les
    contraintes des opérandes. Pour astuce_chaine, Claude fournit du texte
    libre : on vérifie l'exactitude arithmétique de chaque ligne.
    """
    if operation_data is None:
        raise ValueError(f"{render_type} : operation_data manquant")

    if render_type == "division_posee":
        dividende, diviseur = operation_data.get("dividende"), operation_data.get("diviseur")
        if not isinstance(dividende, int) or not isinstance(diviseur, int):
            raise ValueError("division_posee : dividende/diviseur doivent être des entiers")
        if diviseur == 0:
            raise ValueError("division_posee : diviseur ne peut pas être 0")
    elif render_type in ("soustraction_colonnes", "addition_colonnes"):
        n1, n2 = operation_data.get("nombre1"), operation_data.get("nombre2")
        if not isinstance(n1, int) or not isinstance(n2, int):
            raise ValueError(f"{render_type} : nombre1/nombre2 doivent être des entiers")
        if render_type == "soustraction_colonnes" and n1 < n2:
            raise ValueError(f"soustraction_colonnes : nombre1 ({n1}) < nombre2 ({n2}), résultat négatif")
    elif render_type == "multiplication_posee":
        multiplicande, multiplicateur = operation_data.get("multiplicande"), operation_data.get("multiplicateur")
        if not isinstance(multiplicande, int) or not isinstance(multiplicateur, int):
            raise ValueError("multiplication_posee : multiplicande/multiplicateur doivent être des entiers")
        if not (0 <= multiplicateur <= 9):
            raise ValueError(f"multiplication_posee : multiplicateur {multiplicateur} doit être à 1 chiffre")
    elif render_type == "astuce_chaine":
        _validate_astuce_chaine(operation_data)
    else:
        raise ValueError(f"render_type inconnu : {render_type}")


def _validate_classification(script):
    """Type B maths uniquement : vérifie image_route/render_type/operation_data."""
    route = script.get("image_route")
    if route not in ("code_render", "gpt_image"):
        raise ValueError(f"image_route invalide ou manquant : {route!r}")
    if route == "code_render":
        _validate_operation_data(script.get("render_type"), script.get("operation_data"))
    elif route == "gpt_image":
        illustrations = script.get("illustrations")
        if not illustrations or len(illustrations) != 3:
            raise ValueError("gpt_image : 3 illustrations (description_visuelle) attendues")


def generate_script(reel_type, sujet, niveau=None, matiere=None, cta_type="abonnement"):
    """Appelle Claude, valide le nombre de mots (+ classification maths), retourne le dict script."""
    is_maths = reel_type == "competence" and matiere and "math" in matiere.lower()
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

        problems = []
        if not (WORD_MIN <= wc <= WORD_MAX):
            problems.append(f"narration à {wc} mots (cible {WORD_MIN}-{WORD_MAX})")
        if is_maths:
            try:
                _validate_classification(script)
            except ValueError as exc:
                problems.append(str(exc))

        if not problems:
            break
        print(f"Script invalide ({'; '.join(problems)}), régénération...")
        feedback = (
            f"\n\nTa réponse précédente était invalide : {'; '.join(problems)}. "
            "Corrige et réponds à nouveau avec le JSON complet en respectant strictement le schéma."
        )
    else:
        raise ValueError(f"Script invalide après 3 tentatives : {'; '.join(problems)}")

    if not is_maths:
        script.setdefault("image_route", "gpt_image")
        script.setdefault("render_type", None)
        script.setdefault("operation_data", None)

    script["genere_le"] = datetime.datetime.now().isoformat(timespec="seconds")
    script["type"] = reel_type
    script["sujet"] = sujet
    script["niveau"] = niveau
    script["matiere"] = matiere
    script["cta_type"] = cta_type
    script["word_count"] = wc
    return script


def save_script(script, output_dir):
    path = output_dir / "script.json"
    path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    return path
