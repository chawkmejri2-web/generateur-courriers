from generator import generate, letter_to_text, check_invention

data = {"nom": "Sara Ben Ali", "adresse": "", "email": "", "telephone": "",
        "dest_nom": "Direction des ressources humaines", "dest_adresse": "",
        "ville": "Sousse", "date_lettre": "25/11/2026", "poste": "Comptable",
        "type_conge": "Annuel", "date_debut": "01/12/2026", "date_fin": "10/12/2026",
        "motif": "Voyage familial"}

for mock in (True, False):
    L = generate("conge", data, "B", mock=mock)
    text = letter_to_text(data, L)
    print("=== MODE DÉMO ===" if mock else "=== IA GEMINI ===")
    print(text)
    print("ALERTES :", check_invention(data, text))
    print()