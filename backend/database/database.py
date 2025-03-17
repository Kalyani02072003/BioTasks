from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.models import db

def init_db(app):
    """ Initialize the database """
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost:5432/biotasks"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
