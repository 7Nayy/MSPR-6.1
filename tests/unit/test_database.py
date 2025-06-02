# tests/unit/test_database.py
class TestDatabaseUnit:
    """Tests unitaires base de données"""

    @patch('python_file.supabase_conn.create_client')
    def test_supabase_connection(self, mock_create_client):
        """Test : Connexion Supabase"""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        from python_file.supabase_conn import init_supabase
        client = init_supabase()

        assert client is not None
        mock_create_client.assert_called_once()

    def test_animal_info_retrieval(self):
        """Test : Récupération info animal"""
        from python_file.footprint_recognition import FootprintRecognition

        model = FootprintRecognition()

        with patch('python_file.footprint_recognition.supabase') as mock_supabase:
            # Mock réponse DB
            mock_supabase.table().select().eq().execute.return_value.data = [
                {
                    'Espèce': 'Renard',
                    'Card': 'http://card-url.jpg',
                    'Fun fact': 'Fait amusant sur le renard'
                }
            ]

            result = model._get_animal_info('Renard')

            assert result['Espèce'] == 'Renard'
            assert 'Card' in result
            assert 'Fun fact' in result