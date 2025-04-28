from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# Données d'entraînement factices
X = ["j'adore ce produit", "c'est nul", "excellent", "je déteste", "mauvais", "génial"]
y = [1, 0, 1, 0, 0, 1]  # 1 = positif, 0 = négatif

# Entraînement
vectorizer = TfidfVectorizer()
X_vect = vectorizer.fit_transform(X)
model = MultinomialNB()
model.fit(X_vect, y)

# Sauvegarde
joblib.dump(model, "naive_bayes_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

# ⚙️ Charger Naive Bayes et le vectorizer
naive_bayes = joblib.load("naive_bayes_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Naive Bayes pour l'analyse de sentiment
def predict_naive_bayes(text):
    X_vect = vectorizer.transform([text])
    return naive_bayes.predict(X_vect)[0]  # Prédiction Naive Bayes (0 ou 1)