import sys
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from fpdf import FPDF


# 📂 Ajouter chemin racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.main import run_pipeline
# 🌿 Configuration Streamlit
st.set_page_config(page_title="Comm’unity - La ville en temps réel", page_icon="🏙️", layout="wide")

# 🎨 Custom CSS pour améliorer l'apparence
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #eaf4f4;
        }
        .css-1d391kg { 
            background-color: #f9f9f9; 
        }
        .stButton button {
            background-color: #84c69b;
            color: white;
            border-radius: 10px;
            height: 50px;
            width: 100%;
            font-size: 18px;
        }
        footer {
            visibility: hidden;
        }
        footer:after {
            content:'Comm’unity - La ville en temps réel © 2025'; 
            visibility: visible;
            display: block;
            text-align: center;
            padding: 20px;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

# Trouver le chemin absolu du fichier en fonction de la localisation du script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(CURRENT_DIR, "logo.png")
# 📸 Logo dans la sidebar
st.sidebar.image(logo_path, width=250)



# 🛠️ Sidebar
st.sidebar.title("🛠️ Filtres Comm’unity")

# 🔍 Input de recherche
entite = st.sidebar.text_input("Entrez le nom de la ville ou de l'entreprise :", "Gennevilliers")

# 📥 Analyse
if st.sidebar.button("🚀 Lancer l'analyse"):
    with st.spinner("⏳ Analyse en cours, merci de patienter..."):
        df = run_pipeline(entite)
        st.success("✅ Analyse terminée !")

    if not df.empty:
        st.title(f"💬 Résultats pour '{entite}'")
        st.write(f"**{len(df)} commentaires analysés.**")
        st.dataframe(df)

        # Graphique 1 : Sujets
        all_topics = sum(df["topics"], [])
        topics_counter = Counter(all_topics)

        def plot_common_topics(counter, top_n=10):
            top_topics = counter.most_common(top_n)
            topics_df = pd.DataFrame(top_topics, columns=["Topic", "Count"])
            plt.figure(figsize=(12, 6))
            sns.barplot(data=topics_df, x="Count", y="Topic", palette="crest")
            plt.title("🔍 Sujets les plus abordés")
            st.pyplot(plt)

        st.subheader("🔝 Sujets les plus fréquents")
        plot_common_topics(topics_counter)

        # Graphique 2 : Thématiques
        theme_counts = df["theme"].value_counts().reset_index()
        theme_counts.columns = ["Thématique", "Occurrences"]

        def plot_common_themes(theme_df, top_n=10):
            plt.figure(figsize=(12, 6))
            sns.barplot(data=theme_df.head(top_n), x="Occurrences", y="Thématique", palette="flare")
            plt.title("🎯 Thématiques les plus abordées")
            st.pyplot(plt)

        st.subheader("🔝 Thématiques les plus fréquentes")
        plot_common_themes(theme_counts)

        # Table Sujet-Sentiment
        st.subheader("📊 Sujets avec sentiment")
        topics_with_sentiment = sum(df["topics_with_sentiment"], [])
        topics_sentiment_df = pd.DataFrame(topics_with_sentiment, columns=["Topic", "Sentiment"])
        st.dataframe(topics_sentiment_df)

        # 📄 Rapport PDF
        def generer_rapport_pdf(df, topics_counter, topics_sentiment_df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Rapport d'Analyse des Commentaires", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Nombre total de commentaires : {len(df)}", ln=True)
            pdf.ln(10)
            pdf.cell(200, 10, txt="🔝 Sujets les plus fréquents :", ln=True)
            for topic, count in topics_counter.most_common(10):
                pdf.cell(200, 10, txt=f"- {topic} : {count} occurrences", ln=True)
            pdf.ln(10)
            pdf.cell(200, 10, txt="📊 Sujets avec sentiment :", ln=True)
            for _, row in topics_sentiment_df.iterrows():
                pdf.cell(200, 10, txt=f"- {row['Topic']} : {row['Sentiment']}", ln=True)
            pdf.output("rapport_analyse_commentaires.pdf")
            st.success("✅ Rapport PDF généré avec succès : rapport_analyse_commentaires.pdf")

        if st.button("📄 Générer le rapport PDF"):
            generer_rapport_pdf(df, topics_counter, topics_sentiment_df)
    else:
        st.warning(f"⚠️ Aucune donnée trouvée pour '{entite}'.")
