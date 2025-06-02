# tests/functional/test_scan_scenarios.py
class TestScanScenarios:
    """Tests des scénarios de scan"""

    def test_successful_image_upload_analysis(self, client):
        """Test : Upload et analyse d'image réussis"""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['email'] = 'test@example.com'

        with patch('python_file.app.supabase') as mock_supabase, \
                patch('python_file.app.footprint_model') as mock_model:
            # Mock upload Supabase
            mock_supabase.storage.from_().upload.return_value = MagicMock()
            mock_supabase.storage.from_().get_public_url.return_value = "http://test-url.jpg"

            # Mock analyse IA
            mock_model.predict.return_value = {
                'animal': 'Renard',
                'confidence': 0.85,
                'card_url': 'http://card-url.jpg',
                'fun_fact': 'Fait amusant'
            }

            # Image test (1x1 pixel JPEG)
            test_image = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'

            response = client.post('/upload-image',
                                   data={'image': (io.BytesIO(test_image), 'test.jpg')},
                                   content_type='multipart/form-data'
                                   )

            data = response.get_json()
            assert data['success'] is True
            assert 'redirect' in data

    def test_image_upload_without_login(self, client):
        """Test : Upload sans être connecté"""
        response = client.post('/upload-image',
                               data={'image': (io.BytesIO(b'fake-image'), 'test.jpg')},
                               content_type='multipart/form-data'
                               )

        assert response.status_code == 302  # Redirection vers login

    def test_upload_invalid_file_format(self, client):
        """Test : Upload fichier format invalide"""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['email'] = 'test@example.com'

        response = client.post('/upload-image',
                               data={'image': (io.BytesIO(b'not-an-image'), 'test.txt')},
                               content_type='multipart/form-data'
                               )

        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data