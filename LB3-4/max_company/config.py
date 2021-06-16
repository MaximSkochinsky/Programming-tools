import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = '0f0d3f0e75fce7017392388185a5f30c'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + basedir + '/data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT = '1856901165:AAFH1W3Ilzx8gPeQSqE83L7oNmJx7ABicvo'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@db:3306/app'


class TestConfig(Config):
    ENV = 'test'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True
    WTF_CSRF_ENABLED = False
