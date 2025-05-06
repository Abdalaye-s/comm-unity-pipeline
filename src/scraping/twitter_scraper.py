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
BEARER_TOKEN = get_secret("BEARER_TOKEN")

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

    except tweepy.TooManyRequests:
        print("⏳ Trop de requêtes. Pause de 15 minutes...")
        time.sleep(15 * 60)  # Pause de 15 minutes
        return get_tweets(entite)

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        return pd.DataFrame(columns=["source", "date", "text"]) 
'''# src/scraping/twitter_scraper.py

import snscrape.modules.twitter as sntwitter
import pandas as pd

def get_tweets(query, max_tweets=500):
    """
    Scrape des tweets publics correspondant à une requête donnée sans passer par l'API officielle Twitter.

    Args:
        query (str): Le mot-clé ou l'expression à chercher.
        max_tweets (int): Nombre maximum de tweets à récupérer.

    Returns:
        pd.DataFrame: Un DataFrame contenant les tweets.
    """
    tweets = []
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            tweets.append({
                'source': 'Twitter',
                'author': tweet.user.username,
                'rating': None,  # Pas de notation sur Twitter
                'time': tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
                'text': tweet.content
            })
            if i + 1 >= max_tweets:
                break
    except Exception as e:
        print(f"⚠️ Erreur lors du scraping Twitter : {e}")
        return pd.DataFrame()

    return pd.DataFrame(tweets)
'''