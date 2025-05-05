#dashboard_utils.py
import ast
from collections import Counter
from fpdf import FPDF
from transformers import pipeline, AutoTokenizer
import pandas as pd
import os
import urllib.request

import os


def safe_parse_entities(val):
    try:
        parsed = ast.literal_eval(val) if isinstance(val, str) else val
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return []


def safe_parse_topics_with_sentiment(x):
    if isinstance(x, str):
        try:
            val = ast.literal_eval(x)
            if isinstance(val, list):
                # Garder uniquement les tuples de longueur 3
                return [t for t in val if isinstance(t, tuple) and len(t) == 3]
            return []
        except Exception:
            return []
    elif isinstance(x, list):
        return [t for t in x if isinstance(t, tuple) and len(t) == 3]
    return []


# 🎯 Conversion score → couleur
def sentiment_to_color(score):
    if score >= 0.3:
        return "🟢"
    elif score >= 0:
        return "🟡"
    return "🔴"
def split_entities(df):
    df = df.copy()
    df["personnes"] = df["entities"].apply(lambda ents: [e[0] for e in ents if e[1] == "PER"] if isinstance(ents, list) else [])
    df["lieux"] = df["entities"].apply(lambda ents: [e[0] for e in ents if e[1] == "LOC"] if isinstance(ents, list) else [])
    df["organisations"] = df["entities"].apply(lambda ents: [e[0] for e in ents if e[1] == "ORG"] if isinstance(ents, list) else [])
    return df

def chunk_text(text, tokenizer, max_tokens=1024):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        tokens = tokenizer.tokenize(word)
        if current_length + len(tokens) > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(tokens)
        else:
            current_chunk.append(word)
            current_length += len(tokens)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def summarize_text(df):
    # Concaténation du texte nettoyé
    text_clean = df["text_clean"].dropna().tolist()
    if not text_clean:
        return "Aucun texte disponible pour générer un résumé."

    full_text = " ".join(text_clean)
    if not full_text or len(full_text.split()) < 50:
        return "Pas assez de contenu pertinent pour générer un résumé."

    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Séparer en blocs de tokens
    chunks = chunk_text(full_text, tokenizer, max_tokens=1024)
    if not chunks:
        return "[Erreur] Aucun bloc généré — vérifie que le texte est bien encodable."

    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            if not chunk.strip() or len(chunk.split()) < 30:
                summaries.append(f"[Bloc {i} trop court — ignoré]")
                continue
            result = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
            summaries.append(result[0]["summary_text"])
        except Exception as e:
            summaries.append(f"[Erreur pour le bloc {i} : {str(e)}]")

    final_summary = "\n\n".join(summaries)
    return final_summary


# 🧹 Affichage lisible
def stringify_for_display(x):
    if isinstance(x, list):
        return str(x)
    elif pd.isna(x):
        return ""
    return str(x)

def sentiment_to_text(score):
    if score is None:
        return ""
    if score > 0.2:
        return "positif"
    elif score < -0.2:
        return "négatif"
    else:
        return "neutre"

def create_pdf(df, topics_counter=None, topics_sentiment_df=None, summary=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 🔍 Nettoyer les caractères non supportés
    def clean_text(text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    # Titre
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, clean_text("Rapport d'Analyse des Commentaires"), ln=True, align="C")
    pdf.ln(10)

    # Résumé
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, clean_text("Résumé général"), ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, clean_text(summary))
    pdf.ln(8)

    # Statistiques globales
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, clean_text("Chiffres clés"), ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, clean_text(f"- Nombre de commentaires : {len(df)}"), ln=True)
    if "main_theme" in df.columns:
        unique_themes = df["main_theme"].dropna().nunique()
        pdf.cell(200, 8, clean_text(f"- Nombre de thématiques identifiées : {unique_themes}"), ln=True)
    if topics_counter:
        pdf.cell(200, 8, clean_text(f"- Nombre de sujets détectés : {len(topics_counter)}"), ln=True)
    pdf.ln(8)

    # Sujets fréquents
    if topics_counter:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, clean_text("Sujets les plus fréquents"), ln=True)
        pdf.set_font("Arial", size=11)
        for topic, count in topics_counter.most_common(10):
            pdf.cell(200, 8, clean_text(f"- {topic} : {count} occurrences"), ln=True)
        pdf.ln(8)

    # Sentiment par sujet
    if topics_sentiment_df is not None:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, clean_text("Analyse des sujets avec sentiment"), ln=True)
        pdf.set_font("Arial", size=11)
        for _, row in topics_sentiment_df.iterrows():
            score = row.get("sentiment_score", None)
            sentiment = row.get("sentiment", "Inconnu")
            topic = row.get("topic", "Inconnu")
            pdf.cell(200, 8, clean_text(f"- {topic} : {sentiment} (score : {score})"), ln=True)
        pdf.ln(8)

    # Entités nommées
    if "entities" in df.columns and df["entities"].notna().any():
        all_ents = sum(df["entities"], [])
        ent_counter = Counter([ent[0] for ent in all_ents])
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, clean_text("Entités nommées"), ln=True)
        pdf.set_font("Arial", size=11)
        for ent, count in ent_counter.most_common(10):
            pdf.cell(200, 8, clean_text(f"- {ent} : {count} fois"), ln=True)

    pdf_path = "rapport_analyse_commentaires.pdf"
    pdf.output(pdf_path)
    return pdf_path