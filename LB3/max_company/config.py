import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = '0f0d3f0e75fce7017392388185a5f30c'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'var/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT = '1856901165:AAFH1W3Ilzx8gPeQSqE83L7oNmJx7ABicvo'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://b0ae353a0b7f70:a46ebb33@us-cdbr-east-03.cleardb.com' \
                              '/heroku_e307ee4b839f0b0'
