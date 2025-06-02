import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# 🔧 Configuration AVANT tout import
os.environ['TESTING'] = 'True'
os.environ['FLASK_ENV'] = 'testing'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key-for-testing'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# 🛡️ Mock GLOBAL de Supabase avant TOUS les imports
def mock_create_client(*args, **kwargs):
    mock_client = MagicMock()
    mock_client.auth.sign_in_with_password.return_value.user = MagicMock(id="test-user")
    mock_client.auth.sign_up.return_value.user = MagicMock(id="test-user")
    mock_client.auth.sign_out.return_value = None
    mock_client.storage.from_().upload.return_value = MagicMock()
    mock_client.storage.from_().get_public_url.return_value = "http://test-url.jpg"
    mock_client.table().select().eq().execute.return_value.data = []
    return mock_client


# Patcher AVANT l'import de l'app
with patch('supabase.create_client', side_effect=mock_create_client):
    from python_file.app import app


@pytest.fixture
def client():
    """Client de test Flask"""
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def logged_user(client):
    """Utilisateur connecté"""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test-user-id'
        sess['email'] = 'test@example.com'
    return client


@pytest.fixture
def mock_ia_model():
    """Mock modèle IA"""
    with patch('python_file.app.footprint_model') as mock:
        mock.predict.return_value = {
            'animal': 'Renard',
            'confidence': 0.85,
            'card_url': 'http://test-card.jpg',
            'fun_fact': 'Le renard est très malin !'
        }
        yield mock


@pytest.fixture
def test_image():
    """Image de test (JPEG 1x1 pixel)"""
    return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
