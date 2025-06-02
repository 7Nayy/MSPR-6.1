#!/bin/bash
echo "☁️  Démarrage du monitoring WildAware avec Grafana Cloud..."

# Vérifier la config Grafana Cloud
if ! grep -q "VOTRE_USER_ID" .env.monitoring; then
    echo "✅ Configuration Grafana Cloud détectée"
else
    echo "⚠️  ATTENTION: Vous devez configurer vos credentials Grafana Cloud dans .env.monitoring"
    echo "   Visitez: https://grafana.com/auth/sign-up/create-user?pg=prod&plcmt=top-nav"
    exit 1
fi

# Charger les variables d'environnement
if [ -f .env.monitoring ]; then
    export $(cat .env.monitoring | xargs)
fi

# Démarrer les services
docker-compose -f docker-compose.monitoring-cloud.yml up -d

echo ""
echo "✅ Services démarrés avec Grafana Cloud !"
echo ""
echo "🌐 Accès :"
echo "  - Votre app: http://localhost:5001"
echo "  - Métriques exporteur: http://localhost:9090/metrics"
echo "  - Grafana Cloud: https://VOTRE_INSTANCE.grafana.net"
echo ""
echo "📊 Dans Grafana Cloud, vos métriques commenceront par 'wildaware_'"
echo ""
echo "🔧 Logs des services :"
echo "  docker-compose -f docker-compose.monitoring-cloud.yml logs -f"
