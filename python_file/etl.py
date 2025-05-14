import cv2
import numpy as np
from supabase import create_client
from typing import Dict, List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Couleurs pour les prints
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FootprintETL:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialise l'ETL avec les credentials Supabase."""
        self.supabase = create_client(supabase_url, supabase_key)

        # Constantes
        self.SOURCE_BUCKET = "Dirty_Footprint"
        self.DESTINATION_BUCKET = "Empreintes"
        self.TARGET_SIZE = (224, 224)

        # Récupération de la structure des dossiers
        self.source_structure = self._get_bucket_structure(self.SOURCE_BUCKET)
        print(f"\nStructure du bucket source: {self.source_structure}\n")

    def _get_bucket_structure(self, bucket_name: str) -> Dict[str, List[str]]:
        """
        Récupère la structure complète d'un bucket.
        """
        try:
            structure = {}
            root_contents = self.supabase.storage.from_(bucket_name).list()
            print(f"{Colors.BLUE}Lecture du bucket {bucket_name}...{Colors.ENDC}")

            for item in root_contents:
                folder_name = None
                if isinstance(item, dict):
                    if 'name' in item and '/' in item['name']:
                        folder_name = item['name'].split('/')[0]
                    elif 'name' in item:
                        folder_name = item['name']

                if folder_name:
                    try:
                        folder_contents = self.supabase.storage.from_(bucket_name).list(folder_name)
                        print(f"{Colors.BLUE}Dossier trouvé: {folder_name}{Colors.ENDC}")

                        structure[folder_name] = []
                        for file_item in folder_contents:
                            if isinstance(file_item, dict) and 'name' in file_item:
                                full_path = f"{folder_name}/{file_item['name']}"
                                structure[folder_name].append(full_path)
                    except Exception as e:
                        print(f"{Colors.WARNING}⚠️  Erreur lecture dossier {folder_name}: {str(e)}{Colors.ENDC}")

            return structure

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur lecture bucket {bucket_name}: {str(e)}{Colors.ENDC}")
            return {}

    def process_single_footprint(self, source_path: str, animal_folder: str) -> bool:
        """Traite une seule image d'empreinte."""
        try:
            print(f"{Colors.BLUE}🔄 Traitement: {source_path}{Colors.ENDC}", end='\r')

            # Lecture de l'image
            try:
                image_bytes = self.supabase.storage.from_(self.SOURCE_BUCKET).download(source_path)
                if not image_bytes:
                    raise Exception("Données d'image vides")
            except Exception as e:
                print(f"{Colors.FAIL}❌ Erreur téléchargement {source_path}: {str(e)}{Colors.ENDC}")
                return False

            # Conversion et traitement
            img_array = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                print(f"{Colors.FAIL}❌ Erreur décodage {source_path}{Colors.ENDC}")
                return False

            # Redimensionnement
            cleaned_img = cv2.resize(img, self.TARGET_SIZE, interpolation=cv2.INTER_AREA)

            # Préparation pour upload
            is_success, buffer = cv2.imencode(".jpg", cleaned_img, [
                cv2.IMWRITE_JPEG_QUALITY, 95,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])

            if not is_success:
                print(f"{Colors.FAIL}❌ Erreur conversion {source_path}{Colors.ENDC}")
                return False

            # Upload
            destination_path = f"{animal_folder}/{os.path.basename(source_path)}"
            try:
                self.supabase.storage.from_(self.DESTINATION_BUCKET).upload(
                    destination_path,
                    buffer.tobytes(),
                    {"content-type": "image/jpeg"}
                )
                print(f"{Colors.GREEN}✅ Succès: {destination_path}{Colors.ENDC}")
                return True
            except Exception as e:
                print(f"{Colors.FAIL}❌ Erreur upload {destination_path}: {str(e)}{Colors.ENDC}")
                return False

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur générale {source_path}: {str(e)}{Colors.ENDC}")
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
            print(f"\n{Colors.HEADER}=== Démarrage de l'ETL ==={Colors.ENDC}")

            if not self.source_structure:
                print(f"{Colors.WARNING}⚠️ Aucun dossier trouvé dans le bucket source{Colors.ENDC}")
                return stats

            # Traitement par dossier
            for folder, files in self.source_structure.items():
                print(f"\n{Colors.BOLD}--- Traitement du dossier {folder} ---{Colors.ENDC}")
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

                # Affichage des stats du dossier
                print(f"\n{Colors.BOLD}Résultats {folder}:{Colors.ENDC}")
                print(f"  Traités: {stats['by_folder'][folder]['processed']}")
                print(f"  Succès: {Colors.GREEN}{stats['by_folder'][folder]['success']}{Colors.ENDC}")
                print(f"  Échecs: {Colors.FAIL}{stats['by_folder'][folder]['failed']}{Colors.ENDC}")

            # Stats finales
            print(f"\n{Colors.HEADER}=== Fin de l'ETL ==={Colors.ENDC}")
            print(f"Total traité: {stats['total_processed']}")
            print(f"Succès: {Colors.GREEN}{stats['total_success']}{Colors.ENDC}")
            print(f"Échecs: {Colors.FAIL}{stats['total_failed']}{Colors.ENDC}")

            return stats

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur critique: {str(e)}{Colors.ENDC}")
            return stats

# Exemple d'utilisation
if __name__ == "__main__":

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    etl = FootprintETL(supabase_url, supabase_key)
    stats = etl.run_etl()