# ===== ÉTAPE 5: Modification de python_file/supabase_conn.py =====
import os
from supabase import create_client, Client
from dotenv import load_dotenv


def init_supabase() -> Client:
    """Initialise le client Supabase avec gestion des tests"""
    # En mode test, retourner un mock
    if os.getenv('TESTING') == 'True':
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        print("🧪 Mode test: utilisation d'un mock Supabase")
        return mock_client

    # Mode normal
    load_dotenv(dotenv_path='.env')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("Credentials Supabase manquants dans le fichier .env")

    return create_client(supabase_url, supabase_key)


# Initialisation
supabase = init_supabase()