import streamlit as st
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Charger le CSS
with open(Path(__file__).parent / "assets" / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre et logo
col1, col2 = st.columns([1, 10])
with col1:
    st.image(Path(__file__).parent / "logo.png", width=80)
with col2:
    st.title("Comm'Unity - Analyse des avis citoyens")

st.markdown("Bienvenue dans l'outil d'analyse des retours citoyens. Veuillez sélectionner une ville pour lancer une analyse complète.")

# Saisie utilisateur
entite = st.text_input("Nom de la ville ou entité à analyser :", placeholder="Ex: Gennevilliers")

if st.button("🚀 Lancer l'analyse"):
    if entite.strip() == "":
        st.warning("Merci d'entrer un nom de ville valide.")
    else:
        with st.spinner("Exécution du pipeline..."):
            # Appel du pipeline via subprocess
            result = subprocess.run(
                ["python", "../../src/main.py", "--entite", entite],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success("✅ Analyse terminée !")
                st.markdown("Le fichier `comments_annotated.csv` est prêt.")
            else:
                st.error("❌ Erreur durant l'exécution du pipeline.")
                st.code(result.stderr)

# Lecture du fichier généré s'il existe
csv_path = Path(__file__).parent.parent.parent / "comments_annotated.csv"
if csv_path.exists():
    st.markdown("### 📄 Aperçu des données analysées")
    import pandas as pd
    df = pd.read_csv(csv_path)
    st.dataframe(df.head(20))
