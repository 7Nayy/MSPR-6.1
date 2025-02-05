import os
from supabase import create_client, Client

# Initialisation Supabase
supabase_url = "https://lekndkijyvsrtzpssejb.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxla25ka2lqeXZzcnR6cHNzZWpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzk3MTUzNiwiZXhwIjoyMDUzNTQ3NTM2fQ.pjeE5lfQ_NXPWakV7UMvU2RWsHKnqZBtFKx4t32Z0lA"
supabase: Client = create_client(supabase_url, supabase_key)

# Configuration
local_images_folder = "WildLens_img"
bucket_name = "Dirty_Footprint"


def test_connection():
    try:
        supabase.storage.from_(bucket_name).list()
        print("Connexion réussie et accès au bucket confirmé")
        return True
    except Exception as e:
        print(f"Erreur de connexion: {str(e)}")
        return False


def get_public_url(file_path):
    """Génère l'URL publique pour un fichier dans le bucket"""
    return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"


def get_animal_id(espece):
    """Récupère l'ID de l'animal depuis la base de données"""
    try:
        response = supabase.table('Animaux').select('id').eq('Espèce', espece).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'ID pour {espece}: {str(e)}")
        return None


def update_database_urls():
    try:
        for animal_folder in os.listdir(local_images_folder):
            animal_path = os.path.join(local_images_folder, animal_folder)

            if os.path.isdir(animal_path):
                # Récupérer l'ID de l'animal
                animal_id = get_animal_id(animal_folder)

                if animal_id is not None:
                    # Pour chaque image dans le dossier
                    for file in os.listdir(animal_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            file_path = f"{animal_folder}/{file}".replace(" ", "_")
                            public_url = get_public_url(file_path)

                            try:
                                # Ajouter l'URL dans la table Empreintes
                                result = supabase.table('Empreintes').insert({
                                    "animal_id": animal_id,
                                    "image_url": public_url
                                }).execute()
                                print(f"URL ajoutée pour {file_path}")

                            except Exception as e:
                                print(f"Erreur lors de l'ajout de l'URL pour {file_path}: {str(e)}")
                else:
                    print(f"Animal non trouvé dans la base de données: {animal_folder}")

    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base de données: {str(e)}")


def upload_to_supabase(folder_path, bucket):
    try:
        if not os.path.exists(folder_path):
            print(f"Le dossier {folder_path} n'existe pas")
            return

        for animal_folder in os.listdir(folder_path):
            animal_path = os.path.join(folder_path, animal_folder)

            if os.path.isdir(animal_path):
                print(f"Traitement du dossier: {animal_folder}")

                for file in os.listdir(animal_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            local_file_path = os.path.join(animal_path, file)
                            file_key = f"{animal_folder}/{file}".replace(" ", "_")

                            with open(local_file_path, "rb") as file_data:
                                try:
                                    res = supabase.storage.from_(bucket).upload(file_key, file_data)
                                    print(f"Fichier {file_key} uploadé avec succès")
                                except Exception as upload_error:
                                    print(f"Erreur lors de l'upload de {file_key}: {str(upload_error)}")

                        except Exception as file_error:
                            print(f"Erreur lors de la lecture de {file}: {str(file_error)}")
                            continue

    except Exception as e:
        print(f"Erreur générale: {str(e)}")


if __name__ == "__main__":
    if test_connection():
        #upload_to_supabase(local_images_folder, bucket_name)
        update_database_urls()