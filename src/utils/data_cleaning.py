import nltk
import string
import re
import html
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

file_path = os.path.join(os.path.dirname(__file__), 'dictionnaire.txt')

# Initialisation des stopwords et du lemmatizer
french_stopwords = nltk.corpus.stopwords.words('french')
mots = set(line.strip() for line in open(file_path, encoding='utf-8'))
lemmatizer = FrenchLefffLemmatizer()
# Charger un dictionnaire personnalisé
#mots = set(line.strip() for line in open('dictionnaire.txt'))
file_path = os.path.join(os.path.dirname(__file__), 'dictionnaire.txt')
mots = set(line.strip() for line in open(file_path, encoding='utf-8'))
# 📌 Fonction de nettoyage de texte
def clean_text(text):
    text = html.unescape(text)
    text = text.replace("&#39;", "'")
    text = text.lower()
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"[\.,!?]", "", text)
    text = re.sub(r"\b\w{15,}\b", "", text)
    text = re.sub(r"\b\w*\d+\w*\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# 📌 Fonction de prétraitement pour le français
def French_Preprocess_listofSentence(listofSentence):
    preprocess_list = []
    for sentence in listofSentence:
        sentence_w_punct = "".join([i.lower() for i in sentence if i not in string.punctuation])
        sentence_w_num = ''.join(i for i in sentence_w_punct if not i.isdigit())
        tokenize_sentence = nltk.tokenize.word_tokenize(sentence_w_num)
        words_w_stopwords = [i for i in tokenize_sentence if i not in french_stopwords]
        words_lemmatize = (lemmatizer.lemmatize(w) for w in words_w_stopwords)
        sentence_clean = ' '.join(w for w in words_lemmatize if w.lower() in mots or not w.isalpha())
        preprocess_list.append(sentence_clean)
    return preprocess_list