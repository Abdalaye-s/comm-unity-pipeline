# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /Community

# Copier tous les fichiers du projet dans le conteneur
COPY . /Community

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenblas-dev \
    libpng-dev \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip et outils de compilation
RUN pip install --upgrade pip setuptools wheel

# Installer les dépendances Python
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Télécharger les données nécessaires à nltk
RUN python -m nltk.downloader punkt stopwords wordnet

# Télécharger le modèle français de spaCy
RUN python -m spacy download fr_core_news_md
RUN python -m spacy download fr_core_news_sm

# Exposer le port de Streamlit
EXPOSE 8501

# Commande de démarrage du dashboard
CMD ["streamlit", "run", "src/dashboard/0_Accueil.py", "--server.port=8501", "--server.address=0.0.0.0"]
