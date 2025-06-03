# WildAware 🐾

Application web de reconnaissance d'empreintes d'animaux sauvages utilisant l'intelligence artificielle.

## 📋 Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Monitoring](#monitoring)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [API](#api)
- [Contribution](#contribution)

## 🎯 Présentation

WildAware est une application web qui permet d'identifier automatiquement les animaux sauvages à partir de photos de leurs empreintes. L'application utilise un modèle d'intelligence artificielle pour analyser les traces et fournir des informations détaillées sur l'animal identifié.

### Technologies utilisées

- **Backend**: Python Flask
- **Base de données**: Supabase (PostgreSQL)
- **IA**: PyTorch pour la reconnaissance d'images
- **Frontend**: HTML, CSS, JavaScript
- **Déploiement**: Docker, Docker Compose
- **Monitoring**: UptimeRobot, Grafana Cloud (optionnel)
- **Tests**: Pytest

## ✨ Fonctionnalités

- 🔐 **Authentification utilisateur** (inscription/connexion)
- 📸 **Upload d'images** via caméra ou fichier
- 🤖 **Reconnaissance IA** d'empreintes d'animaux
- 📊 **Résultats détaillés** avec niveau de confiance
- 🎴 **Cartes informatives** sur chaque animal
- 📱 **Interface responsive** mobile-friendly
- 🔒 **Sécurité** avec Talisman (HTTPS, CSP, etc.)

### Animaux reconnus

L'application peut identifier 13 espèces d'animaux :
- Renard, Loup, Raton laveur, Lynx, Ours
- Castor, Chat, Chien, Coyote, Écureuil
- Lapin, Puma, Rat

## 🏗️ Architecture

```
WildAware/
├── python_file/           # Code principal de l'application
│   ├── app.py            # Application Flask principale
│   ├── footprint_recognition.py  # Modèle IA de reconnaissance
│   ├── supabase_conn.py  # Connexion base de données
│   └── .env              # Variables d'environnement
├── static/               # Fichiers statiques (CSS, JS, images)
├── templates/            # Templates HTML Jinja2
├── tests_simple/         # Tests unitaires et d'intégration
├── logs/                 # Logs de l'application
├── docker-compose.*.yml  # Configurations Docker
└── requirements.txt      # Dépendances Python
```

## 🚀 Installation

### Prérequis

- Python 3.10+
- Docker et Docker Compose
- Compte Supabase (gratuit)

### Installation locale

1. **Cloner le repository**
```bash
git clone <votre-repo>
cd git_MSPR_6.1
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration de l'environnement**
```bash
# Copier le fichier d'exemple
cp .env.example python_file/.env

# Éditer avec vos credentials Supabase
nano python_file/.env
```

4. **Lancer l'application**
```bash
# Mode développement
docker-compose -f docker-compose.dev.yml up -d

# Ou directement avec Python
cd python_file
python app.py
```

L'application sera accessible sur : http://localhost:5001

## 🐳 Utilisation avec Docker

### Développement
```bash
# Démarrer l'environnement de développement
docker-compose -f docker-compose.dev.yml up -d

# Voir les logs
docker-compose -f docker-compose.dev.yml logs -f

# Arrêter
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Construire et démarrer
docker-compose -f docker-compose.prod.yml up -d

# Avec variables d'environnement
export FLASK_SECRET_KEY="votre-clé-secrète"
export SUPABASE_URL="votre-url-supabase"
export SUPABASE_KEY="votre-clé-supabase"
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### Configuration UptimeRobot

1. **Créer un tunnel public avec ngrok**
```bash
# Installer ngrok
brew install ngrok

# Configurer l'authtoken (depuis https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken VOTRE_TOKEN

# Lancer le tunnel
ngrok http 5001
```

2. **Configurer UptimeRobot**
- Aller sur https://uptimerobot.com
- Créer un nouveau monitor HTTP(s)
- URL : votre URL ngrok (ex: https://abc123.ngrok-free.app)
- Intervalle : 5 minutes

### Monitoring local

```bash
# Script de monitoring simple
python3 << 'EOF'
import requests, time
from datetime import datetime

def check_app():
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        status = "✅ UP" if response.status_code == 200 else f"⚠️ {response.status_code}"
        print(f"{datetime.now().strftime('%H:%M:%S')} - WildAware is {status}")
    except Exception as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} - WildAware is ❌ DOWN: {e}")

while True:
    check_app()
    time.sleep(60)
EOF
```

### Métriques avec Grafana (optionnel)

```bash
# Démarrer Node Exporter pour les métriques système
docker run -d --name node-exporter -p 9100:9100 \
  -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /:/rootfs:ro \
  prom/node-exporter:latest \
  --path.procfs=/host/proc --path.rootfs=/rootfs --path.sysfs=/host/sys

# Lancer le stack de monitoring complet
docker-compose -f docker-compose.monitoring-cloud.yml up -d
```

## 🧪 Tests

### Lancer les tests
```bash
# Tests unitaires et d'intégration
python run_tests.py

# Tests avec couverture
pytest tests_simple/ --cov=python_file --cov-report=html

# Test d'un module spécifique
pytest tests_simple/test_auth.py -v
```

### Tests inclus
- ✅ Tests d'authentification (connexion/inscription)
- ✅ Tests de protection des routes
- ✅ Tests d'upload d'images
- ✅ Test d'intégration complet du parcours utilisateur

## 🚀 Déploiement

### Déploiement automatisé

```bash
# Script de déploiement
chmod +x deploy.sh
./deploy.sh production
```

### Déploiement manuel

1. **Préparer l'environnement de production**
```bash
cp .env.example .env.production
# Éditer .env.production avec les vraies valeurs
```

2. **Construire et déployer**
```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

3. **Vérifier le déploiement**
```bash
curl http://localhost:5001/
docker-compose -f docker-compose.prod.yml ps
```

## 📡 API

### Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/login` | GET/POST | Connexion utilisateur |
| `/inscription` | GET/POST | Inscription utilisateur |
| `/scan` | GET | Page de scan (connecté) |
| `/upload-image` | POST | Upload et analyse d'image |
| `/scan_result` | GET | Résultats d'analyse |
| `/logout` | GET | Déconnexion |

### Exemple d'utilisation de l'API

```python
import requests

# Connexion
session = requests.Session()
response = session.post('http://localhost:5001/login', data={
    'username': 'user@example.com',
    'password': 'password123'
})

# Upload d'image
with open('empreinte.jpg', 'rb') as f:
    response = session.post('http://localhost:5001/upload-image', 
                          files={'image': f})
    result = response.json()
    print(f"Animal identifié: {result}")
```

## 🔧 Configuration

### Variables d'environnement

```bash
# Flask
FLASK_SECRET_KEY=votre-clé-secrète-très-longue
FLASK_DEBUG=False
FLASK_ENV=production

# Supabase
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-clé-service-role

# Déploiement
PORT=5001
DOCKER_REGISTRY=votre-registry
REPLICAS=1
```

### Configuration Supabase

1. **Créer un projet** sur https://supabase.com
2. **Configurer les buckets** de stockage :
   - `UserImg` : Images uploadées par les utilisateurs
   - `Empreintes` : Dataset d'empreintes pour l'IA
3. **Tables principales** :
   - `auth.users` : Gestion des utilisateurs (automatique)
   - `Animaux` : Informations sur les espèces
   - `Empreintes` : Dataset d'images d'empreintes

## 🛠️ Développement

### Structure du code

- `app.py` : Application Flask principale avec toutes les routes
- `footprint_recognition.py` : Modèle IA et logique de reconnaissance
- `supabase_conn.py` : Interface avec la base de données Supabase
- `etl.py` : Scripts de traitement des données d'entraînement

### Ajouter une nouvelle espèce

1. **Ajouter l'espèce** dans `footprint_recognition.py`:
```python
self.class_names = [
    "Renard", "Loup", "Raton laveur", "Lynx", "Ours",
    "Castor", "Chat", "Chien", "Coyote", "Ecureuil",
    "Lapin", "Puma", "Rat", "Nouvelle_Espece"  # Ajouter ici
]
```

2. **Ajouter en base** dans Supabase table `Animaux`

3. **Réentraîner le modèle** avec de nouvelles données

## 🤝 Contribution

1. **Fork** le projet
2. **Créer une branche** (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. **Pousser** (`git push origin feature/nouvelle-fonctionnalite`)
5. **Créer une Pull Request**

### Standards de code

- **Python** : Respecter PEP 8
- **Tests** : Ajouter des tests pour toute nouvelle fonctionnalité
- **Documentation** : Commenter le code et mettre à jour le README
- **Commit** : Messages clairs et descriptifs

## 📞 Support

- **Issues** : Utiliser les GitHub Issues pour signaler des bugs
- **Documentation** : Ce README et les commentaires dans le code
- **Tests** : Vérifier que tous les tests passent avant de contribuer

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

🐾 **WildAware** - Protégeons la faune sauvage grâce à la technologie !