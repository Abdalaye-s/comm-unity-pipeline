# src/theme_detection/ner_entity_extraction.py
import spacy
import streamlit as st
@st.cache_resource 
def load_model():
    nlp = spacy.load("fr_core_news_md")
    return nlp
nlp = load_model()

def extract_named_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ["PER", "LOC", "GPE", "ORG"]]
