import os
from supabase import create_client, Client

# Initialisation Supabase
supabase_url = "https://lekndkijyvsrtzpssejb.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxla25ka2lqeXZzcnR6cHNzZWpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzk3MTUzNiwiZXhwIjoyMDUzNTQ3NTM2fQ.pjeE5lfQ_NXPWakV7UMvU2RWsHKnqZBtFKx4t32Z0lA"
supabase: Client = create_client(supabase_url, supabase_key)

# Configuration
local_images_folder = "cleaned_images"
bucket_name = "Empreintes"

def test_connection():
    try:
        # Test direct avec le bucket spécifique
        supabase.storage.from_(bucket_name).list()
        print("Connexion réussie et accès au bucket confirmé")
        return True
    except Exception as e:
        print(f"Erreur de connexion: {str(e)}")
        return False

def upload_to_supabase(folder_path, bucket):
    try:
        if not os.path.exists(folder_path):
            print(f"Le dossier {folder_path} n'existe pas")
            return

        # Vérifie si on peut accéder au bucket
        try:
            supabase.storage.from_(bucket).list()
        except Exception as e:
            print(f"Erreur d'accès au bucket {bucket}: {str(e)}")
            return

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        local_file_path = os.path.join(root, file)
                        file_key = os.path.relpath(local_file_path, folder_path).replace(" ", "_")

                        with open(local_file_path, "rb") as file_data:
                            try:
                                res = supabase.storage.from_(bucket).upload(file_key, file_data)
                                print(f"Fichier {file} uploadé avec succès")
                            except Exception as upload_error:
                                print(f"Erreur lors de l'upload de {file}: {str(upload_error)}")

                    except Exception as file_error:
                        print(f"Erreur lors de la lecture de {file}: {str(file_error)}")
                        continue

    except Exception as e:
        print(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    if test_connection():
        upload_to_supabase(local_images_folder, bucket_name)