import sys
import os
import argparse
import pandas as pd

# Ajouter le chemin racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.scraping.twitter_scraper import get_tweets
from src.scraping.google_reviews_scraper import get_reviews_for_entity
from src.utils.data_cleaning import clean_text
from src.sentiment_analysis.predict_sentiment import predict_sentiment
from src.theme_detection.exctract_topics_hybride import extract_topics_hybride
from src.theme_detection.extract_topics_with_sentiment import extract_topics_with_sentiment
from src.theme_detection.detect_themes_safe import detect_theme_safe
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
THRESHOLD = float(os.getenv("THRESHOLD", "0.35"))

def safe_scraper(func):
    try:
        return func()
    except Exception as e:
        print(f"⚠️ Erreur dans {func.__name__}: {e}")
        return pd.DataFrame()

def to_dataframe_if_needed(data):
    return data if isinstance(data, pd.DataFrame) else pd.DataFrame()

def run_pipeline(entite):
    print(f"📥 Scraping des données pour : {entite}...")

    reviews = safe_scraper(lambda: get_reviews_for_entity(entite))
    #tweets = safe_scraper(lambda: get_tweets(entite))

    reviews = to_dataframe_if_needed(reviews)
    #tweets = to_dataframe_if_needed(tweets)

    if reviews.empty :#and tweets.empty:
        print("❌ Aucun commentaire récupéré, arrêt du pipeline.")
        return pd.DataFrame()

    print("🔗 Fusion des données...")
    df = pd.concat([reviews], ignore_index=True)#, tweets

    print("🧹 Nettoyage du texte...")
    df["text_clean"] = df["text"].astype(str).apply(clean_text)

    print("🧠 Analyse de sentiment...")
    df["sentiment"] = df["text_clean"].apply(predict_sentiment)

    print("📊 Extraction des sujets...")
    df["topics"] = df["text_clean"].apply(lambda x: extract_topics_hybride(x, top_n=5))

    print("📊 Extraction des sujets avec sentiment...")
    df["topics_with_sentiment"] = df["text_clean"].apply(lambda x: extract_topics_with_sentiment(x, top_n=5))

    print("🏷️ Détection des thématiques...")
    df["theme"] = df["text_clean"].apply(lambda x: detect_theme_safe(x, entite, threshold=THRESHOLD))

    output_path = "comments_annotated.csv"
    print(f"💾 Sauvegarde des résultats dans {output_path}...")
    df.to_csv(output_path, index=False)

    print(f"✅ Pipeline terminé. {len(df)} commentaires sauvegardés.")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de scraping, nettoyage et analyse.")
    parser.add_argument("--entite", type=str, required=True, help="Nom de l'entité à analyser (ex: Gennevilliers)")

    args = parser.parse_args()
    df_final = run_pipeline(args.entite)

    if not df_final.empty:
        print(df_final.head())
