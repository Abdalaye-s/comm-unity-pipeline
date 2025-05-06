# Comm'Unity 

**Comm'Unity** est une plateforme interactive d’analyse de sentiment et d’extraction de thématiques à partir de commentaires en ligne, liée à des **villes**, **entreprises** ou **institutions**. Elle combine le scraping, le traitement du langage naturel et la visualisation des données dans un outil clé-en-main.

---

## 🚀 Fonctionnalités

* 🔍 **Scraping** de commentaires depuis des sources en ligne
* 💬 **Analyse de sentiment** (NLTK, spaCy, ou modèle CamemBERT personnalisé)
* 🧠 **Extraction de thématiques et d’entités nommées**
* 📊 **Dashboard interactif** avec **Streamlit**
* 📄 **Génération automatique de rapports PDF**
* 🕾️ **Comparaison entre plusieurs villes ou structures**

---

## 📺 Démo en ligne

Tu peux tester directement l'application ici :
🔗 [comm-unity-pipeline Streamlit App](https://comm-unity-pipeline-ep627svcndyxtk9h97gpsz.streamlit.app/)

---

## 📦 Lancer avec Docker

1. **Récupérer l’image Docker** :

   ```bash
   docker pull abdalaye/image_comm_unity_test:latest
   ```

2. **Lancer l'application en local** :

   ```bash
   docker run -p 8501:8501 abdalaye/image_comm_unity_test:latest
   ```

3. **Ouvrir l’application** :
   👉 [http://localhost:8501](http://localhost:8501)

---

## ⚙️ Installation en local

> Requiert **Python 3.10**

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/Abdalaye-s/comm-unity-pipeline.git
   cd comm-unity-pipeline
   ```

2. **Créer un environnement virtuel :**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/macOS
   ```

3. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer le dashboard Streamlit :**

   ```bash
   streamlit run src/dashboard/0_Accueil.py
   ```

---

## 📆 Structure du projet (extrait)

```
comm-unity-pipeline/
├── src/
│   ├── scraping/
│   ├── sentiment_analysis/
│   ├── camembert_sentiment_model/
│   ├── dashboard/
│   │   └── 0_Accueil.py
│   └── report_generation/
├── requirements.txt
├── .gitattributes
└── Dockerfile
```

---

## 📦 Modèle CamemBERT & Git LFS

Le modèle lourd utilisé (`pytorch_model.bin`) est suivi via **Git LFS**.

Avant de cloner ou de tirer, installez Git LFS :

```bash
git lfs install
git pull
```

---

## 🛠️ Débogage (si rien ne s’affiche)

* Vérifie la console où tu as lancé `streamlit run src/dashboard/0_Accueil.py`
* Erreurs typiques : mauvaise URL, données absentes, ou fichier manquant
* Assure-toi que les fichiers `.csv` ou `.json` attendus sont bien présents dans le dossier `data/` ou autre

---

## 👨‍💼 Auteurs

* **Abdalaye SOUMARE**
* **Lakhdar DIFF**
* **Sénabou Ben SALIMA**
* **Manel ALLOUNE**

---

## 📄 Licence

Ce projet est distribué sous licence MIT.
