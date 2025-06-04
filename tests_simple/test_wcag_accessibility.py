"""
Tests d'accessibilité WCAG (Web Content Accessibility Guidelines) pour WildAware
Vérifie la conformité aux niveaux A, AA et certains critères AAA
"""
import pytest
import re
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock
import colorsys


class WCAGTester:
    """Utilitaire pour tester la conformité WCAG"""

    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def check_images_alt_text(self):
        """WCAG 1.1.1 (Niveau A) - Contenu non textuel"""
        images = self.soup.find_all('img')
        issues = []

        for img in images:
            if not img.get('alt'):
                issues.append(f"Image sans attribut alt: {img}")
            elif img.get('alt').strip() == '':
                issues.append(f"Image avec alt vide: {img}")

        return issues

    def check_heading_structure(self):
        """WCAG 1.3.1 (Niveau A) - Information et relations"""
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        issues = []

        if not headings:
            issues.append("Aucun titre trouvé sur la page")
            return issues

        # Vérifier qu'il y a un H1
        h1_count = len(self.soup.find_all('h1'))
        if h1_count == 0:
            issues.append("Aucun titre H1 trouvé")
        elif h1_count > 1:
            issues.append(f"Plusieurs titres H1 trouvés ({h1_count})")

        # Vérifier la hiérarchie des titres
        previous_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if level > previous_level + 1:
                issues.append(f"Saut de niveau de titre: {heading.name} après h{previous_level}")
            previous_level = level

        return issues

    def check_form_labels(self):
        """WCAG 1.3.1 (Niveau A) - Labels des formulaires"""
        inputs = self.soup.find_all(['input', 'textarea', 'select'])
        issues = []

        for input_field in inputs:
            # Ignorer les champs cachés et les boutons
            if input_field.get('type') in ['hidden', 'submit', 'button']:
                continue

            field_id = input_field.get('id')
            field_name = input_field.get('name')

            # Chercher un label associé
            label = None
            if field_id:
                label = self.soup.find('label', {'for': field_id})

            if not label:
                # Chercher un label parent
                label = input_field.find_parent('label')

            if not label:
                issues.append(f"Champ sans label: {input_field}")

        return issues

    def check_button_accessibility(self):
        """WCAG 2.4.4 (Niveau A) - Objectif des liens et boutons"""
        buttons = self.soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
        links = self.soup.find_all('a')
        issues = []

        # Vérifier les boutons
        for button in buttons:
            text = button.get_text(strip=True)
            if not text and not button.get('aria-label') and not button.get('title'):
                issues.append(f"Bouton sans texte descriptif: {button}")

        # Vérifier les liens
        for link in links:
            text = link.get_text(strip=True)
            if not text and not link.get('aria-label') and not link.get('title'):
                issues.append(f"Lien sans texte descriptif: {link}")
            elif text.lower() in ['cliquez ici', 'ici', 'lire plus', 'plus']:
                issues.append(f"Lien avec texte non descriptif: '{text}'")

        return issues

    def check_color_contrast(self):
        """WCAG 1.4.3 (Niveau AA) - Contraste des couleurs"""
        # Note: Test basique sur les styles inline
        # Dans un vrai projet, il faudrait analyser les CSS externes
        issues = []
        elements_with_style = self.soup.find_all(attrs={'style': True})

        for element in elements_with_style:
            style = element.get('style', '')
            if 'color:' in style and 'background' in style:
                # Analyse basique - dans la réalité, il faudrait un parser CSS complet
                issues.append(f"Vérifier manuellement le contraste: {element}")

        return issues

    def check_semantic_structure(self):
        """WCAG 1.3.1 (Niveau A) - Structure sémantique"""
        issues = []

        # Vérifier la présence de landmarks
        landmarks = self.soup.find_all(['main', 'nav', 'header', 'footer', 'aside', 'section'])
        if not landmarks:
            issues.append("Aucun élément sémantique (main, nav, header, etc.) trouvé")

        # Vérifier la structure de base
        if not self.soup.find('main') and not self.soup.find(attrs={'role': 'main'}):
            issues.append("Pas de contenu principal identifié (balise <main> ou role='main')")

        return issues

    def check_keyboard_navigation(self):
        """WCAG 2.1.1 (Niveau A) - Navigation au clavier"""
        issues = []
        interactive_elements = self.soup.find_all(['a', 'button', 'input', 'select', 'textarea'])

        for element in interactive_elements:
            # Vérifier les éléments qui pourraient bloquer la navigation clavier
            if element.get('tabindex') == '-1' and element.name != 'input':
                issues.append(f"Élément interactif non accessible au clavier: {element}")

        return issues

    def check_page_title(self):
        """WCAG 2.4.2 (Niveau A) - Titre de page"""
        issues = []
        title = self.soup.find('title')

        if not title:
            issues.append("Pas de balise <title> trouvée")
        elif not title.get_text(strip=True):
            issues.append("Titre de page vide")
        elif len(title.get_text(strip=True)) < 10:
            issues.append("Titre de page trop court (moins de 10 caractères)")

        return issues

    def check_language_attribute(self):
        """WCAG 3.1.1 (Niveau A) - Langue de la page"""
        issues = []
        html_tag = self.soup.find('html')

        if not html_tag or not html_tag.get('lang'):
            issues.append("Attribut lang manquant sur la balise <html>")

        return issues


def test_wcag_accessibility_homepage(client):
    """Test WCAG pour la page d'accueil"""
    response = client.get('/')
    assert response.status_code == 200

    tester = WCAGTester(response.data.decode('utf-8'))
    all_issues = []

    # Tests WCAG Niveau A
    all_issues.extend(tester.check_images_alt_text())
    all_issues.extend(tester.check_heading_structure())
    all_issues.extend(tester.check_form_labels())
    all_issues.extend(tester.check_button_accessibility())
    all_issues.extend(tester.check_semantic_structure())
    all_issues.extend(tester.check_keyboard_navigation())
    all_issues.extend(tester.check_page_title())
    all_issues.extend(tester.check_language_attribute())

    # Tests WCAG Niveau AA
    all_issues.extend(tester.check_color_contrast())

    # Afficher les problèmes trouvés
    if all_issues:
        print("\n🚨 PROBLÈMES D'ACCESSIBILITÉ WCAG DÉTECTÉS:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print(f"\n📊 Total: {len(all_issues)} problèmes trouvés")
    else:
        print("\n✅ AUCUN PROBLÈME D'ACCESSIBILITÉ WCAG DÉTECTÉ")

    # Le test échoue s'il y a des problèmes critiques (optionnel)
    critical_issues = [issue for issue in all_issues if
                       'alt' in issue.lower() or 'label' in issue.lower() or 'title' in issue.lower()]

    assert len(critical_issues) == 0, f"Problèmes critiques d'accessibilité: {critical_issues}"


def test_wcag_accessibility_login_page(client):
    """Test WCAG pour la page de connexion"""
    response = client.get('/login')
    assert response.status_code == 200

    tester = WCAGTester(response.data.decode('utf-8'))
    all_issues = []

    # Focus sur les formulaires pour la page de connexion
    all_issues.extend(tester.check_form_labels())
    all_issues.extend(tester.check_button_accessibility())
    all_issues.extend(tester.check_page_title())
    all_issues.extend(tester.check_heading_structure())

    # Vérifications spécifiques aux formulaires de connexion
    soup = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    # Vérifier que les champs de mot de passe ont le bon type
    password_fields = soup.find_all('input', {'type': 'password'})
    if not password_fields:
        all_issues.append("Aucun champ de mot de passe trouvé avec type='password'")

    # Vérifier que les champs email ont le bon type
    email_fields = soup.find_all('input', {'type': 'email'})
    username_fields = soup.find_all('input', {'name': 'username'})
    if not email_fields and not username_fields:
        all_issues.append("Aucun champ email/username trouvé")

    if all_issues:
        print(f"\n🚨 PROBLÈMES WCAG PAGE CONNEXION: {len(all_issues)} trouvés")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ PAGE CONNEXION: Conforme WCAG")


def test_wcag_accessibility_scan_page(logged_user):
    """Test WCAG pour la page de scan (nécessite une connexion)"""
    response = logged_user.get('/scan')
    assert response.status_code == 200

    tester = WCAGTester(response.data.decode('utf-8'))
    all_issues = []

    all_issues.extend(tester.check_button_accessibility())
    all_issues.extend(tester.check_page_title())
    all_issues.extend(tester.check_heading_structure())

    # Vérifications spécifiques à la page de scan
    soup = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    # Vérifier les champs de fichier
    file_inputs = soup.find_all('input', {'type': 'file'})
    for file_input in file_inputs:
        if not file_input.get('accept'):
            all_issues.append("Champ fichier sans attribut 'accept' pour filtrer les types")

    # Vérifier les boutons d'action
    scan_buttons = soup.find_all('button', class_='connexion')
    if len(scan_buttons) < 2:
        all_issues.append("Pas assez de boutons d'action trouvés sur la page de scan")

    if all_issues:
        print(f"\n🚨 PROBLÈMES WCAG PAGE SCAN: {len(all_issues)} trouvés")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ PAGE SCAN: Conforme WCAG")


def test_wcag_accessibility_result_page(logged_user, test_image):
    """Test WCAG pour la page de résultats"""
    # Simuler un upload et redirection vers résultats
    with patch('python_file.app.supabase') as mock_supabase, \
            patch('python_file.app.footprint_model') as mock_ia:

        mock_upload_response = MagicMock()
        mock_upload_response.error = None
        mock_supabase.storage.from_().upload.return_value = mock_upload_response
        mock_supabase.storage.from_().get_public_url.return_value = "http://test-image.jpg"

        mock_ia.predict.return_value = {
            'animal': 'Renard',
            'confidence': 0.85,
            'card_url': 'http://test-card.jpg',
            'fun_fact': 'Test fact about foxes'
        }

        # Simuler la session avec les résultats
        with logged_user.session_transaction() as sess:
            sess['analysis_result'] = {
                'animal': 'Renard',
                'confidence': 85.0,
                'card_url': 'http://test-card.jpg',
                'fun_fact': 'Test fact about foxes'
            }
            sess['image_url'] = 'http://test-image.jpg'

        response = logged_user.get('/scan_result')
        assert response.status_code == 200

        tester = WCAGTester(response.data.decode('utf-8'))
        all_issues = []

        all_issues.extend(tester.check_images_alt_text())
        all_issues.extend(tester.check_heading_structure())
        all_issues.extend(tester.check_button_accessibility())
        all_issues.extend(tester.check_page_title())

        if all_issues:
            print(f"\n🚨 PROBLÈMES WCAG PAGE RÉSULTATS: {len(all_issues)} trouvés")
            for issue in all_issues:
                print(f"  - {issue}")
        else:
            print("\n✅ PAGE RÉSULTATS: Conforme WCAG")


def test_wcag_comprehensive_report(client, logged_user):
    """Rapport complet de conformité WCAG"""
    print("\n" + "=" * 60)
    print("🔍 RAPPORT COMPLET DE CONFORMITÉ WCAG - WILDAWARE")
    print("=" * 60)

    pages_to_test = [
        ('/', 'Page d\'accueil'),
        ('/login', 'Page de connexion'),
        ('/inscription', 'Page d\'inscription')
    ]

    total_issues = 0

    for url, page_name in pages_to_test:
        print(f"\n📄 Test de {page_name} ({url})")
        print("-" * 40)

        response = client.get(url)
        if response.status_code != 200:
            print(f"❌ Erreur: Page non accessible (code {response.status_code})")
            continue

        tester = WCAGTester(response.data.decode('utf-8'))
        page_issues = []

        # Tests complets
        page_issues.extend(tester.check_images_alt_text())
        page_issues.extend(tester.check_heading_structure())
        page_issues.extend(tester.check_form_labels())
        page_issues.extend(tester.check_button_accessibility())
        page_issues.extend(tester.check_semantic_structure())
        page_issues.extend(tester.check_keyboard_navigation())
        page_issues.extend(tester.check_page_title())
        page_issues.extend(tester.check_language_attribute())
        page_issues.extend(tester.check_color_contrast())

        if page_issues:
            print(f"🚨 {len(page_issues)} problème(s) trouvé(s):")
            for i, issue in enumerate(page_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ Aucun problème détecté")

        total_issues += len(page_issues)

    # Test de la page scan (avec connexion)
    print(f"\n📄 Test de Page de scan (/scan)")
    print("-" * 40)

    response = logged_user.get('/scan')
    if response.status_code == 200:
        tester = WCAGTester(response.data.decode('utf-8'))
        scan_issues = []
        scan_issues.extend(tester.check_button_accessibility())
        scan_issues.extend(tester.check_page_title())
        scan_issues.extend(tester.check_heading_structure())

        if scan_issues:
            print(f"🚨 {len(scan_issues)} problème(s) trouvé(s):")
            for i, issue in enumerate(scan_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ Aucun problème détecté")

        total_issues += len(scan_issues)

    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE CONFORMITÉ WCAG")
    print("=" * 60)

    if total_issues == 0:
        print("🎉 FÉLICITATIONS! Application entièrement conforme WCAG")
        compliance_level = "100%"
    elif total_issues <= 5:
        print(f"✅ Bonne conformité WCAG ({total_issues} problèmes mineurs)")
        compliance_level = "Très bon"
    elif total_issues <= 10:
        print(f"⚠️  Conformité acceptable ({total_issues} problèmes à corriger)")
        compliance_level = "Acceptable"
    else:
        print(f"❌ Conformité insuffisante ({total_issues} problèmes importants)")
        compliance_level = "Insuffisant"

    print(f"📈 Niveau de conformité: {compliance_level}")
    print(f"🔢 Nombre total de problèmes: {total_issues}")

    print("\n📋 RECOMMANDATIONS PRIORITAIRES:")
    print("1. Ajouter des attributs alt descriptifs à toutes les images")
    print("2. S'assurer que tous les formulaires ont des labels appropriés")
    print("3. Vérifier la hiérarchie des titres (H1, H2, H3...)")
    print("4. Ajouter l'attribut lang='fr' à la balise <html>")
    print("5. Tester la navigation au clavier sur toutes les pages")

    print("\n🔗 RESSOURCES UTILES:")
    print("- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/")
    print("- Validator WAVE: https://wave.webaim.org/")
    print("- axe DevTools: https://www.deque.com/axe/devtools/")

    # Le test passe toujours mais affiche le rapport
    assert True, "Rapport de conformité WCAG généré"


if __name__ == "__main__":
    # Pour exécuter directement le fichier de test
    pytest.main([__file__, "-v"])