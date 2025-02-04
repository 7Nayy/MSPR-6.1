import os
from supabase import create_client, Client

# Initialisation du client Supabase
supabase_url = "https://qmaywilajvnwvcnacfmu.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtYXl3aWxhanZud3ZjbmFjZm11Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzcxNDQyMCwiZXhwIjoyMDUzMjkwNDIwfQ.p7DuDwc8ZPKI2jFVnA30Otu3bv1Kb3drHmbm-yDl9ao"  # Votre clé service_role
supabase: Client = create_client(supabase_url, supabase_key)

# Chemin local vers vos images
local_images_folder = "cleaned_images"
bucket_name = "dataset-images-wildlens"


def upload_to_supabase(folder_path, bucket):
    try:
        # Vérifier si le bucket existe
        buckets = supabase.storage.list_buckets()
        if not any(b['name'] == bucket for b in buckets):
            print(f"Le bucket {bucket} n'existe pas.")
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
                                print(f"Fichier {file} uploadé avec succès.")
                            except Exception as upload_error:
                                print(f"Erreur lors de l'upload de {file}: {str(upload_error)}")

                    except Exception as file_error:
                        print(f"Erreur lors de la lecture de {file}: {str(file_error)}")
                        continue

    except Exception as e:
        print(f"Erreur générale: {str(e)}")


if __name__ == "__main__":
    upload_to_supabase(local_images_folder, bucket_name)