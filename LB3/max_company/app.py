from datetime import timedelta, datetime

import click
import telebot
from faker import Faker
from flask import Flask, render_template, redirect, url_for, request
from flask.cli import AppGroup
from flask_login import LoginManager, login_required, login_user, logout_user

import config
import logger
import telegram
from forms import LoginForm
from models import db, User, Client, Meeting

login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    @app.route('/')
    @login_required
    def index():
        users = User.query.all()
        return render_template('index.html', users=users)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                return render_template('login.html', form=form, error='Invalid username or password')
            login_user(user, remember=form.remember_me.data)
            app.logger.info('User ' + user.username + ' logged.')
            return redirect(url_for('index'))

        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/telegram', methods=["GET", "POST"])
    def telegram_webhook():
        if request.method == 'POST' and request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            telegram.bot.process_new_updates([update])
        return {"ok": True}

    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    db.create_all()
    login_manager.init_app(app)
    logger.init_app(app)
    telegram.init_app(app)

    return app


app = create_app(config.ProductionConfig)

telegram_cli = AppGroup('telegram', short_help='Control telegram bot')


@telegram_cli.command('webhook')
@click.argument('webhook')
def set_webhook(webhook):
    """ Set url webhook for telegram bot """
    telegram.bot.set_webhook(webhook)


@telegram_cli.command('notify')
def notify():
    d = datetime.today() - timedelta(hours=1)
    clients = Client.query.all()
    for client in clients:
        if client.user and client.user.telegram_user:
            for meeting in client.meetings:
                if not meeting.notified:
                    time_delta = (meeting.datetime - d)
                    total_seconds = time_delta.total_seconds()
                    minutes = round(total_seconds / 60)
                    if minutes <= 60:
                        telegram.bot.send_message(client.user.telegram_user.id,
                                                  'У вас запланирована встреча с ' + client.full_name + ' в ' + meeting.address + ' через ' + str(
                                                      minutes) + ' минут')
                        meeting.notified = True
                        db.session.commit()


app.cli.add_command(telegram_cli)

fake = Faker()

fixtures_cli = AppGroup('fixtures')


@fixtures_cli.command('load')
def fixtures_load():
    User.query.delete()

    users = [
        {
            'full_name': 'Максим Скочинский',
            'email': 'example@gmail.com',
            'role': User.ROLE_MANAGER,
            'username': 'max_manager',
            'password': 'manager'
        },
        {
            'full_name': 'Максим Скочинский',
            'email': 'admin_example@gmail.com',
            'role': User.ROLE_ADMINISTRATOR,
            'username': 'max_admin',
            'password': 'admin'
        },

    ]

    for user in users:
        manager = User()
        manager.full_name = user.get('full_name')
        manager.email = user.get('email')
        manager.role = user.get('role')
        manager.username = user.get('username')
        manager.set_password(user.get('password'))
        manager.generate_token()
        db.session.add(manager)

        for i in range(10):
            client = Client()
            client.full_name = fake.name()
            client.user = manager
            client.organization_name = fake.company()
            client.address = fake.address()
            client.phone_number = fake.phone_number()
            db.session.add(client)

            meeting = Meeting()
            meeting.user = manager
            meeting.client = client
            meeting.datetime = datetime.today() - timedelta(minutes=30)
            meeting.goal = 'Договор'
            meeting.address = client.address
            db.session.add(meeting)

    db.session.commit()
    pass


app.cli.add_command(fixtures_cli)
