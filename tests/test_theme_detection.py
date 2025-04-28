from src.theme_detection.detect_themes_safe import detect_theme_safe
from src.theme_detection.exctract_topics_with_sentiment import extract_topics_with_sentiment

text = "Les transports à Gennevilliers sont souvent en retard et peu fiables."

theme_safe=detect_theme_safe(text)
topics = extract_topics_with_sentiment(text)

print("Sentiment :", sentiment)
print("Sujets extraits :", topics)