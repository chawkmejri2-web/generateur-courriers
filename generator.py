"""Génération (API LLM Gemini ou mode démo), composition et contrôle anti-invention."""
import json, os, re
from dotenv import load_dotenv
from letters import LETTER_TYPES
from prompts import build_prompt

load_dotenv()
PARTS = ("objet", "destinataire", "salutation", "corps", "politesse", "signature")


def api_available():
    return bool(os.getenv("GEMINI_API_KEY"))


def call_llm(system, user):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    r = client.models.generate_content(
        model=os.getenv("LLM_MODEL", "gemini-3.5-flash"),
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system, temperature=0.3, response_mime_type="application/json"),
    )
    return r.text


def parse_letter(raw):
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("Réponse du modèle sans JSON.")
    d = json.loads(m.group(0))
    miss = [k for k in PARTS if not str(d.get(k, "")).strip()]
    if miss:
        raise ValueError(f"Parties manquantes : {miss}")
    return {k: str(d[k]).strip() for k in PARTS}


def mock_letter(t, d):
    g = lambda k: d.get(k, "")
    body = {
        "conge": f"Je vous prie de bien vouloir m'accorder un congé {g('type_conge').lower()} du {g('date_debut')} au {g('date_fin')}, au titre de mon poste de {g('poste')}.",
        "attestation": f"Je souhaite obtenir une attestation {g('type_attestation')}. Elle me sera utile pour : {g('usage')}.",
        "reclamation": f"Je me permets de vous adresser une réclamation concernant {g('sujet')}. Les faits datent du {g('date_incident')} : {g('description')}",
        "stage": f"Étudiant(e) en {g('formation')}, je vous adresse ma candidature pour le poste suivant : {g('poste')}. Mes compétences principales : {g('competences')}. Je suis disponible à partir du {g('disponibilite')} pour une durée de {g('duree')}.",
        "demission": f"Par la présente, je vous informe de ma décision de démissionner de mon poste de {g('poste')}, avec un départ effectif le {g('date_effet')}.",
    }[t]
    for k in ("motif", "preavis", "montant"):
        if g(k) and t in ("conge", "demission", "reclamation"):
            body += f"\n\n{k.capitalize()} : {g(k)}."
    if t == "reclamation":
        body += f"\n\nJe souhaite : {g('attendu')}"
    return {"objet": LETTER_TYPES[t]["label"], "destinataire": g("dest_nom"), "salutation": "Madame, Monsieur,",
            "corps": body, "politesse": "Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
            "signature": g("nom")}


def generate(type_key, data, variant="B", mock=False):
    if mock:
        return mock_letter(type_key, data)
    system, user = build_prompt(variant, type_key, data)
    try:
        return parse_letter(call_llm(system, user))
    except json.JSONDecodeError:  # 1 nouvel essai si JSON invalide
        return parse_letter(call_llm(system, user))


def letter_to_text(d, L):
    head = [d["nom"]] + [d[k] for k in ("adresse", "email", "telephone") if d.get(k)]
    dest = [L["destinataire"]] + ([d["dest_adresse"]] if d.get("dest_adresse") else [])
    return "\n\n".join(["\n".join(head), "\n".join(dest), f"{d['ville']}, le {d['date_lettre']}",
                        f"Objet : {L['objet']}", L["salutation"], L["corps"], L["politesse"], L["signature"]])


def check_invention(data, text):
    """Signale ce que le texte contient et que le formulaire ne contient pas."""
    src = " ".join(str(v) for v in data.values())
    digits = set(re.findall(r"\d+", src))
    warns = []
    for n in sorted(set(re.findall(r"\d+", text)) - digits):
        if len(n) >= 2:
            warns.append(f"Nombre/date absent du formulaire : {n}")
    for e in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)):
        if e not in src:
            warns.append(f"E-mail absent du formulaire : {e}")
    if re.search(r"\[[^\]]+\]|X{3,}|\.{4,}", text):
        warns.append("Texte à compléter (crochets / XXX / pointillés) détecté.")
    return warns