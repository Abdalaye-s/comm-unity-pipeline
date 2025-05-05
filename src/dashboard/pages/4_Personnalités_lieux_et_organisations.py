import streamlit as st
import pandas as pd
import ast
import os
import sys

# 📁 Chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "../../")))

from src.utils.dashboard_utils import safe_parse_entities

def split_entities(df):
    if "entities" not in df.columns:
        return df

    personnes, lieux, organisations = [], [], []

    for row in df["entities"]:
        row = row if isinstance(row, list) else []
        persons, locations, orgs = [], [], []
        for ent in row:
            if not isinstance(ent, (list, tuple)) or len(ent) != 2:
                continue
            label = ent[1].upper()
            if label == "PER":
                persons.append(ent[0])
            elif label == "LOC":
                locations.append(ent[0])
            elif label == "ORG":
                orgs.append(ent[0])
        personnes.append(persons)
        lieux.append(locations)
        organisations.append(orgs)

    df["personnes"] = personnes
    df["lieux"] = lieux
    df["organisations"] = organisations
    return df

st.set_page_config(page_title="Entités nommées", layout="wide")
st.title("🧠 Personnalités, lieux et organisations mentionnés")

# ✅ Vérifier que les données existent dans la session
if "df" not in st.session_state:
    st.warning("⚠️ Aucune donnée trouvée. Veuillez lancer une recherche depuis la page d’accueil.")
    st.stop()

# ✅ Utiliser les données filtrées de la session
df = st.session_state["df"].copy()

# Parser et splitter les entités
df["entities"] = df["entities"].apply(safe_parse_entities)
df = split_entities(df)

# ✅ Affichage
st.write("Colonnes disponibles dans le fichier :", df.columns.tolist())

cols = ["text", "personnes", "lieux", "organisations"]
available_cols = [col for col in cols if col in df.columns]

if available_cols:
    st.markdown("### Entités extraites des commentaires :")
    st.dataframe(df[available_cols].dropna(how="all").reset_index(drop=True), height=600)
else:
    st.warning("Aucune colonne d'entités nommées détectée dans le fichier.")
