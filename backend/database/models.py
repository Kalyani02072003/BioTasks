from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    """ User table to store registered users """
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Store hashed passwords
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    """ Table to store tasks and their outputs """
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    output_blob_url = db.Column(db.String(500), nullable=True)  # Azure Blob Storage URL
