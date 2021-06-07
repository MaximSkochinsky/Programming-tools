import random
import string

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    ROLE_MANAGER = 'manager'
    ROLE_ADMINISTRATOR = 'administrator'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True)
    full_name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    email = db.Column(db.String(255), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    telegram_users = db.relationship('TelegramUser', backref='user', lazy='dynamic')
    token = db.Column(db.String(255))
    meetings = db.relationship('Meeting', backref='user', lazy='dynamic')
    clients = db.relationship('Client', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        self.token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class TelegramUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    username = db.Column(db.String(255))
    chat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    state = db.Column(db.String(255))
    state_data = db.Column(db.TEXT)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    organization_name = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    meetings = db.relationship('Meeting', backref='client', lazy='dynamic')
    user_id = db.Column(db.Integer, ForeignKey('user.id'))


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DATETIME)
    address = db.Column(db.String(255))
    goal = db.Column(db.String(255))
    result = db.Column(db.String(255))
    client_id = db.Column(db.Integer, ForeignKey('client.id'))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
