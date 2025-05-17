#dashboard_utils.py
import ast
from collections import Counter
from fpdf import FPDF
from transformers import pipeline, AutoTokenizer
import pandas as pd
import os
import urllib.request
import seaborn as sns
from wordcloud import WordCloud
from matplotlib import pyplot as plt

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


#  Conversion score → couleur
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

class RapportMairiePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, " Rapport Synthétique ", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_section(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(230, 230, 250)
        self.cell(0, 10, f" {title}", ln=True, fill=True)
        self.ln(2)

    def add_text(self, text, size=11):
        self.set_font("Arial", size=size)
        text = text.encode('latin-1', 'replace').decode('latin-1')  # éviter les erreurs Unicode
        self.multi_cell(0, 8, text)
        self.ln()

    def add_image(self, path, w=180):
        if os.path.exists(path):
            self.image(path, w=w)
            self.ln(10)

def create_pdf(df, topics_counter=None, topics_sentiment_df=None, filename="rapport_analyse_commentaires.pdf"):
    pdf = RapportMairiePDF()
    pdf.add_page()

    # Section 1 : Contexte
    pdf.add_section("Contexte général")
    pdf.add_text("Ce rapport présente une synthèse des ressentis exprimés par les citoyens à travers des avis en ligne.")
    pdf.add_text(f"Nombre total de commentaires analysés : {len(df)}")

    if "main_theme" in df.columns:
        n_themes = df["main_theme"].nunique()
        pdf.add_text(f"Nombre de thématiques identifiées : {n_themes}")

    # Section 2 : Sentiment global
    pdf.add_section("Sentiment global")
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x="sentiment", palette="Set2")
    plt.title("Distribution des sentiments")
    plt.tight_layout()
    plt.savefig("sentiment_global.png")
    plt.close()
    pdf.add_image("sentiment_global.png")

    # Section 3 : Sujets fréquents
    if topics_counter:
        pdf.add_section("Sujets les plus discutés")
        for topic, count in topics_counter.most_common(10):
            pdf.add_text(f" {topic} ({count} mentions)")

    # Section 4 : Sujets associés à un sentiment
    if topics_sentiment_df is not None and not topics_sentiment_df.empty:
        pdf.add_section("Sujets associés aux sentiments négatifs ou positifs")
        for _, row in topics_sentiment_df.iterrows():
            topic = row.get("topic", "Inconnu")
            sentiment = row.get("sentiment", "Inconnu")
            score = row.get("sentiment_score", "-")
            pdf.add_text(f" {topic} : {sentiment} (score : {score})")

    # Section 5 : Nuage de mots
    if "topics" in df.columns and df["topics"].notna().any():
        all_words = ' '.join(sum(df["topics"], []))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_words)
        wordcloud.to_file("nuage_mots.png")
        pdf.add_section("Nuage de mots (thématiques les plus visibles)")
        pdf.add_image("nuage_mots.png")

    # Section 6 : Entités citées
    if "entities" in df.columns and df["entities"].notna().any():
        all_entities = sum(df["entities"], [])
        ent_counter = Counter([ent[0] for ent in all_entities])
        pdf.add_section("Lieux, personnalités ou organisations citées")
        for ent, count in ent_counter.most_common(10):
            pdf.add_text(f" {ent} ({count} fois)")

    # Enregistrement
    pdf.output(filename)
    print(f"✅ Rapport PDF généré : {filename}")
    pdf.output(filename)
    return filename 