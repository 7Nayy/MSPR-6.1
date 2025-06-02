"""Tests de base pour vérifier que tout fonctionne"""

def test_home_page(client):
    """Test: Page d'accueil accessible"""
    response = client.get('/')
    assert response.status_code == 200

def test_scan_page_requires_login(client):
    """Test: Page scan nécessite une connexion"""
    response = client.get('/scan')
    assert response.status_code == 302  # Redirection vers login
    assert '/login' in response.location

def test_scan_page_with_login(logged_user):
    """Test: Page scan accessible quand connecté"""
    response = logged_user.get('/scan')
    assert response.status_code == 200
    assert b'test@example.com' in response.data

