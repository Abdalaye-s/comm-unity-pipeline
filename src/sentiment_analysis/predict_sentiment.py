import sys
import os

# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Afficher les chemins pour déboguer
print(sys.path)

from src.sentiment_analysis.camembert_model import predict_camembert
from src.sentiment_analysis.vader_texblob import predict_textblob, predict_vader
from src.sentiment_analysis.naive_bayes_model import predict_naive_bayes
from src.utils.data_cleaning import clean_text, French_Preprocess_listofSentence
from collections import Counter

# 🗳 Fonction de vote majoritaire
def vote_maj(text, use_weights=True):
    predictions = [
        predict_camembert(text),
        predict_textblob(text),
        predict_vader(text),
        predict_naive_bayes(text)
    ]

    if use_weights:
        weights = [1, 1, 1, 1]  # Poids : CamemBERT peut avoir plus de poids
        votes = {}
        for i, pred in enumerate(predictions):
            votes[pred] = votes.get(pred, 0) + weights[i]
        return max(votes, key=votes.get)
    else:
        return Counter(predictions).most_common(1)[0][0]

# 🧠 Prédiction finale
def predict_sentiment(text):
    text = clean_text(text)
    text = French_Preprocess_listofSentence([text])[0]  # 🔧 Ajout du [0] pour récupérer le texte nettoyé
    sentiment = vote_maj(text)
    label = "Positif ou Neutre" if sentiment == 1 else "Négatif"
    return label
