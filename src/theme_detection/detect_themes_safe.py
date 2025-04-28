from transformers import pipeline
import os
import sys
# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.utils.data_cleaning import clean_text

# Charger un modèle pré-entraîné pour la classification de texte
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

# Liste des thématiques
themes = [
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

def detect_theme_safe(text, entite=None, threshold=0.35):
    cleaned = clean_text(text)
    if not cleaned:
        return "Autres / Non catégorisé"

    result = classifier(cleaned, candidate_labels=themes)
    top_score = result['scores'][0]
    top_label = result['labels'][0]

    if top_score >= threshold:
        return top_label
    else:
        # Retourne les 2 meilleurs choix en cas d'ambiguïté
        return f"Ambigu entre : {result['labels'][0]} et {result['labels'][1]}"
