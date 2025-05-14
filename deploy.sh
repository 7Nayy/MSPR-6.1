#!/bin/bash
# deploy-local.sh

# Vérifier l'argument pour l'environnement
if [ "$1" == "prod" ]; then
    ENV="production"
    BRANCH="prod"
    COMPOSE_FILE="docker-compose.yml"
elif [ "$1" == "dev" ]; then
    ENV="development"
    BRANCH="pre-prod"
    COMPOSE_FILE="docker-compose.dev.yml"
else
    echo "Usage: ./deploy-local.sh [prod|dev]"
    exit 1
fi

echo "Déploiement de l'environnement $ENV localement..."

# Récupérer les dernières modifications
git fetch
git checkout $BRANCH
git pull

# Construire et démarrer les conteneurs
docker-compose -f $COMPOSE_FILE down
docker-compose -f $COMPOSE_FILE up -d --build

# Afficher le statut
echo "Déploiement terminé. Conteneurs en cours d'exécution:"
docker-compose -f $COMPOSE_FILE ps