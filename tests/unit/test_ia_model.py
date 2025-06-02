# tests/unit/test_ia_model.py
class TestIAModelUnit:
    """Tests unitaires modèle IA"""

    def test_model_prediction_format(self):
        """Test : Format retour prédiction"""
        from python_file.footprint_recognition import FootprintRecognition

        model = FootprintRecognition()
        test_image_bytes = b'fake-image-data'

        result = model.predict(test_image_bytes)

        # Vérifier structure réponse
        assert 'animal' in result
        assert 'confidence' in result
        assert 'card_url' in result
        assert 'fun_fact' in result

        # Vérifier types
        assert isinstance(result['animal'], str)
        assert isinstance(result['confidence'], (int, float))
        assert 0 <= result['confidence'] <= 1

    def test_model_class_names_validity(self):
        """Test : Validité noms de classes"""
        from python_file.footprint_recognition import FootprintRecognition

        model = FootprintRecognition()
        class_names = model.class_names

        # Vérifier liste non vide
        assert len(class_names) > 0

        # Vérifier que tous les noms sont des chaînes
        assert all(isinstance(name, str) for name in class_names)

        # Vérifier pas de doublons
        assert len(class_names) == len(set(class_names))
