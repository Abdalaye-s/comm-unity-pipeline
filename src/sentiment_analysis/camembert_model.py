import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Charger les variables d'environnement
model_path = os.path.normpath(os.path.abspath(os.path.join("src", "camembert_sentiment_model")))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Utilisation de l'appareil : {device}")
print("Utilisation du modèle :", model_path)

class CamembertSentimentAnalyzer:
    def __init__(self):
        print(f"Chargement du modèle depuis : {model_path}")
        if not os.path.exists(os.path.join(model_path, "pytorch_model.bin")):
            raise FileNotFoundError(f"Le fichier 'pytorch_model.bin' est introuvable dans {model_path}")
        if not os.path.exists(os.path.join(model_path, "config.json")):
            raise FileNotFoundError(f"Le fichier 'config.json' est introuvable dans {model_path}")
        if not os.path.exists(os.path.join(model_path, "tokenizer.json")) and not os.path.exists(os.path.join(model_path, "vocab.json")):
            raise FileNotFoundError(f"Les fichiers 'tokenizer.json' ou 'vocab.json' sont introuvables dans {model_path}")
        # Charger le tokenizer et le modèle depuis le chemin local
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        self.model.eval()
        self.model.to(device)

    def predict_camembert(self, text):
        # Préparer les entrées pour le modèle
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128).to(device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            pred_class = torch.argmax(probs).item()
        return pred_class  # 0 = Négatif, 1 = Positif/Neutre

# --- Fonction globale accessible directement ---
_analyzer = CamembertSentimentAnalyzer()

def predict_camembert(text):
    return _analyzer.predict_camembert(text)


