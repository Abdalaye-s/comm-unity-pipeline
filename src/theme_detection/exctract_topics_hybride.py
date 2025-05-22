from spacy.lang.fr.stop_words import STOP_WORDS as SPACY_STOPWORDS
import string
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import streamlit as st
<<<<<<< HEAD
@st.cache_resource 
def load_model():
    nlp = spacy.load("fr_core_news_sm")
    return nlp
=======
>>>>>>> e3d35cf75165ba3ef083b97acf6d03814f69f8c8

@st.cache_resource 
def load_model():
    nlp = spacy.load("fr_core_news_sm")
    return nlp
# === 2. Charger les modèles spaCy ===
try:
    nlp = load_model()
except OSError:
    # Si le modèle n'est pas trouvé, le télécharger
    spacy.cli.download("fr_core_news_sm")
    nlp = spacy.load("fr_core_news_sm")
# Stopwords personnalisés à retirer en plus
CUSTOM_STOPWORDS = set([
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "au", "aux", "l",
    "ce", "cet", "cette", "son", "sa", "ses", "nos", "notre", "votre", "vos"
])

# Stopwords "thématiques" à exclure du résultat final (optionnel)
stop_topics = set(CUSTOM_STOPWORDS.union(SPACY_STOPWORDS))

def extract_topics_hybride(text, top_n=5, remove_generic=True):
    """
    Extraction hybride des sujets à partir d'un texte.
    - Nettoyage avancé
    - Extraction par noun chunks
    - Fallback sur NOUN+ADJ
    - Scoring par TF-IDF
    """
    if not text or not isinstance(text, str):
        return []

    # Nettoyage basique
    text_cleaned = re.sub(r"http\S+|@\w+|#\w+|[^\w\s]", " ", text.lower())
    doc = nlp(text_cleaned)

    # 1️⃣ Extraction des chunks nominaux
    phrases = []
    for chunk in doc.noun_chunks:
        phrase = chunk.lemma_.lower().strip(string.punctuation + " ")
        if (phrase and
            len(phrase.split()) <= 4 and
            len(phrase) > 2 and
            phrase not in stop_topics and
            not any(w in stop_topics for w in phrase.split())):
            phrases.append(phrase)

    # 2️⃣ Fallback si trop peu d'infos
    if len(phrases) < 2:
        phrases = [
            token.lemma_.lower().strip() for token in doc
            if token.pos_ in {"NOUN", "ADJ"}
            and len(token.text) > 2
            and token.lemma_.lower() not in stop_topics
        ]

    # 3️⃣ TF-IDF scoring
    if not phrases:
        return []

    try:
        vectorizer = TfidfVectorizer(max_features=50)
        X = vectorizer.fit_transform([' '.join(phrases)])
        tfidf_scores = dict(zip(vectorizer.get_feature_names_out(), X.toarray()[0]))
        top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        keywords = [kw for kw, _ in top_keywords]

        if remove_generic:
            return [kw for kw in keywords if kw not in stop_topics]
        return keywords
    except:
        # fallback simplifié
        return [w for w in phrases if w not in stop_topics][:top_n]

