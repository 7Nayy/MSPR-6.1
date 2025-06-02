#!/usr/bin/env python3
"""
Script pour lancer les tests avec l'environnement correct
Usage: python run_tests.py
"""
import os
import sys
import subprocess


def main():
    # Configuration de l'environnement
    env = os.environ.copy()
    env.update({
        'TESTING': 'True',
        'FLASK_ENV': 'testing',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key-for-testing',
        'FLASK_SECRET_KEY': 'test-secret-key'
    })

    # Commande pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests_simple/',
        '-v',
        '--tb=short'
    ]

    print("🚀 Lancement des tests avec environnement de test...")
    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
