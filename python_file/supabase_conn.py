import os
from supabase import create_client, Client
from dotenv import load_dotenv


def init_supabase() -> Client:
    # Chargement des variables d'environnement
    load_dotenv(dotenv_path='.env')

    # Récupération des credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    # Vérification des credentials
    if not supabase_url or not supabase_key:
        raise ValueError("Credentials Supabase manquants dans le fichier .env")

    # Création et retour du client
    return create_client(supabase_url, supabase_key)


# Initialisation du client Supabase
supabase = init_supabase()