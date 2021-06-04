from flask_login import UserMixin
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    telegram_users = db.relationship('TelegramUser', backref='user', lazy='dynamic')
    token = db.Column(db.String(16))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class TelegramUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(40))
    chat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    agent_id = db.Column(db.Integer)


class Meetings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, ForeignKey('user.id'))
    client_id = db.Column(db.Integer, ForeignKey('client.id'))
    date = db.Column(db.String(50))
    place = db.Column(db.String(50))
    purpose = db.Column(db.String(100))



