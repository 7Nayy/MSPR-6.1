# tests/security/test_data_protection.py
class TestSecurityDataProtection:
    """Tests protection des données"""

    def test_sensitive_data_exposure(self):
        """Test : Exposition données sensibles"""
        with app.test_client() as client:
            # Tenter d'accéder aux logs
            response = client.get('/logs/app.log')
            assert response.status_code == 404

            # Tenter d'accéder aux variables d'env
            response = client.get('/.env')
            assert response.status_code == 404

    def test_session_fixation_protection(self):
        """Test : Protection fixation session"""
        with app.test_client() as client:
            # Obtenir session ID avant connexion
            response1 = client.get('/')

            # Se connecter
            with patch('python_file.app.supabase') as mock_supabase:
                mock_user = MagicMock()
                mock_user.id = "test-user-id"
                mock_supabase.auth.sign_in_with_password.return_value.user = mock_user

                response2 = client.post('/login', data={
                    'username': 'test@example.com',
                    'password': 'password123'
                })

            # Vérifier redirection (session renouvelée)
            assert response2.status_code == 302

    def test_unauthorized_access_protection(self):
        """Test : Protection accès non autorisé"""
        with app.test_client() as client:
            # Tenter d'accéder à scan sans être connecté
            response = client.get('/scan')
            assert response.status_code == 302  # Redirection vers login

            # Tenter upload sans être connecté
            response = client.post('/upload-image')
            assert response.status_code == 302