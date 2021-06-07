import logging
import os
from logging.handlers import RotatingFileHandler

import telebot

from app import app, bot

if not os.path.exists('var/log'):
    os.makedirs('var/log')

file_handler = RotatingFileHandler('var/log/' + app.env + '.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

if app.debug:
    app.logger.setLevel(logging.DEBUG)
    telebot.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.ERROR)
    telebot.logger.setLevel(logging.ERROR)
