# dashboard.py — Vue d’ensemble améliorée Comm'Unity
import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from collections import Counter
from datetime import datetime
import ast
import base64

# Configuration de la page
st.set_page_config(page_title="Comm’Unity – Vue d’ensemble", layout="wide")

# 📁 Setup des chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "../../")))

# 🖼️ Logo et Style
logo_path = os.path.join(CURRENT_DIR, "logo.png")
css_path = os.path.join(CURRENT_DIR, "assets", "styles.css")

if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ✅ Header
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style='display: flex; align-items: center;'>
            <img src='data:image/png;base64,{logo_base64}' width='50'>
            <h1 style='padding-left: 1rem; color:#4A90E2;'>Comm’Unity – Vue d’ensemble</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("### Comm’Unity – Vue d’ensemble")
    st.warning("Logo non trouvé.")

st.markdown("Suivez l'évolution des ressentis dans votre **ville** ou votre **organisation**.")
st.markdown("---")

# 🧠 Initialisation session
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# 🔍 Entrée utilisateur
with st.expander("🔎 Lancer une nouvelle analyse", expanded=not st.session_state.data_loaded):
    ville = st.text_input("Nom de la ville ou de l'entreprise:", placeholder="Ex: Gennevilliers")
    btn = st.button("🚀 Lancer")

    if btn and ville:
        from src.utils.data_loader import load_data  # <-- à adapter si nécessaire

        with st.spinner(f"Chargement des données pour {ville}..."):
            df = load_data(ville)

        if df is not None and not df.empty:
            if "df" in st.session_state:
                colonnes_uniques = ["time", "text", "ville"]  # ou adapte à ton modèle
                st.session_state["df"] = (
                    pd.concat([st.session_state["df"], df], ignore_index=True)
                    .drop_duplicates(subset=colonnes_uniques)
                )
                st.session_state["ville"] += f", {ville}"
            else:
                st.session_state["df"] = df
                st.session_state["ville"] = ville


            st.session_state.data_loaded = True
            st.success("✅ Données chargées.")
            st.experimental_rerun()
        else:
            st.error("Aucune donnée trouvée.")

if not st.session_state.get("df", pd.DataFrame()).empty:
    df = st.session_state.df
else:
    st.stop()

# 🧹 Pré-traitement
df.columns = df.columns.str.strip().str.lower()
if "time" in df.columns:
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
if "topics_with_sentiment" in df.columns:
    def safe_parse(x): return ast.literal_eval(x) if isinstance(x, str) else x
    df["topics_with_sentiment"] = df["topics_with_sentiment"].apply(safe_parse)

# 🧾 Filtres latéraux
with st.sidebar:
    st.markdown("## 🎛️ Filtres")
    
    if "ville" in df.columns:
        villes = sorted(df["ville"].dropna().unique())
        filtres_ville = st.multiselect("🏙️ Villes :", villes, default=villes)
        df = df[df["ville"].isin(filtres_ville)]

    if "time" in df.columns and not df["time"].isna().all():
        min_date, max_date = df["time"].min().date(), df["time"].max().date()
        start, end = st.date_input("🗓️ Période :", [min_date, max_date])
        df = df[(df["time"].dt.date >= start) & (df["time"].dt.date <= end)]

    if "thematic_query" in df.columns:
        themes = ["Toutes"] + sorted(df["thematic_query"].dropna().unique().tolist())
        choix_theme = st.selectbox("🎯 Thématique :", themes)
        if choix_theme != "Toutes":
            df = df[df["thematic_query"] == choix_theme]

# 🧩 Résumé
nb_comments = len(df)
entite_label = "ville" if "ville" in df.columns else "entité"
nom_affiche = st.session_state.get("ville", "Inconnue")
st.markdown(f"### 📊 Résultats pour : **{nom_affiche}** – {nb_comments} commentaires")

# 📍 Analyse thématique
tab1, tab2 = st.tabs(["📌 Sujets les plus mentionnés", "🔍 Sujets avec sentiment"])

with tab1:
    if "topics" in df.columns and df["topics"].notna().any():
        flat_topics = sum(df["topics"].dropna(), [])
        top_topics = pd.DataFrame(Counter(flat_topics).most_common(10), columns=["Sujet", "Occurrences"])
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=top_topics, x="Occurrences", y="Sujet", palette="Blues_d", ax=ax)
        st.pyplot(fig)
        st.dataframe(top_topics)
    else:
        st.info("Aucun sujet détecté.")

with tab2:
    if "topics_with_sentiment" in df.columns and df["topics_with_sentiment"].notna().any():
        flat = sum(df["topics_with_sentiment"].dropna(), [])
        if flat:
            df_sent = pd.DataFrame(flat, columns=["Sujet", "Sentiment"])
            top_sentiments = df_sent["Sujet"].value_counts().nlargest(10).index.tolist()
            df_sent = df_sent[df_sent["Sujet"].isin(top_sentiments)]
            chart = alt.Chart(df_sent).mark_bar().encode(
                x="count():Q",
                y=alt.Y("Sujet:N", sort="-x"),
                color="Sentiment:N"
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(df_sent)
        else:
            st.info("Pas de sujet avec sentiment associé.")
    else:
        st.info("Aucune donnée sentimentale détectée.")

# 🔁 Réinitialisation
if st.button("🔄 Réinitialiser"):
    for key in ["df", "ville", "data_loaded"]:
        st.session_state.pop(key, None)
    st.experimental_rerun()

# 📎 Pied de page
st.markdown("<hr><center>© 2025 Comm’Unity – Analyse citoyenne intelligente</center>", unsafe_allow_html=True)
