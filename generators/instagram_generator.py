"""Description Instagram via Claude API — structure fixe du brief (section 14)."""

import anthropic

from config import CLAUDE_MODEL, COST_DESCRIPTION, ENV, log_api_call

MENTIONS = {
    "toujours": ["@scilabus", "@lumni_off", "@cestpassorcier_off"],
    "science": ["@cnrsofficial", "@palais_de_la_decouverte"],
    "actualite": ["@franceinfo", "@bfmtv"],
    "transport": ["@sncf", "@transilien"],
    "meteo": ["@meteofrance"],
    "education": ["@maitressenadege", "@profsdecole"],
    "parents": ["@parents.fr"],
}

STRUCTURE = """[EMOJI] [ACCROCHE — reformulation du hook]

[DÉVELOPPEMENT — 3 paragraphes courts]

[FAIT CLÉ mis en valeur avec emoji]

👇 [QUESTION D'ENGAGEMENT pour les commentaires]

📩 Envoie CURIO en MP et reçois gratuitement une activité pédagogique
niveau CP-CM2 sur [SUJET].

🔔 Suis Curio pour une nouvelle curiosité chaque jour.

[5 HASHTAGS MAX, jamais de majuscule, toujours inclure #curio]

[2-3 MENTIONS STRATÉGIQUES selon sujet]"""


def generate_description(script, output_dir):
    """Génère description_instagram.txt. Skip si déjà présent."""
    target = output_dir / "description_instagram.txt"
    if target.exists():
        print(f"  [skip] {target.name} existe déjà")
        return target

    client = anthropic.Anthropic(api_key=ENV["ANTHROPIC_API_KEY"])
    mentions_pool = "\n".join(f"- {k} : {', '.join(v)}" for k, v in MENTIONS.items())
    niveau = f"\nNiveau scolaire : {script['niveau']}" if script.get("niveau") else ""
    if script.get("cta_type") == "commentaire":
        mot = script.get("cta_mot", "CURIO")
        cta_note = (
            f"\nCTA du Reel : commenter le mot {mot} pour recevoir l'activité. "
            f"Remplace la ligne 📩 par : 💬 Commente {mot} et reçois gratuitement "
            "une activité pédagogique niveau CP-CM2 sur le sujet."
        )
    else:
        cta_note = "\nCTA du Reel : abonnement. Garde la ligne 📩 Envoie CURIO en MP telle quelle."

    prompt = f"""Écris la description Instagram d'un Reel du compte @curio.education
(éducation primaire française, mascotte pingouin Curio).

Sujet : {script['sujet']}
Hook du Reel : {script['hook']}
Narration complète : {script['narration']}{niveau}{cta_note}
Thème : {script.get('theme', 'default')}

Structure OBLIGATOIRE (respecte-la exactement, remplace les crochets) :
{STRUCTURE}

Règles :
- 5 hashtags maximum, jamais de majuscule dans les hashtags.
- Choisis 2-3 mentions dans ce vivier selon le thème (les mentions "toujours" sont prioritaires) :
{mentions_pool}
- Si le sujet est une compétence scolaire, ajoute le hashtag du niveau (ex: #ce2).
- Ton chaleureux, accessible aux parents, phrases courtes.

Réponds UNIQUEMENT avec le texte final de la description, rien d'autre."""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    target.write_text(text + "\n")
    log_api_call(output_dir, "claude description", COST_DESCRIPTION, target)
    print(f"  [ok] {target.name}")
    return target
