import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import seaborn as sns
import matplotlib.pyplot as plt
st.set_page_config(page_title="Analyse de sentiment", layout="wide")
st.title(" Analyse de sentiment")

# Utiliser les données partagées depuis la page d'accueil
if "df" not in st.session_state:
    st.warning("⚠️ Aucune donnée trouvée. Veuillez lancer une recherche depuis la page d’accueil.")
    st.stop()

df = st.session_state["df"].copy()  # Copie pour éviter les modifications sur l'original

def safe_parse_topics(x):
    try:
        if isinstance(x, str):
            return ast.literal_eval(x)
        elif isinstance(x, list):
            return x
    except Exception:
        pass
    return []


#  Prétraitements
df["sentiment"] = df["sentiment"].fillna("Inconnu").astype(str).str.strip()
df["topics"] = df["topics"].apply(safe_parse_topics)

#  Aperçu
st.dataframe(df.head())

#  Distribution des sentiments
if not df.empty:
    df["sentiment"] = (
        df["sentiment"]
        .fillna("Inconnu")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
        .str.capitalize()
    )

st.subheader("Distribution des sentiments")

sentiment_counts = df["sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Nombre"]
sentiment_counts["Pourcentage"] = (sentiment_counts["Nombre"] / sentiment_counts["Nombre"].sum() * 100).round(1)
# Debugging: Print sentiment_counts to verify data
print("Sentiment Counts:")
print(sentiment_counts)
sentiment_counts=pd.DataFrame(sentiment_counts)
# Create a pie chart
fig = px.pie(
    sentiment_counts,
    names="Sentiment",
    values="Nombre",
    title="Distribution des sentiments"
)
print(fig)

# Display the pie chart
st.plotly_chart(fig, use_container_width=True)

#  Sélection par type de sentiment
st.subheader("Thématiques par sentiment")
sentiment_choice = st.selectbox("Filtrer par sentiment :", options=["Tous"] + list(df["sentiment"].unique()))

filtered_df = df if sentiment_choice == "Tous" else df[df["sentiment"] == sentiment_choice]

# Aplatir les topics pour les compter
all_topics = [t for sublist in filtered_df["topics"] for t in sublist]
if all_topics:
    topic_freq = pd.Series(all_topics).value_counts().reset_index()
    topic_freq.columns = ["Thématique", "Nombre"]
    # Sort the DataFrame by "Nombre" in descending order
    topic_freq = topic_freq.sort_values(by="Nombre", ascending=True)
    fig_topics = px.bar(topic_freq, x="Nombre", y="Thématique", orientation="h", title="Fréquence des thématiques")
    st.plotly_chart(fig_topics, use_container_width=True)
else:
    st.info("Aucune thématique disponible pour ce filtre.")
