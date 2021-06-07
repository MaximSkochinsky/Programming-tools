import telebot
from flask import render_template, redirect, url_for, request
from flask_login import logout_user, login_user, login_required

from app import app, bot
from app.forms import LoginForm
from app.models import User


@app.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/telegram', methods=["GET", "POST"])
def telegram():
    if request.method == 'POST' and request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    return {"ok": True}


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
