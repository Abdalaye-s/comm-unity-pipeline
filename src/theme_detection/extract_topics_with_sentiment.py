import sys
import os

# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.sentiment_analysis.predict_sentiment import vote_maj
from src.theme_detection.exctract_topics_hybride import extract_topics_hybride

def extract_topics_with_sentiment(text, top_n=5):
    """
    Retourne une liste de tuples (sujet, sentiment) à partir d’un texte brut.
    """
    if not text or not isinstance(text, str):
        return []

    # Nettoyage + extraction des sujets
    topics = extract_topics_hybride(text, top_n=top_n)

    # Prédiction du sentiment (0 ou 1)
    sentiment_id = vote_maj(text)
    sentiment = "Positif ou Neutre" if sentiment_id == 1 else "Négatif"

    return [(t, sentiment) for t in topics]