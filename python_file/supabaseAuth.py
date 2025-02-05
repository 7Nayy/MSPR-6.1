from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from flask_talisman import Talisman
from datetime import timedelta
from functools import wraps
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Chargement des variables d'environnement
load_dotenv()

# Configuration de base de Flask
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static'
            )

# Configuration de la sécurité
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Activation des en-têtes de sécurité avec Talisman
if os.getenv('FLASK_ENV') == 'production':
    Talisman(app,
             force_https=True,
             strict_transport_security=True,
             session_cookie_secure=True
             )
else:
    Talisman(app,
             force_https=False,
             session_cookie_secure=False
             )

# Configuration de Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Configuration des logs
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Démarrage de l\'application')


# Décorateur pour les routes protégées
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Routes de l'application
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

            # Validation des entrées
            if not email or not password:
                raise ValueError("Email et mot de passe requis")

            if not '@' in email:
                raise ValueError("Format d'email invalide")

            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # Configuration de la session
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

            # Validations
            if not email or not password or not confirm_password:
                raise ValueError("Tous les champs sont obligatoires")

            if not '@' in email:
                raise ValueError("Format d'email invalide")

            if len(password) < 8:
                raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

            if password != confirm_password:
                raise ValueError("Les mots de passe ne correspondent pas")

            # Inscription avec Supabase
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            # Configuration de la session
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
        # Vous pouvez ajouter ici la logique pour récupérer
        # les données spécifiques à l'utilisateur
        email = session.get('email', 'Utilisateur inconnu')
        return render_template('scan.html', email=email)
    except Exception as e:
        app.logger.error(f'Erreur dans la page scan: {str(e)}')
        return redirect(url_for('login'))


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


# Gestionnaire d'erreurs personnalisé
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Erreur serveur: {error}')
    return render_template('500.html'), 500


# Point d'entrée de l'application
if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')