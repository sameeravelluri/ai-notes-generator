from flask import Flask, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import speech_recognition as sr
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# ------------------ DATABASE ------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ ROUTES ------------------

# Landing Page
@app.route('/')
def landing():
    return render_template('landing.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists ❌"

        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')
        else:
            return "Wrong credentials ❌"

    return render_template('login.html')

# Home (Dashboard)
@app.route('/home')
@login_required
def home():
    return render_template('index.html', username=current_user.username)

# 🎤 CONTINUOUS RECORD (CHUNK + SAVE)
@app.route('/record')
@login_required
def record():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # 🎤 3 sec chunk
            audio = recognizer.listen(source, phrase_time_limit=4)

            text = recognizer.recognize_google(audio)

            # ⏱️ timestamp
            time_stamp = datetime.now().strftime("%H:%M:%S")
            final_text = f"[{time_stamp}] {text}"

            # 💾 SAVE TO FILE
            with open("notes.txt", "a", encoding="utf-8") as f:
                f.write(final_text + "\n")

            # 🧠 summary (last 10 words)
            words = text.split()
            summary = " ".join(words[-10:])

            return jsonify({
                "transcript": final_text,
                "summary": summary
            })

    except:
        return jsonify({
            "transcript": "",
            "summary": ""
        })

# 🧹 CLEAR FILE BEFORE START
@app.route('/clear_notes')
@login_required
def clear_notes():
    open("notes.txt", "w").close()
    return "cleared"

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# ------------------ RUN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
