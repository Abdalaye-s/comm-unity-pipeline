import streamlit as st
import pandas as pd
from collections import Counter
import os
import sys
import base64

# Configuration de la page
st.set_page_config(page_title=" Gagnez du temps avec votre rapport automatique", layout="wide")
st.title("⏱ Gagnez du temps avec votre rapport automatique")

#  Chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "../../")))

from src.utils.dashboard_utils import create_pdf, summarize_text, safe_parse_topics_with_sentiment

#  Utilisation des données filtrées si dispo
if "df" not in st.session_state:
    st.warning("⚠️ Aucune donnée chargée. Veuillez lancer une recherche depuis la page d’accueil.")
    st.stop()

df = st.session_state["df"]
ville = st.session_state.get("ville", "votre ville")

# Aperçu des données
st.write(f"Aperçu des données exportables pour **{ville}** :")
st.dataframe(df.head(20))

# Export CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="💾 Télécharger au format CSV",
    data=csv,
    file_name=f'resultats_opinion_{ville.lower().replace(" ", "_")}.csv',
    mime='text/csv'
)

#  Préparation des sujets
if "topics" in df.columns:
    df["topics"] = df["topics"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

if "topics_with_sentiment" in df.columns:
    df["topics_with_sentiment"] = df["topics_with_sentiment"].apply(safe_parse_topics_with_sentiment)

topics_counter = Counter(df["topics"].explode()) if "topics" in df.columns else Counter()


#  Préparer DataFrame de sujets avec sentiments
topics_sentiment = []
if "topics_with_sentiment" in df.columns:
    for row in df["topics_with_sentiment"]:
        for item in row:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                topic = item[0]
                sentiment = item[1]
                score = item[2] if len(item) > 2 else None
            topics_sentiment.append({"topic": topic, "sentiment": sentiment, "sentiment_score": score})
topics_sentiment_df = pd.DataFrame(topics_sentiment).drop_duplicates("topic") if topics_sentiment else pd.DataFrame(columns=["topic", "sentiment", "sentiment_score"])


#  Export PDF
if st.button("📄 Générer le rapport PDF"):
    with st.spinner("⏳ Génération du PDF en cours..."):
        try:
            pdf_path = create_pdf(df, topics_counter=topics_counter, topics_sentiment_df=topics_sentiment_df)
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="rapport_commentaires_{ville.lower().replace(" ", "_")}.pdf">📥 Télécharger le rapport PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")
