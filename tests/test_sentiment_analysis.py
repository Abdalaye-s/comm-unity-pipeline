import sys
import os

# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from src.sentiment_analysis.predict_sentiment import predict_sentiment
# Exemple de texte à prédire
text = "La ville de Gennevilliers pourrait être plus propre et il y a des soucis de sécurité dans certaines zones."

# Prédiction du sentiment
sentiment = predict_sentiment(text)

# Affichage du résultat
print("Prédiction de sentiment :", sentiment)