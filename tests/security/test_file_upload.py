# tests/security/test_file_upload.py
class TestSecurityFileUpload:
    """Tests de sécurité upload fichiers"""

    def test_malicious_file_upload(self):
        """Test : Upload fichier malveillant"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user'
                sess['email'] = 'test@example.com'

            # Fichier exécutable déguisé
            malicious_file = b'#!/bin/bash\nrm -rf /'

            response = client.post('/upload-image',
                                   data={'image': (io.BytesIO(malicious_file), 'malicious.jpg')},
                                   content_type='multipart/form-data'
                                   )

            data = response.get_json()
            # L'upload doit échouer ou être sécurisé
            assert data['success'] is False or 'error' in data

    def test_file_size_limit_enforcement(self):
        """Test : Respect limite taille fichier"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user'
                sess['email'] = 'test@example.com'

            # Fichier > 16MB (limite app)
            large_file = b'0' * (17 * 1024 * 1024)

            response = client.post('/upload-image',
                                   data={'image': (io.BytesIO(large_file), 'large.jpg')},
                                   content_type='multipart/form-data'
                                   )

            # Doit être rejeté
            assert response.status_code == 413

    def test_file_type_validation(self):
        """Test : Validation type de fichier"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user'
                sess['email'] = 'test@example.com'

            # Fichier non-image
            text_file = b'This is not an image'

            response = client.post('/upload-image',
                                   data={'image': (io.BytesIO(text_file), 'document.txt')},
                                   content_type='multipart/form-data'
                                   )

            data = response.get_json()
            assert data['success'] is False
