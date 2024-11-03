from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Changez ceci avec une clé secrète sécurisée

# Informations de connexion
server = 'localhost'
database = 'netflix'

def get_db_connection():
    return pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO dbo.utilisateurs (email, password) VALUES (?, ?)", 
                               (email, generate_password_hash(password)))
                conn.commit()
            return render_template('index.html', success="Inscription réussie !")
        except Exception as e:
            return render_template('index.html', error=f"Erreur lors de l'inscription : {str(e)}")

    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return index()  # Redirige vers la fonction index pour gérer l'inscription

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM dbo.utilisateurs WHERE email = ?", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user[0], password):
                    session['user'] = email
                    return redirect("https://universalblog7.webnode.page/")  # Redirection vers l'URL externe
                
                return render_template('sign_in.html', error="Identifiants invalides !")
        except Exception as e:
            return render_template('sign_in.html', error=f"Erreur lors de la connexion : {str(e)}")

    return render_template('sign_in.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('signin'))  # Redirige vers la page de connexion si non authentifié
    return render_template('home.html', user=session['user'])

@app.route('/signout')
def signout():
    session.pop('user', None)  # Supprime l'utilisateur de la session
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)