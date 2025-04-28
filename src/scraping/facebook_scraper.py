from dotenv import load_dotenv
import os

load_dotenv()
# Charger les variables d'environnement
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

def get_facebook_posts(page_id, access_token, limit=100):
    import requests

    url = f"https://graph.facebook.com/v12.0/{page_id}/posts"
    params = {
        'access_token': access_token,
        'limit': limit
    }

    posts = []
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            posts.extend(data.get('data', []))
            # Récupérer l'URL pour la page suivante, si disponible
            url = data.get('paging', {}).get('next', None)
            params = {}  # Après la première requête, plus besoin des paramètres initiaux
        else:
            raise Exception(f"Error fetching posts: {response.status_code} - {response.text}")
    
    return posts
