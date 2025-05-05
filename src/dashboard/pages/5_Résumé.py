import streamlit as st
import pandas as pd
import os
import sys

# 📁 Chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "../../")))

from src.utils.dashboard_utils import summarize_text  # Assure-toi que summarize_text est bien importé

st.set_page_config(page_title="Résumé", layout="wide")
st.title("🧠 Résumé automatique des commentaires")

# ✅ Vérifie si les données sont déjà en session
if "df" not in st.session_state:
    st.warning("⚠️ Aucune donnée chargée. Veuillez lancer une recherche depuis la page d’accueil.")
    st.stop()

df = st.session_state["df"].copy()

@st.cache_data
def summarize_text_cached(df):
    return summarize_text(df)
# ✅ Bouton pour lancer le résumé
if st.button("📝 Générer le résumé"):
    with st.spinner("⏳ Résumé en cours..."):
        summary = summarize_text_cached(df)
        if "Erreur" in summary or "[Erreur" in summary:
            st.error("Une erreur est survenue lors du résumé.")
            st.text(summary)
        else:
            st.success("Résumé généré !")
            st.text(summary)
