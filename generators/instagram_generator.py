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

{ligne_cta}

🔔 Suis Curio pour une nouvelle curiosité chaque jour.

[5 HASHTAGS MAX, jamais de majuscule, toujours inclure #curio.
Jamais de hashtag de niveau scolaire (#cp, #ce1, #cm1...) sauf Reel compétence.]

[2-3 MENTIONS STRATÉGIQUES selon sujet]"""

LIGNE_CTA = {
    "abonnement": "📩 Envoie CURIO en MP et reçois gratuitement une activité pédagogique\nniveau CP-CM2 sur [SUJET].",
    "commentaire": "💬 Commente CURIO et reçois gratuitement une activité pédagogique\nniveau CP-CM2 sur [SUJET].",
}


def generate_description(script, output_dir):
    """Génère description_instagram.txt. Skip si déjà présent."""
    target = output_dir / "description_instagram.txt"
    if target.exists():
        print(f"  [skip] {target.name} existe déjà")
        return target

    client = anthropic.Anthropic(api_key=ENV["ANTHROPIC_API_KEY"])
    mentions_pool = "\n".join(f"- {k} : {', '.join(v)}" for k, v in MENTIONS.items())
    niveau = f"\nNiveau scolaire : {script['niveau']}" if script.get("niveau") else ""
    cta_type = script.get("cta_type", "abonnement")
    structure = STRUCTURE.format(ligne_cta=LIGNE_CTA[cta_type])
    cta_note = f"\nCTA du Reel : {cta_type}. La ligne CTA de la structure est déjà la bonne, reprends-la."

    prompt = f"""Écris la description Instagram d'un Reel du compte @curio.education
(éducation primaire française, mascotte pingouin Curio).

Sujet : {script['sujet']}
Hook du Reel : {script['hook']}
Narration complète : {script['narration']}{niveau}{cta_note}
Thème : {script.get('theme', 'default')}

Structure OBLIGATOIRE (respecte-la exactement, remplace les crochets) :
{structure}

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
