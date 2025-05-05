import streamlit as st
import pandas as pd
import plotly.express as px
import ast

st.set_page_config(page_title="Thématiques", layout="wide")
st.title("📌 Analyse par thématique")

# ✅ Utiliser les données partagées depuis la page d’accueil
if "df" not in st.session_state:
    st.warning("⚠️ Aucune donnée trouvée. Veuillez lancer une recherche depuis la page d’accueil.")
    st.stop()

df = st.session_state["df"].copy()

# ✅ Affichage des colonnes (optionnel pour debug)
st.dataframe(df.head())
st.write("Colonnes du DataFrame :", df.columns.tolist())

def safe_parse_topics(x):
    try:
        if isinstance(x, str):
            return ast.literal_eval(x)
        elif isinstance(x, list):
            return x
    except Exception:
        pass
    return []



if "topics" not in df.columns:
    st.warning("Aucune colonne 'topics' dans les données.")
else:
    # ✅ Convertir les chaînes de topics en listes
    df["topics"] = df["topics"].apply(safe_parse_topics)

    # Aplatir toutes les listes de thématiques
    all_topics = [topic.strip().lower() for sublist in df["topics"] for topic in sublist if topic]

    # ✅ Affichage du graphe
    if all_topics:
        topic_freq = pd.Series(all_topics).value_counts().reset_index()
        topic_freq.columns = ["Thématique", "Nombre"]

        fig = px.bar(topic_freq, x="Nombre", y="Thématique", orientation="h", title="Fréquence des thématiques")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune thématique détectée dans la colonne 'topics'.")