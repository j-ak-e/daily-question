from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, default=None)

    decks = db.relationship("UserDeck", backref="user", lazy=True)
    ratings = db.relationship("Rating", backref="user", lazy=True)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    questions = db.Column(db.Text, nullable=False)
    total_downloads = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)

    users = db.relationship("UserDeck", backref="deck", lazy=True)
    ratings = db.relationship("Rating", backref="deck", lazy=True)

class UserDeck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)