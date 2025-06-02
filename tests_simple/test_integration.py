# MANQUAIT AU DÉBUT DU FICHIER:
import io
import pytest
from unittest.mock import patch, MagicMock

def test_complete_user_journey(client, test_image):
    """
    Test d'intégration : Parcours utilisateur complet
    Inscription → Connexion → Upload Image → Analyse → Résultats → Déconnexion
    """

    # 🔥 ÉTAPE 1: Inscription
    with patch('python_file.app.supabase') as mock_supabase:
        mock_user = MagicMock()
        mock_user.id = "integration-test-user"
        mock_supabase.auth.sign_up.return_value.user = mock_user

        response = client.post('/inscription', data={
            'username': 'integration@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        assert response.status_code == 302
        assert '/scan' in response.location
        print("✅ Étape 1: Inscription réussie")

    # 🔥 ÉTAPE 2: Accès à la page scan
    response = client.get('/scan')
    assert response.status_code == 200
    assert b'integration@test.com' in response.data
    print("✅ Étape 2: Accès page scan réussi")

    # 🔥 ÉTAPE 3: Upload d'une image (CORRECTION ICI)
    with patch('python_file.app.supabase') as mock_supabase, \
            patch('python_file.app.footprint_model') as mock_ia:
        # 🔧 CORRECTION: Mock Supabase storage correctement
        mock_upload_response = MagicMock()
        mock_upload_response.error = None  # Pas d'erreur
        mock_supabase.storage.from_().upload.return_value = mock_upload_response
        mock_supabase.storage.from_().get_public_url.return_value = "http://integration-test.jpg"

        # Mock IA analysis
        mock_ia.predict.return_value = {
            'animal': 'Lynx',
            'confidence': 0.92,
            'card_url': 'http://lynx-card.jpg',
            'fun_fact': 'Le lynx est un excellent chasseur nocturne'
        }

        response = client.post('/upload-image',
                               data={'image': (io.BytesIO(test_image), 'integration.jpg')},
                               content_type='multipart/form-data')

        data = response.get_json()
        assert data['success'] is True
        assert 'redirect' in data
        assert '/scan_result' in data['redirect']
        print("✅ Étape 3: Upload et analyse réussis")

    # 🔥 ÉTAPE 4: Vérification des résultats
    response = client.get('/scan_result')
    assert response.status_code == 200
    assert b'Lynx' in response.data
    print("✅ Étape 4: Affichage résultats réussi")

    # 🔥 ÉTAPE 5: Déconnexion
    with patch('python_file.app.supabase') as mock_supabase:
        response = client.get('/logout')
        assert response.status_code == 302
        assert '/' in response.location
        print("✅ Étape 5: Déconnexion réussie")

    # 🔥 ÉTAPE 6: Vérification protection
    response = client.get('/scan')
    assert response.status_code == 302
    assert '/login' in response.location
    print("✅ Étape 6: Protection des pages vérifiée")

    print("🎉 PARCOURS UTILISATEUR COMPLET RÉUSSI !")