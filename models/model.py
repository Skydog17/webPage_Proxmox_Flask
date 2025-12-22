
from flask_login import UserMixin
from datetime import datetime
from models.connection import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('user','admin'), nullable=False)

class VMRequest(db.Model):
    __tablename__ = 'vm_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vm_type = db.Column(db.Enum('bronze','silver','gold'), nullable=False)
    status = db.Column(db.Enum('pending','approved','created','rejected'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vm_instance = db.relationship('VMInstance', backref='request', uselist=False)

class VMInstance(db.Model):
    __tablename__ = 'vm_instances'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('vm_requests.id', ondelete="CASCADE"), nullable=False)
    hostname = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    vm_user = db.Column(db.String(50))
    vm_password = db.Column(db.String(50))
    cores = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    disk = db.Column(db.Integer)