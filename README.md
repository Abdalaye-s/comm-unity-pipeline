# Comm'Unity - Projet de veille e-réputation pour collectivités

---

## 📚 Description du projet
Comm'Unity est un outil d'analyse de l'e-réputation basé sur le scraping d'avis publics et l'analyse de sentiments via NLP.  
L'objectif est d'accompagner les collectivités dans le suivi des politiques publiques et la détection des signaux faibles.

---

## 🚀 Fonctionnalités principales
- Scraping Google Reviews et twitter par thématique (Mairie, Logement, Écoles, Sport...).
- Analyse de sentiment (positif, négatif, neutre) via modèle CamemBERT.
- Extraction automatique d'entités nommées (lieux, élus...).
- Détection de signaux faibles et alertes internes.
- Dashboard Streamlit interactif et personnalisable.

---

## 🛠️ Stack technique
- **Python** (3.10+)
- **Streamlit** pour l'interface utilisateur
- **Transformers (HuggingFace)** pour NLP
- **Docker** pour la containerisation
- **Git/GitHub** pour la collaboration
- **PostgreSQL** (prévu) pour la base de données scalable

---
## 🗂️ Sources de données prévues

- Google Reviews (API Places)
- Facebook public (scraping éthique)
- TikTok public (scraping éthique)
- X (ancien Twitter) - Limité à 100 lectures gratuites/mois via API v2
- Forums/blogs locaux (futur)
- Médias en ligne locaux (futur via RSS ou API presse)

## 🔧 Installation rapide

```bash
# Clonez le dépôt
git clone https://github.com/TON_ORGANISATION/comm-unity-pipeline.git

# Allez dans le dossier
cd comm-unity-pipeline

# Créez un environnement virtuel
python -m venv venv
source venv/bin/activate   # ou .\venv\Scripts\activate sur Windows

# Installez les dépendances
pip install -r requirements.txt

# Lancez Streamlit
streamlit run src/dashboard/dashboard.py
