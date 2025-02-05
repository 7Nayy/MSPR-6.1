from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
# Assurez-vous que Flask trouve bien le dossier templates
app = Flask(__name__,
            template_folder='../templates',  # Chemin relatif vers le dossier templates
            static_folder='../static'  # Chemin relatif vers les fichiers statiques
            )
app.secret_key = 'votre_cle_secrete'

# Configuration Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session['user_id'] = response.user.id
            return redirect(url_for('scan'))

        except Exception as e:
            return render_template('connexion.html', error=str(e))

    return render_template('connexion.html')


@app.route('/scan')
def scan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('scan.html')


if __name__ == '__main__':
    app.run(debug=True)