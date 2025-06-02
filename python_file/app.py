from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
from flask_talisman import Talisman
from datetime import timedelta
from functools import wraps
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from PIL import Image
from io import BytesIO
import base64
import time
import torch
from python_file.footprint_recognition import initialize_model, footprint_model

load_dotenv()

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mo
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialisation du modèle d'IA - Changé pour un fichier .pth
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'animal_footprint_model_safe.pth')
try:
    initialize_model(MODEL_PATH)
    app.logger.info('Modèle d\'IA PyTorch chargé avec succès')
except Exception as e:
    app.logger.error(f'Erreur lors du chargement du modèle d\'IA: {str(e)}')

if os.getenv('FLASK_ENV') == 'production':
    Talisman(app,
             force_https=True,
             strict_transport_security=True,
             session_cookie_secure=True,
             content_security_policy={
                 'default-src': "'self'",
                 'script-src': ["'self'", "'unsafe-inline'"],
                 'style-src': ["'self'", "'unsafe-inline'"],
                 'img-src': ["'self'", "data:", "blob:", "*"]  # Ajout de "*" pour les images externes
             })
else:
    Talisman(app,
             force_https=False,
             session_cookie_secure=False,
             content_security_policy={
                 'default-src': "'self'",
                 'script-src': ["'self'", "'unsafe-inline'"],
                 'style-src': ["'self'", "'unsafe-inline'"],
                 'img-src': ["'self'", "data:", "blob:", "*"]  # Ajout de "*" pour les images externes
             })

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Démarrage de l\'application')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('accueil.html')


@app.route('/accueil')
def accueil():
    return render_template('accueil.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not email or not password:
                raise ValueError("Email et mot de passe requis")

            if not '@' in email:
                raise ValueError("Format d'email invalide")

            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session.permanent = True
            session['user_id'] = response.user.id
            session['email'] = email
            app.logger.info(f'Connexion réussie pour l\'utilisateur: {email}')

            return redirect(url_for('scan'))

        except ValueError as e:
            app.logger.warning(f'Tentative de connexion invalide: {str(e)}')
            return render_template('connexion.html', error=str(e))
        except Exception as e:
            app.logger.error(f'Erreur de connexion: {str(e)}')
            return render_template('connexion.html',
                                   error="Une erreur est survenue lors de la connexion")

    return render_template('connexion.html')


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        try:
            email = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not email or not password or not confirm_password:
                raise ValueError("Tous les champs sont obligatoires")

            if not '@' in email:
                raise ValueError("Format d'email invalide")

            if len(password) < 8:
                raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

            if password != confirm_password:
                raise ValueError("Les mots de passe ne correspondent pas")

            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            session.permanent = True
            session['user_id'] = response.user.id
            session['email'] = email
            app.logger.info(f'Inscription réussie pour l\'utilisateur: {email}')

            return redirect(url_for('scan'))

        except ValueError as e:
            app.logger.warning(f'Tentative d\'inscription invalide: {str(e)}')
            return render_template('inscription.html', error=str(e))
        except Exception as e:
            app.logger.error(f'Erreur lors de l\'inscription: {str(e)}')
            return render_template('inscription.html',
                                   error="Une erreur est survenue lors de l'inscription")

    return render_template('inscription.html')


@app.route('/scan')
@login_required
def scan():
    try:
        email = session.get('email', 'Utilisateur inconnu')
        return render_template('scan.html', email=email)
    except Exception as e:
        app.logger.error(f'Erreur dans la page scan: {str(e)}')
        return redirect(url_for('login'))


@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    try:
        app.logger.info("Début de l'upload")

        # Vérifier si un fichier a été envoyé
        if 'image' not in request.files:
            app.logger.error("Pas d'image dans la requête")
            return jsonify({'success': False, 'error': 'Pas d\'image reçue'})

        uploaded_file = request.files['image']
        if not uploaded_file:
            app.logger.error("Fichier vide")
            return jsonify({'success': False, 'error': 'Fichier vide'})

        # Lire les données du fichier
        image_bytes = uploaded_file.read()

        # Génération du nom de fichier
        timestamp = int(time.time())
        filename = f"scan_{session['user_id']}_{timestamp}.jpg"
        user_email = session.get('email').replace('@', '_at_')  # Création d'un nom de dossier sécurisé

        try:
            # Upload uniquement dans UserImg avec dossier utilisateur
            app.logger.info(f"Upload vers UserImg/{user_email}")
            user_path = f"{user_email}/{filename}"

            response_user = supabase.storage \
                .from_('UserImg') \
                .upload(
                path=user_path,
                file=image_bytes,
                file_options={"content-type": "image/jpeg"}
            )

            if hasattr(response_user, 'error') and response_user.error is not None:
                raise Exception(f"Erreur UserImg: {response_user.error}")

            # Obtenir l'URL publique de l'image
            image_url = supabase.storage.from_('UserImg').get_public_url(user_path)

            # Analyse de l'image avec l'IA
            try:
                app.logger.info("Analyse de l'image avec l'IA")

                # Au lieu de stocker l'image complète en session, stockons seulement l'URL
                session['image_url'] = image_url  # Nouvelle ligne

                # Analyser l'image avec le modèle d'IA
                result = footprint_model.predict(image_bytes)

                # Stocker les résultats en session (mais pas l'image complète)
                session['analysis_result'] = {
                    'animal': result['animal'],
                    'confidence': result['confidence'] * 100,  # Convertir en pourcentage
                    'card_url': result['card_url'],
                    'fun_fact': result['fun_fact']
                }

                app.logger.info(f"Animal identifié: {result['animal']} avec une confiance de {result['confidence']}")

                # Rediriger vers la page de résultats
                return jsonify({'success': True, 'redirect': url_for('scan_result')})

            except Exception as e:
                app.logger.error(f"Erreur lors de l'analyse de l'image: {str(e)}")
                return jsonify({'success': False, 'error': f"Erreur lors de l'analyse: {str(e)}"})

        except Exception as e:
            app.logger.error(f'Erreur lors de l\'upload Supabase : {str(e)}')
            return jsonify({'success': False, 'error': str(e)})

    except Exception as e:
        app.logger.error(f'Erreur générale : {str(e)}')
        return jsonify({'success': False, 'error': str(e)})

# Modifiez également la route scan_result pour utiliser l'URL de l'image au lieu de l'image en base64
@app.route('/scan_result')
@login_required
def scan_result():
    try:
        if 'analysis_result' not in session:
            return redirect(url_for('scan'))

        result = session['analysis_result']
        # Utilisez l'URL de l'image au lieu de l'image en base64
        image_url = session.get('image_url', '')
        email = session.get('email', 'Utilisateur inconnu')

        return render_template('scan_result.html',
                               email=email,
                               image_url=image_url,  # Passez l'URL au template
                               animal=result['animal'],
                               confidence=result['confidence'],
                               card_url=result['card_url'],
                               fun_fact=result['fun_fact'])

    except Exception as e:
        app.logger.error(f'Erreur lors de l\'affichage des résultats: {str(e)}')
        return redirect(url_for('scan'))


@app.route('/logout')
def logout():
    try:
        if 'user_id' in session:
            email = session.get('email', 'Utilisateur inconnu')
            supabase.auth.sign_out()
            app.logger.info(f'Déconnexion réussie pour l\'utilisateur: {email}')
    except Exception as e:
        app.logger.error(f'Erreur lors de la déconnexion: {str(e)}')
    finally:
        session.clear()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Erreur serveur: {error}')
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')