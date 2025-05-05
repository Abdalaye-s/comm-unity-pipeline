import streamlit as st
import pandas as pd

st.set_page_config(page_title="Détail Ville", layout="wide")

# CSS personnalisé (optionnel)
try:
    from pathlib import Path
    with open(Path(__file__).parent.parent / "assets" / "styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass  # Si le fichier n’existe pas, on n’arrête pas l’app

st.title("📍 Détail des avis ")

# 🧠 Vérifie que les données sont bien chargées
if "df" not in st.session_state or "ville" not in st.session_state:
    st.warning("⚠️ Aucune donnée trouvée. Veuillez d'abord lancer une analyse via la page d'accueil.")
    st.stop()

# 🔄 Récupère les données
df = st.session_state["df"]

# 📍 Ville en mémoire
ville_actuelle = st.session_state.get("ville", "")
villes_possibles = df["theme"].dropna().unique().tolist()

if not villes_possibles:
    st.info("Aucune ville disponible dans les données.")
    st.stop()

ville_selectionnee = st.selectbox(
    "Choisissez une ville pour explorer les avis :",
    villes_possibles,
    index=villes_possibles.index(ville_actuelle) if ville_actuelle in villes_possibles else 0
)

# 🔎 Filtrage
df_ville = df[df["theme"] == ville_selectionnee]

if df_ville.empty:
    st.info(f"Aucun avis trouvé pour {ville_selectionnee}.")
else:
    st.subheader(f"📝 Aperçu des commentaires pour {ville_selectionnee}")
    st.dataframe(df_ville[["text", "sentiment", "topics", "entities"]].head(20), use_container_width=True)

    st.subheader("📊 Statistiques de sentiment")
    sentiment_counts = df_ville["sentiment"].value_counts()
    st.bar_chart(sentiment_counts)
