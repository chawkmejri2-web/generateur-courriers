"""Deux formulations de prompt à comparer (A: simple, B: contraint)."""
from letters import LETTER_TYPES, all_fields

KEYS = '{"objet": "...", "destinataire": "...", "salutation": "...", "corps": "...", "politesse": "...", "signature": "..."}'

SYSTEM = {
    "A": "Tu es un assistant qui rédige des courriers administratifs en français.",
    "B": ("Tu es un rédacteur administratif expert. Tu écris en français, avec un ton formel et courtois. "
          "RÈGLE ABSOLUE : tu utilises UNIQUEMENT les informations fournies. Tu n'inventes aucun nom, "
          "date, chiffre, numéro, adresse, e-mail ni fait. Si une information manque, tu l'omets, "
          "sans crochets ni point d'interrogation ni texte à compléter. Tu réponds uniquement en JSON valide."),
}


def build_prompt(variant, type_key, data):
    fields = all_fields(type_key)
    given = [f"- {f.label} : {data[f.key]}" for f in fields if data.get(f.key)]
    missing = [f.label for f in fields if not data.get(f.key)]
    label = LETTER_TYPES[type_key]["label"]
    if variant == "A":
        user = (f"Rédige une lettre : {label}.\nInformations :\n" + "\n".join(given) +
                f"\nRéponds en JSON avec les clés : {KEYS}")
    else:
        user = (f"Type de courrier : {label}\n\nINFORMATIONS FOURNIES (seule source autorisée) :\n" + "\n".join(given) +
                "\n\nINFORMATIONS NON FOURNIES (ne pas les mentionner ni les inventer) : " +
                (", ".join(missing) or "aucune") +
                "\n\nCONSIGNES :\n- objet : court et précis\n- destinataire : nom du destinataire seulement\n"
                "- salutation : ex. « Madame, Monsieur, »\n- corps : 2 à 3 paragraphes (séparés par \\n\\n), "
                "motif, détails fournis, demande claire\n- politesse : formule de politesse complète\n"
                "- signature : nom de l'expéditeur uniquement\n- Ne répète pas l'adresse ni la date (ajoutées automatiquement)\n"
                f"\nFORMAT : JSON strict, sans Markdown : {KEYS}")
    return SYSTEM[variant], user