# src/utils/data_loader.py

import pandas as pd
import os, sys

# Assure que le chemin vers src.main est connu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.main import run_pipeline

def load_data(city_name):
    """
    Charge les données pour une ville donnée via le pipeline principal.
    Nettoie les doublons et extrait le nom d'entreprise si disponible.
    """
    df = run_pipeline(city_name)

    # Supprimer doublons
    if "text_clean" in df.columns:
        df = df.drop_duplicates(subset=["text_clean"])

    # Extraire nom d'entreprise (ou valeur par défaut)
    if "entreprise" in df.columns:
        df["entreprise"] = df["entreprise"].astype(str)
        df["nom_entreprise"] = df["entreprise"].str.replace(r"^Entreprise\s+", "", regex=True)
    else:
        df["nom_entreprise"] = "Inconnue"

    return df
