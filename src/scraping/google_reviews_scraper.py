import requests
import os
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_place_id(nom_lieu):
    """
    Récupère l'ID du lieu correspondant à un nom donné via l'API Google Places.

    Args:
        nom_lieu (str): Le nom de la ville ou de l'entreprise.

    Returns:
        str or None: L'ID du lieu correspondant ou None si aucun lieu n'est trouvé.
    """
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": nom_lieu,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": GOOGLE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        if result.get("candidates"):
            return result["candidates"][0]["place_id"]
        else:
            print(f"❌ Aucun lieu trouvé pour '{nom_lieu}'.")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du place_id : {e}")
        return None

def get_google_reviews(place_id):
    """
    Récupère les avis Google pour un lieu donné.

    Args:
        place_id (str): L'ID du lieu.

    Returns:
        list[dict]: Une liste de dictionnaires contenant les avis Google.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,reviews",
        "key": GOOGLE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        reviews = data.get("result", {}).get("reviews", [])
        if not reviews:
            print(f"⚠️ Aucun avis trouvé pour ce lieu.")
        results = []
        for review in reviews:
            results.append({
                "source": "Google Reviews",
                "author": review.get("author_name"),
                "rating": review.get("rating"),
                "time": review.get("relative_time_description"),
                "text": review.get("text")
            })
        return results
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des avis : {e}")
        return []

def get_reviews_for_entity(entite):
    """
    Récupère les avis Google pour une entité donnée (ville ou entreprise).

    Args:
        entite (str): Le nom de la ville ou de l'entreprise.

    Returns:
        pd.DataFrame: Un DataFrame contenant les avis Google.
    """
    place_id = get_place_id(entite)
    if not place_id:
        return pd.DataFrame(columns=["source", "author", "rating", "time", "text"])

    reviews = get_google_reviews(place_id)
    if not reviews:
        return pd.DataFrame(columns=["source", "author", "rating", "time", "text"])

    return pd.DataFrame(reviews)
