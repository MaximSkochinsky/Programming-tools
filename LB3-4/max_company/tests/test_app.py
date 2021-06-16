import json

import flask_login
import pytest
from faker import Faker
from flask import url_for, template_rendered
from flask_login import login_user
from telebot import types

import config
import telegram
from app import create_app, load_user, fixtures_load
from models import db as _db, User, TelegramUser, Client, Meeting


@pytest.fixture(scope='function')
def app():
    app = create_app(config.TestConfig)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(scope='function')
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def user(db):
    user = User()
    user.username = 'max'
    user.full_name = 'Скочинский Максим'
    user.set_password('1234')
    user.email = 'email@example.com'
    user.role = User.ROLE_MANAGER
    user.token = 'test_token'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def bot(mocker):
    send_message_stub = mocker.stub(name='bot_send_message')
    reply_to_stub = mocker.stub(name='bot_reply_to')
    telegram.bot.send_message = send_message_stub
    telegram.bot.reply_to = reply_to_stub
    return telegram.bot


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def test_create_app_production():
    app = create_app(config.ProductionConfig)
    assert app.config['ENV'] == 'production'


def test_create_app_development():
    app = create_app(config.Config)
    assert app.config['ENV'] == 'development'


def test_login_required(client):
    assert client.get('/').status_code == 302


def test_login_required_when_user_logger(app, client, captured_templates, db, user):
    @app.login_manager.request_loader
    def load_user_from_request(request):
        return User.query.first()

    login_user(user)
    client.get(url_for('index'), follow_redirects=True)
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"


def test_login_form_show(client, captured_templates, db):
    client.get(url_for('login'))
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "login.html"


def test_login_user_loader(user):
    assert load_user(user.id).id == user.id


def test_login_user_not_found(client, db):
    assert b'Invalid username or password' in client.post(url_for('login'),
                                                          data={'username': 'admin', 'password': '1234'}).data


def test_login_user_exist(client, user):
    client.post(url_for('login'),
                data={'username': user.username, 'password': '1234'})
    assert flask_login.current_user.username == user.username


def test_logout(client, db):
    assert client.get('logout').status_code == 302


def test_telegram_webhook_route(client):
    response = client.get(url_for('telegram_webhook'))
    assert response.status_code == 200 and response.json['ok'] is True


def test_telegram_any_message(client):
    response = client.post(url_for('telegram_webhook'), json={'update_id': 1},
                           headers={'Content-type': 'application/json'})
    assert response.status_code == 200 and response.json['ok'] is True


def create_text_message(text):
    params = {'text': text}
    user = types.User(id=11, is_bot=False, first_name='Максим', username='supermax', last_name='Скочинский')
    return types.Message(1, user, None, user, 'text', params, "")


@pytest.fixture(scope='function')
def telegram_user(db):
    message = create_text_message('init_message')
    telegram_user = TelegramUser(id=message.from_user.id, first_name=message.from_user.first_name,
                                 username=message.from_user.username, last_name=message.from_user.last_name,
                                 chat_id=message.chat.id)
    telegram_user.state_data = json.dumps({'client_id': None})
    db.session.add(telegram_user)
    db.session.commit()
    return telegram_user


@pytest.fixture(scope='function')
def auth_telegram_user(db, telegram_user, user):
    telegram_user.user = user
    db.session.commit()
    return telegram_user


def test_bot_start_message_without_login_at_first_message(bot, db):
    message = create_text_message('/start')
    bot.process_new_messages([message])
    bot.send_message.assert_called_once_with(message.chat.id,
                                             'Неавторизованный пользователь. Для продолжения введите токен.')


def test_bot_message_without_login_after_first_message(bot, app, telegram_user):
    message = create_text_message('/start')
    bot.process_new_messages([message])
    bot.send_message.assert_called_once_with(message.chat.id, 'Неверный токен. Для продолжения введите токен.')


def test_bot_message_send_wrong_token(bot, app, telegram_user):
    message = create_text_message('1ab2c3')
    bot.process_new_messages([message])
    bot.send_message.assert_called_once_with(message.chat.id, 'Неверный токен. Для продолжения введите токен.')


def test_bot_message_send_token(bot, app, telegram_user, user):
    message = create_text_message('test_token')
    bot.process_new_messages([message])
    assert telegram_user.user == user
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def clients(db, user, faker):
    clients = []
    for i in range(10):
        client = Client()
        client.full_name = faker.name()
        client.user = user
        client.organization_name = faker.company()
        client.address = faker.address()
        client.phone_number = faker.phone_number()
        db.session.add(client)
        clients.append(client)
    db.session.commit()
    return clients


@pytest.fixture
def meetings(db, clients, faker, user):
    meetings = []
    for client in clients:
        meeting = Meeting()
        meeting.goal = 'Договор'
        meeting.address = faker.address()
        meeting.datetime = faker.date_time()
        meeting.client = client
        meeting.user = user
        db.session.add(meeting)
        meetings.append(meeting)
    db.session.commit()
    return meetings


def test_bot_message_client_list(bot, app, auth_telegram_user, clients):
    message = create_text_message('Клиенты')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите клиента:'


def test_bot_message_back_from_client(bot, db, app, auth_telegram_user):
    auth_telegram_user.state = 'client'
    db.session.commit()
    message = create_text_message('Назад')
    bot.process_new_messages([message])
    assert auth_telegram_user.state == 'start'


@pytest.fixture
def cli_runner(app):
    yield app.test_cli_runner()


def test_cli_fixtures_load(app, db, cli_runner):
    result = cli_runner.invoke(fixtures_load)
    assert result.exit_code == 0


def test_bot_message_client_show(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state = 'client'
    client = clients[0]
    message = create_text_message(client.full_name + ' из ' + client.organization_name)
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == telegram.client_card(client)


def test_bot_message_choose_client_wrong_text(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state = 'client_show'
    message = create_text_message('wrong text message')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Пожалуйста выберите клиента кнопкой.'


def test_bot_message_meetings_list_no_meetings(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id})
    message = create_text_message('Встречи')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Не назначено ни одной встречи:'


def test_bot_message_meetings_list_with_meetings(bot, app, auth_telegram_user, clients, meetings):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id})
    message = create_text_message('Встречи')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите встречу:'


def test_bot_message_create_meeting(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id})
    message = create_text_message('Создать встречу')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите время встречи в формате dd mm YY H:i:'


def test_bot_message_create_meeting_date_step_with_correct_date(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meetings': {
        'datetime': None,
        'place': None,
        'goal': None
    }})
    auth_telegram_user.state = 'meetings_create'
    message = create_text_message('01 02 21 15:00')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите место встречи:'


def test_bot_message_create_meeting_date_step_with_non_correct_date(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meetings': {
        'datetime': None,
        'place': None,
        'goal': None
    }})
    auth_telegram_user.state = 'meetings_create'
    message = create_text_message('non correct date')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Неверный формат даты. Введите время встречи в формате dd mm YYYY H:i:'


def test_bot_message_create_meeting_place_step(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meetings': {
        'datetime': '01 02 21 15:00',
        'place': None,
        'goal': None
    }})
    auth_telegram_user.state = 'meetings_create'
    message = create_text_message('Минск')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите цель встречи:'


def test_bot_message_create_meeting_place_goal(bot, app, auth_telegram_user, clients):
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meetings': {
        'datetime': '2021-02-01 15:00',
        'place': 'Минск',
        'goal': None
    }})
    auth_telegram_user.state = 'meetings_create'
    message = create_text_message('Договор')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите встречу:'


def test_bot_message_meetings_show(bot, app, auth_telegram_user, clients, meetings):
    auth_telegram_user.state = 'meetings'
    meeting = meetings[0]
    message = create_text_message('Встреча#' + str(meeting.id))
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_meetings_edit(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Редактировать встречу')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_meetings_edit_date(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Редактировать время')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите время встречи в формате dd mm YY H:i:'


def test_bot_message_meetings_edit_place(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Редактировать место')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите место:'


def test_bot_message_meetings_edit_goal(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Редактировать цель')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Введите цель:'


def test_bot_message_meeting_show_with_meeting_id_from_state(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_show'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Wrong message')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_meeting_edit_date(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit_date'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('01 02 21 15:00')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_meeting_edit_date_incorrect(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit_date'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('01 02 21')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Неверный формат даты. Введите время встречи в формате dd mm YYYY H:i:'


def test_bot_message_meeting_edit_place(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit_place'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Минск')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_meeting_edit_goal(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit_goal'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Договор')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите команду:'


def test_bot_message_wrong_state(bot, app, auth_telegram_user, clients, meetings):
    auth_telegram_user.state = 'wrong_state'
    message = create_text_message('Some message')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Произошла ошибка. Попробуйте еще раз.'


def test_bot_message_back_from_client_show(bot, app, auth_telegram_user, clients, meetings):
    auth_telegram_user.state = 'client_show'
    message = create_text_message('Назад')
    bot.process_new_messages([message])
    assert bot.send_message.call_args.args[1] == 'Выберите клиента:'


def test_bot_message_meeting_delete(bot, app, auth_telegram_user, clients, meetings):
    meeting = meetings[0]
    auth_telegram_user.state = 'meetings_edit_place'
    auth_telegram_user.state_data = json.dumps({'client_id': clients[0].id, 'meeting_id': meeting.id})
    message = create_text_message('Удалить встречу')
    bot.process_new_messages([message])
    assert Meeting.query.get(meeting.id) is None


client_card_info = [
    (Client(organization_name='test', full_name='test', address='test', phone_number='test'),
     "Организация: test \nКлиент: test\nАдрес: <a href='test'>test</a>\nТелефон: test"),
    (Client(organization_name='Randall, Campbell and Branch', full_name='Tamara Vaughan',
            address='61235 Romero Underpass Apt. 705 Salazarport, AL 74021', phone_number='001-000-422-4851x8522'),
     "Организация: Randall, Campbell and Branch \nКлиент: Tamara Vaughan\nАдрес: <a href='61235 Romero Underpass Apt. 705 Salazarport, AL 74021'>61235 Romero Underpass Apt. 705 Salazarport, AL 74021</a>\nТелефон: 001-000-422-4851x8522"),
    (Client(organization_name='Barton-Johnson', full_name='Ricardo Hall',
            address='4471 Fischer Fork Suite 751 Josephhaven, WI 36253',
            phone_number='2435429052'),
     "Организация: Barton-Johnson \nКлиент: Ricardo Hall\nАдрес: <a href='4471 Fischer Fork Suite 751 Josephhaven, WI 36253'>4471 Fischer Fork Suite 751 Josephhaven, WI 36253</a>\nТелефон: 2435429052"),
]


@pytest.mark.parametrize("test_input,expected", client_card_info)
def test_client_card_info(app, test_input, expected):
    assert telegram.client_card(test_input) == expected
