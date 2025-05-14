# Documentation WildLens

## Présentation du projet

WildLens est une application web mobile qui permet aux utilisateurs d'identifier automatiquement des traces d'animaux à partir de photos prises sur le terrain. L'application utilise un modèle d'intelligence artificielle pour analyser les images et fournir des informations détaillées sur l'espèce animale identifiée, contribuant ainsi à l'éducation environnementale et à la sensibilisation à la faune locale.

## Architecture technique

### Composants principaux

1. **Backend (Flask)** : API web développée en Python avec le framework Flask
2. **Frontend** : Interface utilisateur en HTML/CSS/JavaScript
3. **Base de données** : Utilisation de Supabase pour le stockage des données et l'authentification
4. **IA** : Modèle de reconnaissance d'empreintes basé sur PyTorch
5. **Conteneurisation** : Docker pour standardiser le déploiement
6. **CI/CD** : GitHub Actions pour l'intégration et le déploiement continus

### Structure des dossiers

```
wildlens/
├── .github/                # Configuration GitHub Actions
│   └── workflows/
│       └── ci-cd.yml
├── python_file/            # Code backend
│   ├── app.py              # Application principale Flask
│   ├── footprint_recognition.py  # Modèle de reconnaissance
│   ├── supabase_conn.py    # Connexion à Supabase
│   └── ...
├── static/                 # Ressources statiques (CSS, JS)
│   ├── accueil.css
│   ├── scan.js
│   └── ...
├── templates/              # Fichiers HTML
│   ├── accueil.html
│   ├── scan.html
│   └── ...
├── logs/                   # Dossier pour les logs (créé automatiquement)
├── Dockerfile              # Configuration Docker pour la production
├── Dockerfile.dev          # Configuration Docker pour le développement
├── docker-compose.yml      # Configuration Docker Compose pour la production
├── docker-compose.dev.yml  # Configuration Docker Compose pour le développement
└── requirements.txt        # Dépendances Python
```

## Fonctionnalités

### 1. Classification d'une photo d'empreinte

L'application permet d'identifier automatiquement des empreintes d'animaux à partir d'une photo. Le processus suit ces étapes :

1. L'utilisateur peut prendre une photo avec l'appareil photo de son appareil ou importer une image existante
2. L'image est traitée côté client (compression, redimensionnement) pour optimiser le transfert
3. L'image est envoyée au serveur via une requête AJAX
4. L'image est stockée dans Supabase (bucket `UserImg`)
5. Le modèle d'IA analyse l'image pour identifier l'espèce animale
6. Le résultat est retourné à l'utilisateur avec le niveau de confiance

L'application peut identifier 13 espèces différentes :
- Renard
- Loup
- Raton laveur
- Lynx
- Ours
- Castor
- Chat
- Chien
- Coyote
- Ecureuil
- Lapin
- Puma
- Rat

### 2. Affichage des informations sur l'espèce reconnue

Une fois l'empreinte identifiée, l'application affiche :
- Le nom de l'animal identifié
- Le niveau de confiance de la prédiction (en pourcentage)
- Une carte d'information sur l'animal
- Un fait amusant ou éducatif sur l'espèce

### 3. Recueil des données de prise de photo

Chaque capture d'image est enregistrée dans Supabase avec les informations suivantes :
- L'image originale (stockée dans le bucket `UserImg`)
- Un identifiant unique basé sur l'utilisateur et l'horodatage
- L'identifiant de l'utilisateur qui a réalisé la capture
- Le résultat de l'analyse (animal identifié, confiance)

Ces données contribuent à enrichir la base de connaissances du système et pourront être utilisées pour améliorer le modèle d'IA.

## Installation et déploiement

### Prérequis

- Docker et Docker Compose
- Un compte Supabase avec les buckets configurés :
  - `UserImg` : pour stocker les images des utilisateurs
  - `Dirty_Footprint` : pour les images brutes d'empreintes
  - `Empreintes` : pour les images traitées d'empreintes

### Configuration de Supabase

1. Créer un projet sur [Supabase](https://supabase.com)
2. Dans "Storage", créer les buckets mentionnés ci-dessus
3. Dans "Database", créer les tables suivantes :
   - `Animaux` : informations sur les espèces animales
   - `Empreintes` : catalogue d'empreintes connues
4. Récupérer l'URL et la clé API dans les paramètres du projet

### Déploiement en développement

1. Cloner le dépôt
   ```bash
   git clone https://github.com/7Nayy/MSPR-6.1.git
   cd wildlens
   ```

2. Créer un fichier `.env` à la racine du projet
   ```
   FLASK_SECRET_KEY=votre_clé_secrète
   FLASK_DEBUG=True
   FLASK_ENV=development
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_KEY=votre-clé-supabase
   ```

3. Lancer l'environnement de développement avec Docker
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. Accéder à l'application
   L'application sera disponible à l'adresse http://localhost:5001

### Déploiement en production

1. Configurer les variables d'environnement de production
   ```
   FLASK_SECRET_KEY=votre_clé_secrète_production
   FLASK_DEBUG=False
   FLASK_ENV=production
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_KEY=votre-clé-supabase
   ```

2. Construire et démarrer les conteneurs
   ```bash
   docker-compose up -d --build
   ```

3. Configuration d'un serveur web (optionnel)
   Pour un déploiement en production, il est recommandé d'utiliser un serveur web comme Nginx en frontal :

   ```nginx
   server {
       listen 80;
       server_name votre-domaine.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## CI/CD avec GitHub Actions

Le projet utilise GitHub Actions pour l'intégration et le déploiement continus. Le workflow est défini dans `.github/workflows/ci-cd.yml` et comprend :

1. **Test** : Exécution des vérifications de qualité de code et des tests unitaires
2. **Build** : Construction de l'image Docker
3. **Deploy** : Déploiement automatique sur les environnements appropriés

Les branches sont configurées comme suit :
- `pre-prod` : Environnement de pré-production/staging
- `prod` : Environnement de production

Pour utiliser le pipeline CI/CD, assurez-vous de configurer les secrets GitHub suivants :
- `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` pour le registre Docker
- `STAGING_HOST`, `STAGING_USER`, `STAGING_SSH_KEY` pour le serveur de staging
- `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY` pour le serveur de production

## Modèle de reconnaissance d'empreintes

Le modèle d'IA utilise PyTorch pour la reconnaissance des empreintes animales. Dans l'implémentation actuelle :

1. La classe `FootprintRecognition` dans `footprint_recognition.py` utilise une approche de simulation qui :
   - Génère un hachage à partir de l'image pour obtenir une prédiction stable
   - Renvoie l'une des 13 espèces supportées
   - Récupère les informations de l'espèce depuis Supabase

2. Pour implémenter un vrai modèle de reconnaissance :
   - Collecter et étiqueter un dataset d'images d'empreintes
   - Entrainer un réseau de neurones convolutif (CNN)
   - Convertir le modèle avec `convert_model.py`
   - Remplacer le modèle factice par le modèle entrainé

## Sécurité

L'application intègre plusieurs mesures de sécurité :

1. **HTTPS** : Utilisation de Flask-Talisman pour renforcer la sécurité HTTP
2. **Protection contre les attaques XSS** : Content Security Policy configurée
3. **Stockage sécurisé des utilisateurs** : Géré par Supabase Auth
4. **Validation des entrées** : Vérification côté serveur des données reçues
5. **Limites de taille pour les uploads** : Configuration de la taille maximale des fichiers

## Maintenance et mises à jour

### Mise à jour des dépendances

Pour mettre à jour les dépendances du projet :

```bash
pip install --upgrade -r requirements.txt
```

Il est recommandé de vérifier régulièrement les vulnérabilités dans les dépendances :

```bash
pip install safety
safety check
```

### Sauvegarde des données

La sauvegarde des données est gérée par Supabase, mais il est recommandé d'exporter régulièrement :
- La structure de la base de données
- Les images stockées dans les buckets

### Surveillance des logs

Les logs de l'application sont stockés dans le dossier `logs/` et sont également accessibles via Docker :

```bash
docker-compose logs -f wildaware-app
```

## Dépannage

### Problèmes courants et solutions

1. **Erreur d'accès à Supabase**
   
   Vérifiez les variables d'environnement `SUPABASE_URL` et `SUPABASE_KEY`.

2. **L'application ne démarre pas**
   
   Vérifiez les logs de l'application :
   ```bash
   docker-compose logs wildaware-app
   ```

3. **Erreur lors du chargement du modèle**
   
   Assurez-vous que le modèle est correctement configuré dans `footprint_recognition.py`.

4. **Problèmes d'upload d'images**
   
   Vérifiez la taille des images (limite de 16 Mo) et les permissions du bucket Supabase.

5. **Port déjà utilisé**
   
   Modifiez le port dans le fichier docker-compose :
   ```yaml
   ports:
     - "5002:5000"  # Utilise le port 5002 au lieu de 5000/5001
   ```

## Contribution au projet

Pour contribuer au projet :

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Committer vos changements
   ```bash
   git commit -m "feat: Ajouter une nouvelle fonctionnalité"
   ```
4. Pousser vers votre fork
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
5. Ouvrir une Pull Request
