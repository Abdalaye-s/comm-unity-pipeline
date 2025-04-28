# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /Community

# Copier les fichiers du projet
COPY . /Community

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    wget \
    git \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenblas-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
# Télécharger les ressources nécessaires pour nltk
RUN python -m nltk.downloader punkt stopwords punkt_tab wordnet

# Exposer le port pour Streamlit
EXPOSE 8501

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "src/dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
