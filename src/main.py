# ✅ 2. main.py (MODIFIÉ)

import sys
import os
import argparse
import pandas as pd
from deep_translator import GoogleTranslator
from langdetect import detect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Ajouter le chemin racine du projet
model_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "camembert_sentiment_model"))

from src.scraping.scrape_city_by_themes import scrape_city_by_themes
from src.utils.data_cleaning import clean_text
from src.sentiment_analysis.predict_sentiment import predict_sentiment
from src.theme_detection.exctract_topics_hybride import extract_topics_hybride
from src.theme_detection.extract_topics_with_sentiment import extract_topics_with_sentiment
from src.theme_detection.detect_themes_safe import detect_theme_safe
from src.theme_detection.ner_entity_extraction import extract_named_entities
from src.scraping.twitter_scraper import get_tweets
import streamlit as st
from src.scraping.scrape_city_by_themes import is_entreprise

# Essayez d’utiliser st.secrets, et fallback sur os.getenv en local
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except KeyError:
        import os
        return os.getenv(key, default)

THRESHOLD = float(get_secret("THRESHOLD")) 

def translate_to_french_if_needed(text):
    try:
        lang = detect(text)
        if lang != "fr":
            return GoogleTranslator(source='auto', target='fr').translate(text)
        return text
    except Exception as e:
        print(f"⚠️ Erreur de traduction ou détection de langue : {e}")
        return text


def safe_scraper(func):
    try:
        return func()
    except Exception as e:
        print(f"⚠️ Erreur dans {func.__name__}: {e}")
        return pd.DataFrame()

def to_dataframe_if_needed(data):
    return data if isinstance(data, pd.DataFrame) else pd.DataFrame()

def run_pipeline(entite):
    # Barre de progression globale
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(f"📅 Scraping des données pour : {entite}...")
    tweets = safe_scraper(lambda: get_tweets(entite))
    reviews = safe_scraper(lambda: scrape_city_by_themes(entite))
    reviews = to_dataframe_if_needed(reviews)
    progress_bar.progress(10)

    if reviews.empty:
        st.error("❌ Aucun commentaire récupéré, arrêt du pipeline.")
        return pd.DataFrame()
    
    df = pd.concat([reviews, tweets], ignore_index=True)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    
    status_text.text(" Nettoyage du texte...")
    df["text_clean"] = df["text"].astype(str).apply(clean_text)
    progress_bar.progress(20)

    status_text.text(" Traduction vers le français si nécessaire...")
    df["text_clean"] = df["text_clean"].apply(translate_to_french_if_needed)
    progress_bar.progress(30)

    status_text.text(" Analyse de sentiment...")
    df["sentiment"] = df["text_clean"].apply(predict_sentiment)
    progress_bar.progress(40)

    sentiment_map = {"Positif/Neutre": 1, "Négatif": 0}
    df["sentiment_score"] = df["sentiment"].map(sentiment_map)

    status_text.text(" Extraction des sujets...")
    df["topics"] = df["text_clean"].apply(lambda x: extract_topics_hybride(x, top_n=5))
    progress_bar.progress(60)
    
    # ... (suite de votre fonction)
    status_text.text(" Extraction des sujets avec sentiment...")
    df["topics_with_sentiment"] = df["text_clean"].apply(lambda x: extract_topics_with_sentiment(x, top_n=5))
    progress_bar.progress(75)

    status_text.text(" Détection des thématiques...")
    df["theme"] = df["text_clean"].apply(lambda x: detect_theme_safe(x, entite, threshold=THRESHOLD))
    progress_bar.progress(85)

    status_text.text(" Extraction des entités nommées...")
    df["entities"] = df["text_clean"].apply(extract_named_entities)
    progress_bar.progress(100)
    status_text.text(f" Pipeline terminé - {len(df)} commentaires analysés")


    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entite", type=str, required=True)
    args = parser.parse_args()
    result_df = run_pipeline(args.entite)
    result_df.to_csv("comments_annotated.csv", index=False)
