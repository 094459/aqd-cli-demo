from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    last_login = db.Column(db.TIMESTAMP)
    
    # Relationships
    surveys = db.relationship('Survey', backref='creator', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
