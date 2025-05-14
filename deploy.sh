#!/bin/bash
# Script de déploiement pour WildAware
# Usage: ./deploy.sh [production|staging]

set -e

# Vérifier les arguments
if [ "$1" == "production" ]; then
    ENV="production"
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.production"
    TAG="latest"
elif [ "$1" == "staging" ]; then
    ENV="staging"
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.staging"
    TAG="staging"
else
    echo "Usage: ./deploy.sh [production|staging]"
    exit 1
fi

echo "=============================="
echo "Déploiement en $ENV"
echo "=============================="

# Vérifier que l'environnement est correctement configuré
if [ ! -f "$ENV_FILE" ]; then
    echo "Erreur: Fichier $ENV_FILE introuvable"
    exit 1
fi

# Charger les variables d'environnement
source "$ENV_FILE"

# Vérifier les pré-requis
command -v docker >/dev/null 2>&1 || { echo "docker n'est pas installé"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "docker-compose n'est pas installé"; exit 1; }

# Mettre à jour le code depuis Git
echo "Mise à jour du code..."
git fetch --all
git reset --hard origin/main

# Configuration de l'environnement
export DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry"}
export TAG=$TAG

# Arrêter les conteneurs existants
echo "Arrêt des conteneurs existants..."
docker-compose -f "$COMPOSE_FILE" down || true

# Construire la nouvelle image
echo "Construction de l'image Docker..."
docker-compose -f "$COMPOSE_FILE" build

# Démarrer les nouveaux conteneurs
echo "Démarrage des conteneurs..."
docker-compose -f "$COMPOSE_FILE" up -d

# Vérifier que l'application fonctionne
echo "Vérification du déploiement..."
RETRY=0
MAX_RETRY=5
DELAY=10
until $(curl --output /dev/null --silent --head --fail http://localhost:${PORT:-5000}); do
    if [ ${RETRY} -eq ${MAX_RETRY} ]; then
        echo "L'application n'a pas démarré correctement après ${MAX_RETRY} tentatives"
        docker-compose -f "$COMPOSE_FILE" logs wildaware-app
        exit 1
    fi

    echo "En attente du démarrage de l'application... (${RETRY}/${MAX_RETRY})"
    RETRY=$((RETRY+1))
    sleep ${DELAY}
done

# Nettoyer les images non utilisées
echo "Nettoyage des images anciennes..."
docker image prune -af

echo "=============================="
echo "Déploiement en $ENV réussi !"
echo "=============================="