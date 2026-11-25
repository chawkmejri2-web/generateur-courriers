import sys, pathlib, io
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from letters import LETTER_TYPES, all_fields, validate_form
from generator import mock_letter, letter_to_text, check_invention, parse_letter
from exporter import to_docx
from docx import Document
import pytest


def sample(t):
    d = {f.key: "Valeur 2026" for f in all_fields(t)}
    d.update(nom="Sara Ben Ali", email="sara@mail.tn", telephone="+216 20 123 456", date_lettre="24/11/2026")
    for f in all_fields(t):
        if f.kind == "select":
            d[f.key] = f.options[0]
    return d


@pytest.mark.parametrize("t", LETTER_TYPES)
def test_valid_form_all_types(t):
    assert validate_form(t, sample(t))[1] == {}


def test_required_and_email():
    d = sample("conge")
    d["nom"] = " "
    d["email"] = "pas-un-mail"
    errs = validate_form("conge", d)[1]
    assert "nom" in errs and "email" in errs


def test_at_least_four_types():
    assert len(LETTER_TYPES) >= 4


@pytest.mark.parametrize("t", LETTER_TYPES)
def test_structure_and_no_invention(t):
    d = sample(t)
    L = mock_letter(t, d)
    text = letter_to_text(d, L)
    assert all(L[k] for k in ("objet", "destinataire", "salutation", "corps", "politesse", "signature"))
    assert check_invention(d, text) == []


def test_invention_detected():
    d = sample("conge")
    bad = letter_to_text(d, mock_letter("conge", d)) + "\nTél : 71 999 888, contact@fake.com [à compléter]"
    assert len(check_invention(d, bad)) >= 3


def test_parse_json_and_missing_part():
    ok = '{"objet":"o","destinataire":"d","salutation":"s","corps":"c","politesse":"p","signature":"g"}'
    assert parse_letter("Voici:\n" + ok)["objet"] == "o"
    with pytest.raises(ValueError):
        parse_letter('{"objet":"o"}')


def test_docx_export():
    doc = Document(io.BytesIO(to_docx("Bonjour\nligne 2\n\nObjet : test")))
    assert "Objet : test" in [p.text for p in doc.paragraphs]