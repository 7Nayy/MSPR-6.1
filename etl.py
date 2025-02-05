import cv2
import numpy as np
from supabase import create_client
import logging
from typing import Optional, Dict, List
from datetime import datetime
import json
import os


class FootprintETL:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialise l'ETL avec les credentials Supabase."""
        self.supabase = create_client(supabase_url, supabase_key)
        self.logger = ETLLogger()

        # Constantes
        self.SOURCE_BUCKET = "Dirty_Footprint"
        self.DESTINATION_BUCKET = "Empreintes"
        self.TARGET_SIZE = (224, 224)

        # Récupération de la structure des dossiers
        self.source_structure = self._get_bucket_structure(self.SOURCE_BUCKET)
        self.logger.log_step(f"Structure du bucket source: {self.source_structure}")

    def _get_bucket_structure(self, bucket_name: str) -> Dict[str, List[str]]:
        """
        Récupère la structure complète d'un bucket.
        Retourne un dictionnaire avec les dossiers comme clés et les fichiers comme valeurs.
        """
        try:
            # D'abord, listons le contenu à la racine
            structure = {}
            root_contents = self.supabase.storage.from_(bucket_name).list()
            self.logger.log_step(f"Contenu racine du bucket {bucket_name}: {root_contents}")

            # Pour chaque élément qui pourrait être un dossier
            for item in root_contents:
                folder_name = None
                if isinstance(item, dict):
                    if 'name' in item and '/' in item['name']:
                        folder_name = item['name'].split('/')[0]
                    elif 'name' in item:
                        folder_name = item['name']

                if folder_name:
                    # Lister le contenu du dossier
                    try:
                        folder_contents = self.supabase.storage.from_(bucket_name).list(folder_name)
                        self.logger.log_step(f"Contenu du dossier {folder_name}: {folder_contents}")

                        # Stocker les fichiers du dossier
                        structure[folder_name] = []
                        for file_item in folder_contents:
                            if isinstance(file_item, dict) and 'name' in file_item:
                                full_path = f"{folder_name}/{file_item['name']}"
                                structure[folder_name].append(full_path)
                    except Exception as e:
                        self.logger.log_step(f"⚠️ Erreur lors de la lecture du dossier {folder_name}: {str(e)}")

            return structure

        except Exception as e:
            self.logger.log_step(f"❌ Erreur lors de la lecture du bucket {bucket_name}: {str(e)}")
            return {}

    def process_single_footprint(self, source_path: str, animal_folder: str) -> bool:
        """Traite une seule image d'empreinte."""
        try:
            self.logger.log_step(f"Traitement de l'image: {source_path}")

            # Lecture de l'image source
            try:
                image_bytes = self.supabase.storage.from_(self.SOURCE_BUCKET).download(source_path)
                if not image_bytes:
                    raise Exception("Données d'image vides")
            except Exception as e:
                self.logger.log_step(f"❌ Erreur de téléchargement: {str(e)}")
                return False

            # Conversion en image
            try:
                img_array = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is None:
                    raise Exception("Échec du décodage de l'image")
            except Exception as e:
                self.logger.log_step(f"❌ Erreur de décodage: {str(e)}")
                return False

            # Nettoyage et redimensionnement
            cleaned_img = cv2.resize(img, self.TARGET_SIZE, interpolation=cv2.INTER_AREA)

            # Conversion pour upload
            is_success, buffer = cv2.imencode(".jpg", cleaned_img, [
                cv2.IMWRITE_JPEG_QUALITY, 95,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])

            if not is_success:
                raise Exception("Échec de la conversion de l'image")

            # Construction du chemin de destination
            destination_path = f"{animal_folder}/{os.path.basename(source_path)}"

            # Upload
            try:
                self.supabase.storage.from_(self.DESTINATION_BUCKET).upload(
                    destination_path,
                    buffer.tobytes(),
                    {"content-type": "image/jpeg"}
                )
                self.logger.log_step(f"✅ Image traitée avec succès: {destination_path}")
                return True
            except Exception as e:
                self.logger.log_step(f"❌ Erreur d'upload: {str(e)}")
                return False

        except Exception as e:
            self.logger.log_step(f"❌ Erreur générale: {str(e)}")
            return False

    def run_etl(self) -> Dict:
        """Execute l'ETL complet."""
        stats = {
            "date_execution": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_processed": 0,
            "total_success": 0,
            "total_failed": 0,
            "by_folder": {}
        }

        try:
            self.logger.log_step("=== Démarrage de l'ETL ===")

            if not self.source_structure:
                self.logger.log_step("⚠️ Aucun dossier trouvé dans le bucket source")
                return stats

            # Traitement par dossier
            for folder, files in self.source_structure.items():
                self.logger.log_step(f"\n--- Traitement du dossier {folder} ---")
                stats["by_folder"][folder] = {"processed": 0, "success": 0, "failed": 0}

                for file_path in files:
                    stats["total_processed"] += 1
                    stats["by_folder"][folder]["processed"] += 1

                    if self.process_single_footprint(file_path, folder):
                        stats["total_success"] += 1
                        stats["by_folder"][folder]["success"] += 1
                    else:
                        stats["total_failed"] += 1
                        stats["by_folder"][folder]["failed"] += 1

            self.logger.log_step("\n=== Fin de l'ETL ===")
            self.logger.log_step(f"Total traité: {stats['total_processed']}")
            self.logger.log_step(f"Succès: {stats['total_success']}")
            self.logger.log_step(f"Échecs: {stats['total_failed']}")

            return stats

        except Exception as e:
            self.logger.log_step(f"❌ Erreur critique de l'ETL: {str(e)}")
            return stats


class ETLLogger:
    def __init__(self, log_directory: str = "etl_logs"):
        """Initialise le système de logging."""
        self.start_time = datetime.now()

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        self.process_log = f"{log_directory}/process_{timestamp}.log"

        with open(self.process_log, 'w', encoding='utf-8') as f:
            f.write(f"=== Journal ETL Empreintes - Démarré le {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")

    def log_step(self, message: str):
        """Enregistre une étape importante."""
        with open(self.process_log, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")


# Exemple d'utilisation
if __name__ == "__main__":
    SUPABASE_URL = "https://lekndkijyvsrtzpssejb.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxla25ka2lqeXZzcnR6cHNzZWpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzk3MTUzNiwiZXhwIjoyMDUzNTQ3NTM2fQ.pjeE5lfQ_NXPWakV7UMvU2RWsHKnqZBtFKx4t32Z0lA"

    etl = FootprintETL(SUPABASE_URL, SUPABASE_KEY)
    stats = etl.run_etl()