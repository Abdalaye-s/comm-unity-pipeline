import os
import sys
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Ajouter le chemin racine du projet
model_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "camembert_sentiment_model"))


from src.sentiment_analysis.predict_sentiment import predict_sentiment


#  Charger les données
data_path = r"src\sentiment_analysis\customer_service.csv"  # adapte si ton jeu original est ailleurs
df = pd.read_csv(data_path)

# Nettoyage
df = df.dropna(subset=["Text", "Class"]).drop_duplicates(subset=["Text"])

#  Séparer un jeu de test
_, test_df = train_test_split(df, test_size=0.2, stratify=df["Class"], random_state=42)

#  Prédiction
y_true = test_df["Class"].tolist()
y_pred = [predict_sentiment(text) for text in test_df["Text"]]

# Convertir y_true en labels textuels
label_map = {0: "Négatif", 1: "Positif ou Neutre"}
y_true_text = [label_map[y] for y in y_true]
#  Rapport
print(classification_report(y_true_text, y_pred, target_names=["Négatif", "Positif ou Neutre"]))
