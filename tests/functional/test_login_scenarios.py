# tests/functional/test_login_scenarios.py
import pytest
from python_file.app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestLoginScenarios:
    """Tests des scénarios de connexion"""

    def test_valid_login_success(self, client):
        """Test : Connexion avec identifiants valides"""
        with patch('python_file.app.supabase') as mock_supabase:
            # Mock réponse Supabase succès
            mock_user = MagicMock()
            mock_user.id = "test-user-id"
            mock_supabase.auth.sign_in_with_password.return_value.user = mock_user

            response = client.post('/login', data={
                'username': 'test@example.com',
                'password': 'validpassword123'
            })

            assert response.status_code == 302  # Redirection
            assert '/scan' in response.location

    def test_invalid_email_format(self, client):
        """Test : Email au format invalide"""
        response = client.post('/login', data={
            'username': 'invalid-email',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert b"Format d'email invalide" in response.data

    def test_empty_credentials(self, client):
        """Test : Champs vides"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })

        assert response.status_code == 200
        assert b"Email et mot de passe requis" in response.data

    def test_wrong_credentials(self, client):
        """Test : Identifiants incorrects"""
        with patch('python_file.app.supabase') as mock_supabase:
            mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

            response = client.post('/login', data={
                'username': 'test@example.com',
                'password': 'wrongpassword'
            })

            assert response.status_code == 200
            assert b"Une erreur est survenue" in response.data