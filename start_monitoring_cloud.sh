#!/bin/bash

echo "🚀 DÉMARRAGE MONITORING WILDAWARE (Basé sur config dev)"
echo "===================================================="

# Vérifier Docker
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré. Veuillez le démarrer et réessayer."
    exit 1
fi
echo "✅ Docker est actif"

# Arrêter d'abord les autres docker-compose pour éviter les conflits
echo "🧹 Arrêt des autres services Docker..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.monitoring-cloud.yml down --remove-orphans 2>/dev/null || true

# Libérer les ports
echo "🔓 Libération des ports..."
for port in 5001 9090 9100 12345; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "   Libération du port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# Créer le répertoire logs s'il n'existe pas
mkdir -p logs

echo "🚀 Démarrage du monitoring avec la config qui fonctionne..."
docker-compose -f docker-compose.monitoring-dev.yml up -d

echo "⏳ Attente du démarrage des services (20 secondes)..."
sleep 20

# Vérifier l'état des services
echo ""
echo "🩺 État des services:"
docker-compose -f docker-compose.monitoring-dev.yml ps

echo ""
echo "📊 Test des endpoints:"
endpoints=(
    "localhost:5001|Application WildAware"
    "localhost:9090/metrics|Exporteur WildAware"
    "localhost:9100/metrics|Node Exporter"
    "localhost:12345/-/healthy|Grafana Agent"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS='|' read -r endpoint name <<< "$endpoint_info"
    if curl -s --max-time 5 "http://$endpoint" >/dev/null 2>&1; then
        echo "✅ $name ($endpoint) - OK"
    else
        echo "⚠️  $name ($endpoint) - En cours de démarrage..."
    fi
done

echo ""
echo "🌐 URLs d'accès:"
echo "  - Application WildAware: http://localhost:5001"
echo "  - Métriques application: http://localhost:9090/metrics"
echo "  - Métriques système: http://localhost:9100/metrics"
echo "  - Grafana Agent: http://localhost:12345/-/healthy"
echo "  - Grafana Cloud: https://bd7nayy.grafana.net"

echo ""
echo "🔧 Commandes utiles:"
echo "  - Voir les logs: docker-compose -f docker-compose.monitoring-dev.yml logs -f"
echo "  - Logs Grafana Agent: docker-compose -f docker-compose.monitoring-dev.yml logs -f grafana-agent"
echo "  - Logs Application: docker-compose -f docker-compose.monitoring-dev.yml logs -f wildaware-app"
echo "  - Arrêter: docker-compose -f docker-compose.monitoring-dev.yml down"

echo ""
echo "✅ MONITORING DÉMARRÉ !"
echo "📊 Votre application fonctionne sur le port 5001 (comme en dev)"
echo "📈 Les métriques sont collectées et envoyées vers Grafana Cloud"