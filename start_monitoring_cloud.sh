#!/bin/bash
echo "☁️  Démarrage du monitoring WildAware avec Grafana Cloud..."

if [ ! -f .env.monitoring ]; then
    echo "⚠️  Fichier .env.monitoring non trouvé."
    exit 1
fi

set -o allexport
source .env.monitoring
set +o allexport

if [[ -z "$GRAFANA_CLOUD_USER" || -z "$GRAFANA_CLOUD_API_KEY" || "$GRAFANA_CLOUD_USER" == "VOTRE_USER_ID" ]]; then
    echo "⚠️  Vous devez configurer vos credentials Grafana Cloud dans .env.monitoring"
    exit 1
fi

if ! command -v docker &>/dev/null; then
    echo "⚠️  Docker n'est pas installé ou non dans le PATH."
    exit 1
fi

if ! command -v docker-compose &>/dev/null; then
    echo "⚠️  Docker Compose n'est pas installé ou non dans le PATH."
    exit 1
fi

if [ ! -f docker-compose.monitoring-cloud.yml ]; then
    echo "⚠️  docker-compose.monitoring-cloud.yml introuvable."
    exit 1
fi

docker-compose -f docker-compose.monitoring-cloud.yml up -d

echo ""
echo "✅ Services démarrés avec Grafana Cloud !"
echo ""
echo "🌐 Accès :"
echo "  - Votre app: http://localhost:5001"
echo "  - Métriques exporteur: http://localhost:9090/metrics"
echo "  - Grafana Cloud: https://${GRAFANA_INSTANCE}.grafana.net"
echo ""
echo "📊 Dans Grafana Cloud, vos métriques commenceront par 'wildaware_'"
echo ""
echo "🔧 Logs des services :"
echo "  docker-compose -f docker-compose.monitoring-cloud.yml logs -f"
