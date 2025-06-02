#!/usr/bin/env python3
import time
import re
import os
import requests
from prometheus_client import start_http_server, Counter, Gauge
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WildAwareExporter:
    def __init__(self):
        self.app_url = os.getenv('APP_URL', 'http://wildaware-app:5000')
        self.log_path = os.getenv('LOG_PATH', '/app/logs/app.log')
        self.log_position = 0

        # Métriques simples
        self.app_up = Gauge('wildaware_app_up', 'Application status')
        self.uploads_total = Counter('wildaware_uploads_total', 'Total uploads')
        self.uploads_success = Counter('wildaware_uploads_success_total', 'Successful uploads')
        self.ia_analyses = Counter('wildaware_ia_analyses_total', 'IA analyses')
        self.user_connections = Counter('wildaware_user_connections_total', 'User connections')
        self.errors_total = Counter('wildaware_errors_total', 'Total errors')

    def check_app_health(self):
        try:
            response = requests.get(f"{self.app_url}/", timeout=5)
            self.app_up.set(1 if response.status_code == 200 else 0)
            return response.status_code == 200
        except:
            self.app_up.set(0)
            return False

    def process_logs(self):
        if not os.path.exists(self.log_path):
            return

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                f.seek(self.log_position)
                lines = f.readlines()
                self.log_position = f.tell()

                for line in lines:
                    line = line.strip()
                    if 'Connexion réussie' in line:
                        self.user_connections.inc()
                    elif 'Début de l\'upload' in line:
                        self.uploads_total.inc()
                    elif 'Animal identifié:' in line:
                        self.ia_analyses.inc()
                        self.uploads_success.inc()
                    elif 'ERROR:' in line:
                        self.errors_total.inc()

        except Exception as e:
            logger.error(f"Erreur lecture logs: {e}")

    def run(self):
        logger.info("Démarrage exporteur WildAware")
        while True:
            try:
                self.check_app_health()
                self.process_logs()
                time.sleep(30)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Erreur: {e}")
                time.sleep(60)

if __name__ == '__main__':
    start_http_server(9090)
    exporter = WildAwareExporter()
    exporter.run()
