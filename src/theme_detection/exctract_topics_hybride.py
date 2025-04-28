import nltk
import string
import re
import html
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Téléchargement des ressources nécessaires
nltk.download('punkt')
nltk.download('stopwords')

# Initialisation
lemmatizer = FrenchLefffLemmatizer()
french_stopwords = set(nltk.corpus.stopwords.words('french'))

# Chargement du dictionnaire
file_path = os.path.join(os.path.dirname(__file__), 'dictionnaire.txt')
mots_dictionnaire = set(line.strip() for line in open(file_path, encoding='utf-8'))

# Stopwords personnalisés
custom_stopwords = set([
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "au", "aux", "l",
    "ce", "cet", "cette", "son", "sa", "ses", "nos", "notre", "votre", "vos"
])
stop_topics = custom_stopwords.union(french_stopwords)

def clean_text(text):
    text = html.unescape(text)
    text = text.lower()
    text = re.sub(r"http\S+|@\w+|#\w+|<.*?>", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_topics_hybride(text, top_n=5, remove_generic=True):
    if not text or not isinstance(text, str):
        return []

    cleaned_text = clean_text(text)
    tokens = nltk.word_tokenize(cleaned_text)

    # Suppression des stopwords + lemmatisation
    lemmatized = [
        lemmatizer.lemmatize(token) for token in tokens
        if token not in stop_topics and token.isalpha()
    ]

    # On filtre avec le dictionnaire
    filtered_words = [w for w in lemmatized if w in mots_dictionnaire]

    if not filtered_words:
        return []

    # TF-IDF Scoring
    try:
        vectorizer = TfidfVectorizer(max_features=50)
        X = vectorizer.fit_transform([' '.join(filtered_words)])
        tfidf_scores = dict(zip(vectorizer.get_feature_names_out(), X.toarray()[0]))
        top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        keywords = [kw for kw, _ in top_keywords]

        if remove_generic:
            return [kw for kw in keywords if kw not in stop_topics]
        return keywords
    except Exception as e:
        print("TF-IDF fallback:", e)
        return filtered_words[:top_n]
