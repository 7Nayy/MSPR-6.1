# tests/unit/test_auth.py
import pytest
from unittest.mock import patch, MagicMock
from python_file.app import app


class TestAuthenticationUnit:
    """Tests unitaires d'authentification"""

    @patch('python_file.app.supabase')
    def test_valid_email_validation(self, mock_supabase):
        """Test : Validation format email"""
        with app.test_client() as client:
            # Email valide
            response = client.post('/login', data={
                'username': 'valid@example.com',
                'password': 'password123'
            })
            # Vérifier que l'email est accepté (pas d'erreur de format)
            assert b"Format d'email invalide" not in response.data

    def test_password_length_validation(self):
        """Test : Validation longueur mot de passe"""
        with app.test_client() as client:
            response = client.post('/inscription', data={
                'username': 'test@example.com',
                'password': '123',  # Trop court
                'confirm_password': '123'
            })
            assert b"au moins 8 caractères" in response.data

    def test_password_confirmation_match(self):
        """Test : Correspondance mots de passe"""
        with app.test_client() as client:
            response = client.post('/inscription', data={
                'username': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'different123'
            })
            assert b"ne correspondent pas" in response.data
