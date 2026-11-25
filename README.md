# ✉️ Générateur intelligent de courriers administratifs

Mini-projet – Sujet 4. Application Streamlit qui génère des courriers administratifs structurés avec un LLM (Gemini), avec formulaires validés, prévisualisation modifiable, export DOCX, comparaison de prompts et contrôle anti-invention.

**Étudiants :** chawk mejri - maryem saffar

## 1. Installation

Prérequis : Python 3.10 ou plus (testé avec 3.14, 64 bits).

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # puis ouvrir .env et coller la clé API
```

Clé API Gemini gratuite : https://aistudio.google.com/apikey
Sans clé, l'application fonctionne en **mode démo** (modèles fixes, sans IA).

## 2. Lancement

```bash
streamlit run app.py
```
Puis ouvrir http://localhost:8501

## 3. Tests

```bash
python -m pytest -q
```
Résultat obtenu : **15 tests réussis** (validation des 5 types, champs obligatoires, e-mail invalide, structure du courrier, détection d'invention, parsing JSON, export DOCX).

## 4. Structure du projet

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit |
| `letters.py` | 5 types de courriers, champs, validation pydantic |
| `prompts.py` | Prompts A (simple) et B (contraint) |
| `generator.py` | Appel LLM, parsing JSON, mode démo, contrôle anti-invention |
| `exporter.py` | Export DOCX |
| `tests/test_core.py` | Tests pytest |

## 5. Bibliothèques et justification

| Outil | Rôle | Pourquoi ce choix |
|---|---|---|
| Streamlit | Interface web | Formulaires et téléchargement intégrés, 100 % Python, plus rapide que Flask + HTML/JS |
| google-genai (Gemini) | Génération du texte | API simple, offre gratuite, bon français, sortie JSON |
| pydantic | Validation des champs | Validation déclarative, messages d'erreur précis |
| python-docx | Export Word | Standard Python pour le format DOCX |
| python-dotenv | Lecture de la clé API | Garde la clé hors du code et de GitHub |
| pytest | Tests automatiques | Syntaxe simple, tests paramétrés |

## 6. Technique d'IA

- **LLM via API** : Gemini génère l'objet, le destinataire, la salutation, le corps, la formule de politesse et la signature (réponse JSON).
- **Prompt engineering** : deux formulations. **A** : simple. **B** : rôle, informations fournies comme seule source, liste des champs non fournis, consignes par partie, format JSON strict.
- **Anti-invention** : (1) l'en-tête (coordonnées, ville, date) est ajouté par le code ; (2) le prompt B interdit d'inventer ; (3) `check_invention` compare nombres, e-mails et textes « à compléter » du résultat avec le formulaire.

## 7. Résultats et comparaison des prompts

Test sur une réclamation (même formulaire) :

| Prompt | Alertes d'invention | Mots | Remarques |
|---|---|---|---|
| A | 0 | 103 | Doublon « ville, date » dans le bloc destinataire ; l'IA a interprété la date de l'incident comme date de la facture |
| B | 0 | 84 | Format propre, sans doublon, plus concis |

Conclusion : les deux prompts n'inventent pas de chiffres sur ce cas, mais B donne un courrier plus propre et plus fidèle au formulaire. B est donc le prompt par défaut.

## 8. Problèmes rencontrés et limites

- Python 32 bits incompatible avec Streamlit : installation de Python 64 bits.
- L'IA peut supposer le genre de l'utilisateur (« Je soussigné ») car le formulaire n'a pas ce champ.
- Aucune vérification de cohérence des dates (date de fin avant date de début, date d'incident après la lettre).
- `check_invention` détecte les nombres, e-mails et textes à compléter, mais pas les erreurs de sens.
- Améliorations possibles : champ « genre », validation des dates, export PDF.

## 9. Démonstration

1. Choisir un type de courrier et laisser des champs vides (erreurs de validation).
2. Remplir le formulaire et générer.
3. Modifier le texte, puis exporter en DOCX.
4. Comparer les prompts A et B.