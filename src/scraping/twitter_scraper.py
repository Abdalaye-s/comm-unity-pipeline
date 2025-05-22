import tweepy
import pandas as pd
import time
import os
import streamlit as st

def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except KeyError:
        import os
        return os.getenv(key, default)

# Charger les variables d'environnement
BEARER_TOKEN = get_secret("TWITTER_BEARER_TOKEN")

def get_tweets(entite):
    
    """
    Récupère les tweets récents correspondant à une entité donnée.

    Args:
        entite (str): Le mot-clé ou l'entité à rechercher (ville ou entreprise).

    Returns:
        pd.DataFrame: Un DataFrame contenant les tweets récupérés.
    """

    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    query = f"{entite} -is:retweet lang:fr"
    try:
        tweets = client.search_recent_tweets(
            query=query,
            tweet_fields=["created_at", "text"],
            max_results=12
        )
        if tweets.data:
            data = [{"source": "Twitter", "date": t.created_at, "text": t.text} for t in tweets.data]
            return pd.DataFrame(data)
        else:
            print(f"⚠️ Aucun tweet trouvé pour l'entité '{entite}'.")
            return pd.DataFrame(columns=["source", "date", "text"])

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        return pd.DataFrame(columns=["source", "date", "text"]) 