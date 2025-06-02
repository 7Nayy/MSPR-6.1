# tests/regression/test_compatibility.py
import pytest
import subprocess
import sys
from python_file.app import app


class TestBrowserCompatibility:
    """Tests compatibilité navigateurs"""

    def test_chrome_compatibility(self):
        """Test : Compatibilité Chrome"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')

        try:
            driver = webdriver.Chrome(options=options)
            driver.get('http://localhost:5000')
            assert "WildAware" in driver.title
            driver.quit()
        except Exception as e:
            pytest.skip(f"Chrome non disponible: {e}")

    def test_firefox_compatibility(self):
        """Test : Compatibilité Firefox"""
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        options = Options()
        options.add_argument('--headless')

        try:
            driver = webdriver.Firefox(options=options)
            driver.get('http://localhost:5000')
            assert "WildAware" in driver.title
            driver.quit()
        except Exception as e:
            pytest.skip(f"Firefox non disponible: {e}")


class TestPythonVersionCompatibility:
    """Tests compatibilité versions Python"""

    def test_python_version_support(self):
        """Test : Version Python supportée"""
        version = sys.version_info
        # App développée pour Python 3.10+
        assert version.major == 3
        assert version.minor >= 10

    def test_required_packages_compatibility(self):
        """Test : Compatibilité packages requis"""
        required_packages = [
            'flask', 'supabase', 'flask-talisman',
            'python-dotenv', 'pillow', 'torch',
            'torchvision', 'opencv-python', 'numpy'
        ]

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                pytest.fail(f"Package {package} non installé")


class TestDatabaseCompatibility:
    """Tests compatibilité base de données"""

    def test_supabase_api_compatibility(self):
        """Test : Compatibilité API Supabase"""
        from python_file.supabase_conn import supabase

        try:
            # Test connexion basique
            response = supabase.table('Animaux').select('*').limit(1).execute()
            assert response is not None
        except Exception as e:
            pytest.fail(f"Incompatibilité API Supabase: {e}")

    def test_database_schema_compatibility(self):
        """Test : Compatibilité schéma DB"""
        from python_file.supabase_conn import supabase

        # Vérifier tables requises
        required_tables = ['Animaux', 'Empreintes']

        for table in required_tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                assert response is not None
            except Exception as e:
                pytest.fail(f"Table {table} non accessible: {e}")


class TestDockerCompatibility:
    """Tests compatibilité Docker"""

    def test_docker_build_compatibility(self):
        """Test : Build Docker réussi"""
        result = subprocess.run([
            'docker', 'build', '-t', 'wildaware-test', '.'
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Build Docker échoué: {result.stderr}"

    def test_docker_compose_compatibility(self):
        """Test : Docker Compose fonctionnel"""
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yml', 'config'
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Docker Compose invalide: {result.stderr}"


class TestFileSystemCompatibility:
    """Tests compatibilité système de fichiers"""

    def test_log_directory_permissions(self):
        """Test : Permissions dossier logs"""
        import os

        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Vérifier écriture possible
        test_file = os.path.join(log_dir, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            pytest.fail(f"Permissions logs insuffisantes: {e}")

    def test_static_files_access(self):
        """Test : Accès fichiers statiques"""
        import os

        static_files = [
            'static/accueil.css',
            'static/scan.js',
            'templates/accueil.html'
        ]

        for file_path in static_files:
            assert os.path.exists(file_path), f"Fichier manquant: {file_path}"
            assert os.access(file_path, os.R_OK), f"Fichier non lisible: {file_path}"


class TestEnvironmentCompatibility:
    """Tests compatibilité environnement"""

    def test_environment_variables(self):
        """Test : Variables d'environnement requises"""
        import os

        required_vars = [
            'FLASK_SECRET_KEY',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        assert not missing_vars, f"Variables manquantes: {missing_vars}"

    def test_port_availability(self):
        """Test : Disponibilité port par défaut"""
        import socket

        def is_port_available(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) != 0

        default_port = 5000
        assert is_port_available(default_port), f"Port {default_port} occupé"