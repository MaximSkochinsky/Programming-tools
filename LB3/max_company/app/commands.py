import click
from faker import Faker
from flask.cli import AppGroup

from app import app, db, bot
from app.models import User, Client

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
            'username': 'max',
            'password': 'admin'
        }
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

    db.session.commit()
    pass


app.cli.add_command(fixtures_cli)

users_cli = AppGroup('user', short_help='Control app users')


@users_cli.command('create')
def create_user():
    """ Create database user """
    username = click.prompt('Username?')
    user = User.query.filter_by(username=username).first()
    if user:
        if click.confirm('User "{}" already exist, new password?'.format(username)):
            password = click.prompt('New password?', hide_input=True)
            user.set_password(password)
            db.session.commit()
    else:
        password = click.prompt('Password?', hide_input=True)
        user = User()
        user.username = username
        user.set_password(password)
        user.generate_token()
        db.session.add(user)
        db.session.commit()


@users_cli.command('check-password')
@click.argument('username')
def check_password(username):
    """ Check input password equal for user """
    user = User.query.filter_by(username=username).first()
    if user:
        password = click.prompt('Password?', hide_input=True)
        if user.check_password(password):
            click.echo('Password equal.')
        else:
            click.echo('Wrong password.')
    else:
        click.echo('User "{}" not found.'.format(username))


app.cli.add_command(users_cli)

telegram_cli = AppGroup('telegram', short_help='Control telegram bot')


@telegram_cli.command('webhook')
@click.argument('webhook')
def set_webhook(webhook):
    """ Set url webhook for telegram bot """
    bot.set_webhook(webhook)


app.cli.add_command(telegram_cli)
