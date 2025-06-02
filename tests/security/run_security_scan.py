# tests/security/run_security_scan.py
"""
#!/usr/bin/env python3
import subprocess
import sys

def run_bandit_scan():
    \"\"\"Analyse sécurité avec Bandit\"\"\"
    print("=== Analyse sécurité Bandit ===")
    result = subprocess.run([
        'bandit', '-r', 'python_file/',
        '-f', 'json',
        '-o', 'security_report.json'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Aucun problème de sécurité détecté")
    else:
        print("❌ Problèmes de sécurité détectés")
        print(result.stdout)

    return result.returncode

def run_safety_check():
    \"\"\"Vérification vulnérabilités dépendances\"\"\"
    print("=== Vérification vulnérabilités ===")
    result = subprocess.run([
        'safety', 'check',
        '--json'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Aucune vulnérabilité détectée")
    else:
        print("❌ Vulnérabilités détectées")
        print(result.stdout)

    return result.returncode

if __name__ == "__main__":
    bandit_result = run_bandit_scan()
    safety_result = run_safety_check()

    if bandit_result == 0 and safety_result == 0:
        print("\\n🔒 Tous les tests de sécurité sont passés")
        sys.exit(0)
    else:
        print("\\n⚠️  Des problèmes de sécurité ont été détectés")
        sys.exit(1)
"""