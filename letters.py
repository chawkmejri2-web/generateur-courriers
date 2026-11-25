"""Types de courriers, champs de formulaire et validation (pydantic)."""
from dataclasses import dataclass
from typing import Annotated
from pydantic import ValidationError, StringConstraints, create_model

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE = r"^[+\d][\d\s().-]{5,}$"


@dataclass(frozen=True)
class F:
    key: str
    label: str
    kind: str = "text"  # text | textarea | date | email | phone | select
    required: bool = True
    options: tuple = ()


COMMON = [
    F("nom", "Nom et prénom"), F("adresse", "Adresse", required=False),
    F("email", "E-mail", "email", False), F("telephone", "Téléphone", "phone", False),
    F("dest_nom", "Destinataire (personne ou service)"),
    F("dest_adresse", "Adresse du destinataire", required=False),
    F("ville", "Ville"), F("date_lettre", "Date de la lettre", "date"),
]

LETTER_TYPES = {
    "conge": {"label": "Demande de congé", "fields": [
        F("poste", "Poste / service"),
        F("type_conge", "Type de congé", "select", options=("Annuel", "Maladie", "Sans solde", "Exceptionnel")),
        F("date_debut", "Date de début", "date"), F("date_fin", "Date de fin", "date"),
        F("motif", "Motif (facultatif)", "textarea", False)]},
    "attestation": {"label": "Demande d'attestation", "fields": [
        F("type_attestation", "Type d'attestation", "select", options=("de travail", "de scolarité", "de stage", "de salaire")),
        F("reference", "Matricule / n° étudiant (facultatif)", required=False),
        F("usage", "Usage prévu de l'attestation", "textarea")]},
    "reclamation": {"label": "Réclamation", "fields": [
        F("sujet", "Sujet de la réclamation"), F("date_incident", "Date de l'incident", "date"),
        F("description", "Description des faits", "textarea"),
        F("montant", "Montant concerné (facultatif)", required=False),
        F("attendu", "Résultat attendu", "textarea")]},
    "stage": {"label": "Candidature à un stage", "fields": [
        F("poste", "Stage / poste visé"), F("formation", "Formation actuelle"),
        F("competences", "Compétences principales", "textarea"),
        F("duree", "Durée souhaitée"), F("disponibilite", "Disponible à partir du", "date")]},
    "demission": {"label": "Lettre de démission", "fields": [
        F("poste", "Poste occupé"), F("date_effet", "Date de départ souhaitée", "date"),
        F("preavis", "Préavis (facultatif)", required=False),
        F("motif", "Motif (facultatif)", "textarea", False)]},
}


def all_fields(type_key):
    return COMMON + LETTER_TYPES[type_key]["fields"]


def _model(type_key):
    spec = {}
    for f in all_fields(type_key):
        pattern = {"email": EMAIL, "phone": PHONE}.get(f.kind)
        if f.required:
            t = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=pattern)]
            spec[f.key] = (t, ...)
        else:
            p = f"^$|{pattern}" if pattern else None
            spec[f.key] = (Annotated[str, StringConstraints(strip_whitespace=True, pattern=p)], "")
    return create_model("Form_" + type_key, **spec)


def validate_form(type_key, raw):
    """Retourne (données nettoyées, erreurs {champ: message})."""
    labels = {f.key: f.label for f in all_fields(type_key)}
    try:
        return _model(type_key)(**raw).model_dump(), {}
    except ValidationError as e:
        errs = {}
        for err in e.errors():
            k = err["loc"][0]
            msg = "est obligatoire" if err["type"] in ("string_too_short", "missing") else "a un format invalide"
            errs[k] = f"{labels[k]} {msg}."
        return {}, errs