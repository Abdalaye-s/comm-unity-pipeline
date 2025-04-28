from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# 📊  Initialisation de Vader Sentiment Analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# TextBlob pour l'analyse de sentiment
def predict_textblob(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return 0 if polarity < 0 else 1  # Négatif sinon Positif/Neutre

# Vader pour l'analyse de sentiment
def predict_vader(text):
    scores = vader_analyzer.polarity_scores(text)
    return 0 if scores['compound'] < 0 else 1  # Négatif sinon Positif/Neutre