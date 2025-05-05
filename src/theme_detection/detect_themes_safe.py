from transformers import pipeline
import os
import sys
# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.utils.data_cleaning import clean_text

# Charger le modèle de classification
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

# Thèmes ville
themes_ville = [
    "Jeunesse, éducation, vie scolaire",
    "Logement et aménagement urbain",
    "Retraités/Séniors",
    "Solidarité, social",
    "Sport, loisirs et vie associative",
    "Transition écologique, environnement",
    "Citoyenneté",
    "Commerce, économie sociale et solidaire",
    "Culture, relations internationales",
    "Droits des femmes",
    "Éducation et socio-éducatif"
]

# Thèmes entreprise
themes_entreprise = [
    "Qualité du service",
    "Service client / support",
    "Rapport qualité-prix",
    "Fiabilité / professionnalisme",
    "Délais / ponctualité",
    "Accueil / relation client",
    "Produits / prestations",
    "Expérience utilisateur",
    "Hygiène / propreté",
    "Accessibilité / localisation",
    "Transparence / communication",
    "Engagement environnemental",
    "Éthique / responsabilité sociale",
    "Innovation / technologie",
    "Réclamations / litiges"
]

# Mots-clés indicatifs d'une entreprise
entreprise_keywords = ["SARL", "SAS", "SASU", "Entreprise", "Inc", "LLC", "Corp", "Société", "Groupe"]

def detect_theme_safe(text, entite=None, threshold=0.35):
    cleaned = clean_text(text)
    if not cleaned:
        return "Autres / Non catégorisé"

    # Choix des thèmes selon l'entité
    if entite and any(keyword.lower() in entite.lower() for keyword in entreprise_keywords):
        themes = themes_entreprise
    else:
        themes = themes_ville

    result = classifier(cleaned, candidate_labels=themes)
    top_score = result['scores'][0]
    top_label = result['labels'][0]

    if top_score >= threshold:
        return top_label
    else:
        return f"Ambigu entre : {result['labels'][0]} et {result['labels'][1]}"

