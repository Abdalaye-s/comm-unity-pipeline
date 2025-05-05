# ✅ 2. main.py (MODIFIÉ)

import sys
import os
import argparse
import pandas as pd
from deep_translator import GoogleTranslator
from langdetect import detect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.scraping.scrape_city_by_themes import scrape_city_by_themes
from src.utils.data_cleaning import clean_text
from src.sentiment_analysis.predict_sentiment import predict_sentiment
from src.theme_detection.exctract_topics_hybride import extract_topics_hybride
from src.theme_detection.extract_topics_with_sentiment import extract_topics_with_sentiment
from src.theme_detection.detect_themes_safe import detect_theme_safe
from src.theme_detection.ner_entity_extraction import extract_named_entities
from src.scraping.twitter_scraper import get_tweets
from dotenv import load_dotenv
from src.scraping.scrape_city_by_themes import is_entreprise

load_dotenv()
THRESHOLD = float(os.getenv("THRESHOLD", "0.35"))


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
    print(f"📅 Scraping des données pour : {entite}...")
    #tweets= safe_scraper(lambda: get_tweets(entite))
    tweets = pd.DataFrame(columns=["text", "time"])  # DataFrame vide mais valide
    reviews = safe_scraper(lambda: scrape_city_by_themes(entite))
    reviews = to_dataframe_if_needed(reviews)

    if reviews.empty:
        print("❌ Aucun commentaire récupéré, arrêt du pipeline.")
        return pd.DataFrame()

    df = pd.concat([reviews, tweets], ignore_index=True)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    
    print("🕵️ Nettoyage du texte...")
    df["text_clean"] = df["text"].astype(str).apply(clean_text)

  
    
    print("🌍 Traduction vers le français (si nécessaire)...")
    df["text_clean"] = df["text_clean"].apply(translate_to_french_if_needed)



    print("🧐 Analyse de sentiment...")
    df["sentiment"] = df["text_clean"].apply(predict_sentiment)
    


    sentiment_map = {
    "Positif/Neutre": 1,
    "Négatif": 0
    }
    df["sentiment_score"] = df["sentiment"].map(sentiment_map)


    print("📊 Extraction des sujets...")
    df["topics"] = df["text_clean"].apply(lambda x: extract_topics_hybride(x, top_n=5))


    print("🔎 Exemple de texte nettoyé :")
    print(df["text_clean"].dropna().head(5).to_list())

    print("🔎 Exemples de topics extraits :")
    print(df["topics"].dropna().head(5).to_list())

    print("📊 Extraction des sujets avec sentiment...")
    df["topics_with_sentiment"] = df["text_clean"].apply(lambda x: extract_topics_with_sentiment(x, top_n=5))


    print("🏷️ Détection des thématiques...")
    df["theme"] = df["text_clean"].apply(lambda x: detect_theme_safe(x, entite, threshold=THRESHOLD))
    
    print("🧐 Extraction des entités nommées...")
    df["entities"] = df["text_clean"].apply(extract_named_entities)

    print("✅ Colonnes disponibles :", df.columns.tolist())

    output_path = "comments_annotated.csv"
    print(f"📀 Sauvegarde des résultats dans {output_path}...")
    df.to_csv(output_path, index=False)

    print(f"✅ Pipeline terminé. {len(df)} commentaires sauvegardés.")
    df["type_entite"] = "entreprise" if is_entreprise(entite) else "ville"
    df["ville"] = "" if is_entreprise(entite) else entite

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de scraping, nettoyage et analyse.")
    parser.add_argument("--entite", type=str, required=True, help="Nom de l'entité à analyser (ex: Gennevilliers)")
    args = parser.parse_args()
    df_final = run_pipeline(args.entite)

    if not df_final.empty:
        print(df_final.head())
