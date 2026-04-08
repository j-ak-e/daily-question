from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import json
import os

from models import db, User, Deck, UserDeck, Rating

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-to-something-random"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dailyquestion.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_todays_question(questions):
    index = date.today().toordinal() % len(questions)
    return questions[index]

def detect_and_convert(lines, deck_name):
    questions = []
    subject = deck_name.replace("-", " ").title()

    for line in lines:
        line = line.strip().replace("\u00ad", "")
        if line.startswith("#") or not line:
            continue
        parts = line.split("\t")

        if len(parts) == 2:
            term, definition = parts
            questions.append({
                "subject": subject,
                "text": f"Define: {term}",
                "answer": definition
            })
        elif len(parts) >= 5 and not parts[0].strip().isdigit():
            verb, conjugation, tense, _, context = parts[:5]
            questions.append({
                "subject": subject,
                "text": f"What is the {tense} tense conjugation of '{verb}'? ({context.strip()})",
                "answer": conjugation
            })
        elif len(parts) >= 3 and parts[0].strip().isdigit():
            number, symbol, name = parts[:3]
            category = parts[6].strip() if len(parts) > 6 else ""
            questions.append({
                "subject": subject,
                "text": f"What is the symbol for {name}?",
                "answer": symbol
            })
            questions.append({
                "subject": subject,
                "text": f"What element has atomic number {number}?",
                "answer": name
            })
            if category:
                questions.append({
                    "subject": subject,
                    "text": f"What category is {name}?",
                    "answer": category
                })
        elif len(parts) >= 3 and not parts[0].strip().isdigit():
            term, definition = parts[0], parts[1]
            questions.append({
                "subject": subject,
                "text": f"Define: {term}",
                "answer": definition
            })

    return questions

@app.route("/")
def home():
    if current_user.is_authenticated:
        user_deck_ids = [ud.deck_id for ud in current_user.decks]
        decks = Deck.query.filter(Deck.id.in_(user_deck_ids)).all()
    else:
        decks = Deck.query.filter_by(is_public=True).limit(1).all()
    return render_template("home.html", decks=decks)

@app.route("/deck/<int:deck_id>")
def question_page(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if not current_user.is_authenticated:
        if not deck.is_public:
            return redirect(url_for("login"))
    questions = json.loads(deck.questions)
    question = get_todays_question(questions)
    return render_template("index.html", question=question, deck=deck)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already taken.")
        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered.")

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("home"))

    return render_template("signup.html", error=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return render_template("login.html", error="Invalid username or password.")

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html", error=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/import", methods=["GET", "POST"])
@login_required
def import_deck():
    if request.method == "POST":
        file = request.files.get("deck_file")
        deck_name = request.form.get("deck_name", "").strip()
        is_public = request.form.get("is_public") == "on"

        if not file or not deck_name:
            return render_template("import.html", error="Please provide both a file and a deck name.")

        lines = file.read().decode("utf-8").splitlines()
        questions = detect_and_convert(lines, deck_name)

        if not questions:
            return render_template("import.html", error="No questions could be parsed. Check your file format.")

        deck = Deck(
            name=deck_name,
            owner_id=current_user.id,
            is_public=is_public,
            questions=json.dumps(questions),
            total_downloads=0
        )
        db.session.add(deck)
        db.session.commit()

        user_deck = UserDeck(user_id=current_user.id, deck_id=deck.id)
        db.session.add(user_deck)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("import.html", error=None)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)