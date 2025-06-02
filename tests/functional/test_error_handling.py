# tests/functional/test_error_handling.py
class TestErrorHandling:
    """Tests de gestion d'erreurs"""

    def test_404_page(self, client):
        """Test : Page 404"""
        response = client.get('/page-inexistante')
        assert response.status_code == 404

    def test_500_error_handling(self, client):
        """Test : Gestion erreur 500"""
        with patch('python_file.app.supabase') as mock_supabase:
            mock_supabase.auth.sign_in_with_password.side_effect = Exception("Database error")

            response = client.post('/login', data={
                'username': 'test@example.com',
                'password': 'password'
            })

            assert response.status_code == 200  # Erreur gérée gracieusement

    def test_large_file_upload(self, client):
        """Test : Upload fichier trop volumineux"""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['email'] = 'test@example.com'

        # Créer un fichier > 16MB (limite définie dans app.py)
        large_file = b'0' * (17 * 1024 * 1024)

        response = client.post('/upload-image',
                               data={'image': (io.BytesIO(large_file), 'large.jpg')},
                               content_type='multipart/form-data'
                               )

        assert response.status_code == 413  # Request Entity Too Large