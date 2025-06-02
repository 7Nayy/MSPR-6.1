#!/bin/bash
echo "🛑 Arrêt du monitoring Grafana Cloud..."
docker-compose -f docker-compose.monitoring-cloud.yml down
echo "✅ Services arrêtés !"
