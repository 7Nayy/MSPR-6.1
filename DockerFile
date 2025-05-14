FROM python:3.10-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port sur lequel l'application fonctionne
EXPOSE 5000

# Définir les variables d'environnement
ENV FLASK_APP=python_file/app.py
ENV PYTHONPATH=/app

# Commande pour démarrer l'application
CMD ["python", "python_file/app.py"]