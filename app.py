import datetime as dt
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from letters import LETTER_TYPES, all_fields, validate_form
from generator import generate, letter_to_text, check_invention, api_available
from exporter import to_docx

st.set_page_config(page_title="Courriers administratifs IA", page_icon="✉️", layout="wide")
st.title("✉️ Générateur intelligent de courriers administratifs")

with st.sidebar:
    ttype = st.selectbox("Type de courrier", list(LETTER_TYPES), format_func=lambda k: LETTER_TYPES[k]["label"])
    variant = st.radio("Formulation du prompt", ["A", "B"], index=1,
                       format_func=lambda v: {"A": "A – simple", "B": "B – contrainte (anti-invention)"}[v])
    mock = st.toggle("Mode démo hors-ligne (sans API)", value=not api_available())
    if not api_available() and not mock:
        st.warning("GEMINI_API_KEY absente : activez le mode démo ou renseignez le fichier .env")

tab1, tab2 = st.tabs(["1. Générer", "2. Comparer les prompts"])

with tab1:
    values = {}
    with st.form(f"form_{ttype}"):
        cols = st.columns(2)
        for i, f in enumerate(all_fields(ttype)):
            k, lab = f"{ttype}_{f.key}", f.label + (" *" if f.required else "")
            with cols[i % 2]:
                if f.kind == "date":
                    values[f.key] = st.date_input(lab, dt.date.today(), format="DD/MM/YYYY", key=k).strftime("%d/%m/%Y")
                elif f.kind == "textarea":
                    values[f.key] = st.text_area(lab, key=k)
                elif f.kind == "select":
                    values[f.key] = st.selectbox(lab, f.options, key=k)
                else:
                    values[f.key] = st.text_input(lab, key=k)
        submitted = st.form_submit_button("Générer le courrier", type="primary")
    if submitted:
        clean, errors = validate_form(ttype, values)
        if errors:
            for m in errors.values():
                st.error(m)
        else:
            try:
                with st.spinner("Génération en cours..."):
                    L = generate(ttype, clean, variant, mock)
                st.session_state.update(data=clean, type=ttype, edited=letter_to_text(clean, L))
            except Exception as e:
                st.error(f"Échec de la génération : {e}")
    if "edited" in st.session_state:
        st.subheader("Prévisualisation (modifiable)")
        txt = st.text_area("Modifiez le texte avant validation", key="edited", height=480)
        for w in check_invention(st.session_state["data"], txt):
            st.warning("⚠️ " + w)
        st.download_button("✅ Valider et exporter en DOCX", to_docx(txt), "courrier.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

with tab2:
    st.write("Génère le même courrier avec les prompts A et B à partir du dernier formulaire validé.")
    if "data" not in st.session_state:
        st.info("Générez d'abord un courrier dans l'onglet 1.")
    elif st.button("Comparer A et B"):
        c = st.columns(2)
        for col, v in zip(c, ("A", "B")):
            try:
                txt = letter_to_text(st.session_state["data"], generate(st.session_state["type"], st.session_state["data"], v, mock))
                w = check_invention(st.session_state["data"], txt)
                with col:
                    st.subheader(f"Prompt {v}")
                    st.metric("Alertes d'invention", len(w))
                    st.metric("Mots", len(txt.split()))
                    for x in w:
                        st.warning(x)
                    st.text_area("Résultat", txt, height=400, key=f"cmp_{v}")
            except Exception as e:
                col.error(str(e))