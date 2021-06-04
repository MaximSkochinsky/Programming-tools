import click
import secrets
from flask.cli import AppGroup

from app import app, db, bot
from app.models import User

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
        user.token = secrets.token_hex(10)
        print("Your token is: " + user.token)
        user.username = username
        user.set_password(password)
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
