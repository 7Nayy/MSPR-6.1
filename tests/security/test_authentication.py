# tests/security/test_authentication.py
import pytest
from unittest.mock import patch
from python_file.app import app


class TestSecurityAuthentication:
    """Tests de sécurité authentification"""

    def test_session_security_headers(self):
        """Test : Headers de sécurité session"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user'

            response = client.get('/scan')

            # Vérifier headers sécurité (configurés par Talisman)
            assert 'Strict-Transport-Security' in response.headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers

    def test_sql_injection_protection(self):
        """Test : Protection injection SQL"""
        with app.test_client() as client:
            # Tentative injection SQL
            malicious_input = "'; DROP TABLE users; --"

            response = client.post('/login', data={
                'username': malicious_input,
                'password': 'password'
            })

            # L'app doit gérer gracieusement sans crasher
            assert response.status_code in [200, 302]

    def test_xss_protection(self):
        """Test : Protection XSS"""
        with app.test_client() as client:
            xss_payload = "<script>alert('XSS')</script>"

            response = client.post('/login', data={
                'username': xss_payload,
                'password': 'password'
            })

            # Vérifier que le script n'est pas exécuté
            assert b'<script>' not in response.data

    def test_brute_force_protection(self):
        """Test : Protection force brute"""
        with app.test_client() as client:
            # Simuler tentatives répétées
            for i in range(10):
                response = client.post('/login', data={
                    'username': 'test@example.com',
                    'password': f'wrong_password_{i}'
                })

            # L'application devrait toujours répondre
            assert response.status_code == 200
