import sys
import os
from datetime import datetime, timedelta


# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pandas as pd
import time
from src.scraping.google_reviews_scraper import get_reviews_for_entity

def is_entreprise(entite):
    entreprise_keywords = ["SARL", "SAS", "SASU", "Entreprise", "Inc", "LLC", "Corp", "Société", "Groupe"]
    return any(keyword.lower() in entite.lower() for keyword in entreprise_keywords)

def extract_nom_entreprise(entite):
    if entite.lower().startswith("entreprise "):
        return entite[11:].strip()
    return entite.strip()


def generate_google_review_queries(entite):
    """
    Génère automatiquement les requêtes Google Reviews selon si l'entité est une entreprise ou une ville.
    """
    if is_entreprise(entite):
        nom_entreprise = extract_nom_entreprise(entite)
        templates = [
            "{} avis clients",
            "{} expérience utilisateur",
            "{} retour client",
            "{} service client",
            "{} qualité de service",
            "Avis sur {}",
            "Expérience avec {}",
        ]
        return [template.format(nom_entreprise) for template in templates]
    else:
        templates = [
            "Ville de {}",
            "Restaurants {}",
            "Hôtels {}",
            "Commodités {}",
            "Mairie de {}",
            "Écoles {}",
            "Logement social {}",
            "Parcs et jardins {}",
            "Associations sportives {}",
            "Commerce local {}",
            "Culture et médiathèques {}",
            "Maisons de retraite {}",
            "Solidarité sociale {}",
            "Développement durable {}",
            "Entreprises {}"
        ]
        return [template.format(entite.strip()) for template in templates]


def scrape_city_by_themes(entite, pause_sec=2): 
    queries = generate_google_review_queries(entite)
    all_reviews = []
    is_ent = is_entreprise(entite)
    nom_nettoye = extract_nom_entreprise(entite)

    for query in queries:
        print(f"🔎 Scraping Google Reviews pour : {query}")
        df_reviews = get_reviews_for_entity(query)

        if not df_reviews.empty:
            df_reviews["theme_query"] = query
            df_reviews["entite"] = entite
            df_reviews["nom_entreprise"] = nom_nettoye if is_ent else ""
            all_reviews.append(df_reviews)
        else:   
            print(f"⚠️ Aucun avis trouvé pour : {query}")

        time.sleep(pause_sec)

    if all_reviews:
        result_df = pd.concat(all_reviews, ignore_index=True)
        print(f"✅ Scraping terminé : {len(result_df)} avis collectés.")
        # À la fin de scrape_city_by_themes, juste avant return result_df
        six_months_ago = datetime.now() - timedelta(days=180)
        result_df = result_df[result_df["time"] >= six_months_ago]
        # Ajoute type_entite et ville explicites
        result_df["type_entite"] = "entreprise" if is_ent else "ville"
        result_df["ville"] = "" if is_ent else entite

        return result_df
    else:
        print("❌ Aucun avis collecté.")
        return pd.DataFrame(columns=["source", "author", "rating", "time", "text", "theme_query", "entite", "nom_entreprise"])
