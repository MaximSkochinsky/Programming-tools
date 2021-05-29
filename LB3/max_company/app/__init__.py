import telebot
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object(Config)
toolbar = DebugToolbarExtension(app)
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
bot = telebot.TeleBot(app.config.get('TELEGRAM_BOT'), threaded=False)

from app import routes, logger, models, commands, telegram
