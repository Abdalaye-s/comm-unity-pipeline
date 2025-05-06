import requests
import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except KeyError:
        import os
        return os.getenv(key, default)

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")

def parse_relative_date(text):
    if not text:
        return None
    text = text.lower()
    now = datetime.now()

    try:
        if "day" in text:
            days = int(text.split()[0])
            return now - timedelta(days=days)
        elif "week" in text:
            weeks = int(text.split()[0])
            return now - timedelta(weeks=weeks)
        elif "month" in text:
            months = int(text.split()[0])
            return now - timedelta(days=months * 30)
        elif "year" in text:
            years = int(text.split()[0])
            return now - timedelta(days=years * 365)
    except:
        return None

    return None

def get_place_id(nom_lieu):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": nom_lieu,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": GOOGLE_API_KEY,
        "language": "fr"
    }
    response = requests.get(url, params=params)
    result = response.json()
    try:
        return result["candidates"][0]["place_id"]
    except IndexError:
        print(f"❌ Aucun lieu trouvé pour '{nom_lieu}'.")
        return None

def get_google_reviews(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,reviews",
        "key": GOOGLE_API_KEY,
        "language": "fr" 
    }
    response = requests.get(url, params=params)
    data = response.json()

    reviews = data.get("result", {}).get("reviews", [])
    results = []
    for review in reviews:
        results.append({
            "source": "Google Reviews",
            "author": review.get("author_name"),
            "rating": review.get("rating"),
            "text": review.get("text"),
            # ✅ Utilisation du timestamp UNIX direct
            "time": datetime.fromtimestamp(review.get("time"))
        })
    return results

def get_reviews_for_entity(entite):
    place_id = get_place_id(entite)
    if not place_id:
        return pd.DataFrame(columns=["source", "author", "rating", "text", "time"])
    
    reviews = get_google_reviews(place_id)
    return pd.DataFrame(reviews)
