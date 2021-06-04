from app import bot, db
import datetime
from app.models import TelegramUser, User, Meetings, Client
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey



engine = create_engine("mysql+pymysql://maxim:Real280602@localhost/app")

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    if telegram_user is None:
        telegram_user = TelegramUser(id=message.from_user.id, first_name=message.from_user.first_name,
                                     username=message.from_user.username, last_name=message.from_user.last_name,
                                     chat_id=message.chat.id)
        db.session.add(telegram_user)
        db.session.commit()

    if telegram_user.user is None:
        bot.send_message(telegram_user.chat_id,
                         "Неавторизованный пользователь. Вызовите команду /auth вместе с токеном.")


@bot.message_handler(commands=['auth'])
def token_command(message):
    token = message.text.replace('/auth', '').strip()
    user = User.query.filter_by(token=token).first()
    if user:
        telegram_user = TelegramUser.query.get(message.from_user.id)
        telegram_user.user = user
        db.session.commit()
        bot.send_message(message.from_user.id, 'Здравствуйте, ' + user.username)
    else:
        bot.send_message(message.from_user.id, 'Токен не существует или устарел.')


@bot.message_handler(commands=['meetings'])
def client_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    bot.send_message(telegram_user.chat_id, "Список ваших встреч: ")
    s = select([Meetings])
    conn = engine.connect()
    result = conn.execute(s)
    min_date_obj = None
    min_row = None
    for row in result:
        client = Client.query.get(row.client_id)
        bot.send_message(telegram_user.chat_id, "Встреча с клиентом {0}, {1}\n Место: {2} \n Когда: {3}"
                         .format(client.first_name + " " + client.last_name, row.purpose, row.place, row.date))
        date_time_str = row.date
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        if min_date_obj is None or date_time_obj < min_date_obj:
            min_row = row
            min_date_obj = date_time_obj

    bot.send_message(telegram_user.chat_id, "Ближайшая встреча: ")
    meeting = Meetings.query.get(min_row.id)
    client = Client.query.get(min_row.client_id)
    bot.send_message(telegram_user.chat_id, "Встреча с клиентом {0}, {1}\n Место: {2} \n Когда: {3}"
                     .format(client.first_name + " " + client.last_name, min_row.purpose, min_row.place, min_row.date))


@bot.message_handler(commands=['clients'])
def token_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    bot.send_message(telegram_user.chat_id, "Список ваших клиентов: ")
    s = select([Client])
    conn = engine.connect()
    result = conn.execute(s)
    for row in result:
        if row.agent_id == telegram_user.user_id:
            bot.send_message(telegram_user.chat_id, "{0}. {1} {2}".format(row.id, row.first_name, row.last_name))


@bot.message_handler(content_types=['text'])
def start(message):
    bot.send_message(message.from_user.id, "Введите имя клиента: ")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, "Введите фамилию клиента: ")
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    telegram_user = TelegramUser.query.get(message.from_user.id)
    client = Client(first_name=name, last_name=surname, agent_id=telegram_user.user_id)
    db.session.add(client)
    db.session.commit()
    bot.send_message(message.from_user.id, "Клиент добавлен! ")





