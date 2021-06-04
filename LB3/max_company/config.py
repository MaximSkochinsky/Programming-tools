import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = '0f0d3f0e75fce7017392388185a5f30c'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://maxim:Real280602@localhost/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT = '1752651930:AAGKWH_sH2I3HxYdjC2guR3dyBGub6NPU8U'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://b0ae353a0b7f70:a46ebb33@us-cdbr-east-03.cleardb.com' \
                              '/heroku_e307ee4b839f0b0'
