# comparaison.py – Comparaison entre entités (villes ou entreprises)
import os
import sys
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ⚙️ Config de page
st.set_page_config(page_title="Comm'Unity – Comparaison", layout="wide")

# 📁 Réglage des chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "../../")))

# 🧠 Initialisation session
if "selected_entities" not in st.session_state:
    st.session_state.selected_entities = []

# 🎯 Titre
st.title("📊 Comparaison entre entités")
st.markdown("Comparez les ressentis entre plusieurs **villes** ou **entreprises** chargées dans l’onglet Accueil.")

# 🔍 Vérification des données
if "df" not in st.session_state or st.session_state["df"].empty:
    st.warning("Aucune donnée disponible. Veuillez d'abord effectuer une recherche dans l'onglet Accueil.")
    st.stop()

df = st.session_state["df"]
df.columns = df.columns.str.strip().str.lower()

# 🧠 Détection intelligente de l'identifiant
if "ville" in df.columns:
    identifiant_col = "ville"
elif "entite" in df.columns:
    identifiant_col = "entite"
elif "thematic_query" in df.columns:
    identifiant_col = "thematic_query"
else:
    st.error("Aucune colonne identifiable pour la comparaison ('ville', 'entite', 'thematic_query').")
    st.stop()

# 🎯 Filtrage par type d’entité
with st.sidebar:
    st.markdown("## 🔍 Filtres")
    if "type_entite" in df.columns:
        type_selection = st.selectbox("Type d'entité :", ["Tous", "ville", "entreprise"])
        if type_selection != "Tous":
            df = df[df["type_entite"] == type_selection]

    # ✅ Sélection des entités disponibles
    entities_available = sorted(df[identifiant_col].dropna().unique().tolist())
    selected = st.multiselect(
        "Sélectionnez les entités à comparer :",
        options=entities_available,
        default=st.session_state.selected_entities
    )

    if selected != st.session_state.selected_entities:
        st.session_state.selected_entities = selected

# 🔍 Vérification sélection
if not selected:
    st.info("Veuillez sélectionner au moins une entité.")
    st.stop()

# 📊 Données filtrées
df_filtré = df[df[identifiant_col].isin(selected)]

# 📈 Sentiments
if "sentiment" in df.columns:
    st.markdown("### 📈 Répartition des sentiments par entité")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=df_filtré, x=identifiant_col, hue="sentiment", palette="Set2", ax=ax)
    ax.set_xlabel("Entité")
    ax.set_ylabel("Nombre de commentaires")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("La colonne 'sentiment' est absente des données.")

# 🧩 Thématiques
theme_col = "thematic_query" if "thematic_query" in df.columns else "theme" if "theme" in df.columns else None

if theme_col:
    st.markdown("### 🧩 Répartition des thématiques")
    theme_df = df_filtré.groupby([identifiant_col, theme_col]).size().reset_index(name="Nombre")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=theme_df, x="Nombre", y=theme_col, hue=identifiant_col, ax=ax2)
    plt.title("Thématiques dominantes par entité")
    st.pyplot(fig2)
else:
    st.info("Aucune colonne de thématique disponible pour cette comparaison.")

# 📁 Export CSV
st.markdown("### 💾 Export des données")
csv_data = df_filtré.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Télécharger les données filtrées", data=csv_data, file_name="comparaison.csv", mime="text/csv")

