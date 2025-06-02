"""Tests d'authentification"""
import io
from unittest.mock import patch, MagicMock


def test_login_success(client):
    """Test: Connexion réussie avec identifiants valides"""
    with patch('python_file.app.supabase') as mock_supabase:
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_supabase.auth.sign_in_with_password.return_value.user = mock_user

        response = client.post('/login', data={
            'username': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 302  # Redirection
        assert '/scan' in response.location


def test_login_invalid_email(client):
    """Test: Connexion avec email invalide"""
    response = client.post('/login', data={
        'username': 'email-invalide',
        'password': 'password123'
    })

    assert response.status_code == 200
    assert b"Format d&#39;email invalide" in response.data


def test_login_empty_fields(client):
    """Test: Connexion avec champs vides"""
    response = client.post('/login', data={
        'username': '',
        'password': ''
    })

    assert response.status_code == 200
    assert b"Email et mot de passe requis" in response.data


def test_registration_success(client):
    """Test: Inscription réussie"""
    with patch('python_file.app.supabase') as mock_supabase:
        mock_user = MagicMock()
        mock_user.id = "new-user-id"
        mock_supabase.auth.sign_up.return_value.user = mock_user

        response = client.post('/inscription', data={
            'username': 'nouveau@example.com',
            'password': 'motdepasse123',
            'confirm_password': 'motdepasse123'
        })

        assert response.status_code == 302  # Redirection vers scan


def test_registration_password_mismatch(client):
    """Test: Inscription avec mots de passe différents"""
    response = client.post('/inscription', data={
        'username': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'different123'
    })

    assert response.status_code == 200
    assert b"ne correspondent pas" in response.data