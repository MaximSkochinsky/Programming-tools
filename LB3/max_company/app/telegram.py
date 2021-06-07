import datetime

from sqlalchemy.orm.attributes import flag_modified
from telebot import types

from app import bot, db
from app.models import TelegramUser, User, Client, Meeting
from app.telegramcalendar import create_calendar

current_shown_dates = {}


@bot.middleware_handler(update_types=['message'])
def check_logged_middleware(bot_instance, message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    if '/auth' not in message.text and (telegram_user is None or telegram_user.user is None):
        message.text = '/no_logged'


@bot.message_handler(commands=['no_logged'])
def no_logged_command(message):
    bot.send_message(message.chat.id,
                     "Неавторизованный пользователь. Вызовите команду /auth вместе с токеном.")


@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)

    if telegram_user is None or telegram_user.user is None:
        bot.send_message(message.chat.chat,
                         "Неавторизованный пользователь. Вызовите команду /auth вместе с токеном.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Клиенты')
    itembtn2 = types.KeyboardButton('Встречи')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.from_user.id, 'Выберите команду:', reply_markup=markup)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Клиенты")
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Назад к списку клиентов")
def client_list_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)

    if telegram_user is not None and telegram_user.user is not None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.InlineKeyboardButton('Назад'))
        for client in telegram_user.user.clients:
            markup.add(types.InlineKeyboardButton(client.full_name + ' из ' + client.organization_name))
        bot.send_message(message.chat.id, "Выберите клиента:", reply_markup=markup)
        bot.register_next_step_handler(message, client_info)
        return
    bot.send_message(message.chat.id, 'Непредвиденная ошибка. Попробуйте позже.')


def client_info(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)

    if telegram_user is not None and telegram_user.user is not None:
        client_name = message.text.split(' из ')
        client = Client.query.filter_by(full_name=client_name[0], organization_name=client_name[1]).first()
        if client:
            telegram_user.state = 'client_show'
            telegram_user.state_data = {'client_id': client.id}
            db.session.commit()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('Назад к списку клиентов'))
            markup.add(types.InlineKeyboardButton('Встречи'))

            bot.send_message(message.chat.id,
                             "Организация: {0} \nКонтактное лицо: {1}\nАдрес: <a href='{2}'>{2}</a>\nТелефон: {3}".format(
                                 client.organization_name, client.full_name, client.address, client.phone_number),
                             parse_mode='HTML', reply_markup=markup)
            return
    bot.send_message(message.chat.id, 'Непредвиденная ошибка. Попробуйте позже.')
    pass


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Назад")
def back_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Клиенты')
    itembtn2 = types.KeyboardButton('Встречи')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.from_user.id, 'Выберите команду:', reply_markup=markup)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Встречи")
def client_meeting_show(message):
    telegram_user = TelegramUser.query.get(message.chat.id)
    if telegram_user is not None or telegram_user.user is not None:
        if telegram_user.state == 'client_show':
            telegram_user.state = 'client_meeting_show'
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('Назад к клиенту'))
            markup.add(types.InlineKeyboardButton('Создать встречу'))
            db.session.commit()
            client = Client.query.get(telegram_user.state_data.get('client_id'))
            meetings = Meeting.query.filter_by(client=client, user=telegram_user.user).all()
            if len(meetings) == 0:
                bot.send_message(message.chat.id,
                                 'Не назначено ни одной встречи с клиентом {0}'.format(client.full_name),
                                 reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'no user')


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Создать встречу")
def client_meeting_create(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)

    if telegram_user is not None or telegram_user.user is not None:
        client = Client.query.get(telegram_user.state_data.get('client_id'))
        telegram_user = TelegramUser.query.get(message.from_user.id)
        if telegram_user is not None:
            now = datetime.datetime.now()
            chat_id = message.chat.id
            date = (now.year, now.month)
            telegram_user.state = 'calendar'
            telegram_user.state_data['calendar'] = {}
            telegram_user.state_data['meeting'] = {}
            telegram_user.state_data['calendar'][str(chat_id)] = date
            flag_modified(telegram_user, 'state_data')
            db.session.commit()
            markup = create_calendar(now.year, now.month)
            bot.send_message(message.chat.id, "Выберите дату встречи", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'DAY' in call.data)
def handle_day_query(call):
    chat_id = call.message.chat.id
    telegram_user = TelegramUser.query.get(chat_id)
    if telegram_user is not None:
        saved_date = telegram_user.state_data['calendar'][str(chat_id)]
        last_sep = call.data.rfind(';') + 1
        if saved_date is not None:
            day = call.data[last_sep:]
            date = datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0)
            telegram_user.state_data['meeting']['date'] = date
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('По адресу клиента'))
            bot.send_message(chat_id=chat_id, text='Укажите место встречи', reply_markup=markup)
            bot.register_next_step_handler(call.message, handle_meeting_place)
        else:
            bot.send_message(chat_id=chat_id, text='no saved data')
            pass
    else:
        bot.send_message(chat_id=chat_id, text='no user')


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "По адресу клиента")
def handle_meeting_place(message):
    telegram_user = TelegramUser.query.get(message.chat.id)
    if telegram_user is not None:
        if message.text == 'По адресу клиента':
            client = Client.query.get(telegram_user.state_data.get('client_id'))
            telegram_user.state_data['meeting']['place'] = client.address
        else:
            telegram_user.state_data['meeting']['place'] = message.text
        flag_modified(telegram_user, 'state_data')
        db.session.commit()

        bot.send_message(message.chat.id, 'Укажите цель встречи', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_meeting_goal)


def handle_meeting_goal(message):
    telegram_user = TelegramUser.query.get(message.chat.id)
    if telegram_user is not None:
        client = Client.query.get(telegram_user.state_data.get('client_id'))
        meeting = Meeting()
        meeting.address = telegram_user.state_data['meeting']['place']
        meeting.goal = message.text
        meeting.user = telegram_user.user
        meeting.client = client
        db.session.add(meeting)
        telegram_user.state = 'client_show'
        db.session.commit()
        client_meeting_show(message)
    else:
        bot.send_message(message.chat.id, 'no user')


@bot.callback_query_handler(func=lambda call: 'MONTH' in call.data)
def handle_month_query(call):
    info = call.data.split(';')
    month_opt = info[0].split('-')[0]
    year, month = int(info[1]), int(info[2])
    chat_id = call.message.chat.id

    if month_opt == 'PREV':
        month -= 1

    elif month_opt == 'NEXT':
        month += 1

    if month < 1:
        month = 12
        year -= 1

    if month > 12:
        month = 1
        year += 1

    date = (year, month)

    telegram_user = TelegramUser.query.get(chat_id)
    if telegram_user is not None:
        telegram_user.state_data['calendar'][str(chat_id)] = date
        flag_modified(telegram_user, 'state_data')
        db.session.commit()
        markup = create_calendar(year, month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.from_user.id, "no telegram user")


@bot.callback_query_handler(func=lambda call: "IGNORE" in call.data)
def ignore(call):
    bot.answer_callback_query(call.id, text="OOPS... something went wrong")


@bot.message_handler(commands=['auth'])
def token_command(message):
    token = message.text.replace('/auth', '').strip()
    user = User.query.filter_by(token=token).first()
    if user:
        telegram_user = TelegramUser.query.get(message.from_user.id)
        if telegram_user is None:
            telegram_user = TelegramUser(id=message.from_user.id, first_name=message.from_user.first_name,
                                         username=message.from_user.username, last_name=message.from_user.last_name,
                                         chat_id=message.chat.id)
            db.session.add(telegram_user)
            db.session.commit()

        telegram_user.user = user
        user.generate_token()
        db.session.commit()
        bot.send_message(message.from_user.id, 'Здравствуйте, ' + user.username)
    else:
        bot.send_message(message.from_user.id, 'Токен не существует или устарел.')


@bot.message_handler(commands=['clients'])
def client_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    bot.send_message(telegram_user.chat_id,
                     "Список ваших клиентов")


@bot.message_handler(commands=['addclient'])
def add_client(message):
    bot.send_message(message.from_user.id, "Введите имя клиента: ")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    bot.send_message(message.from_user.id, "Введите фамилию клиента: ")
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    surname = message.text
    client = Client(first_name=name, last_name=surname, agent_id=telegram_user.user_id)
    db.session.add(client)
    db.session.commit()
    bot.send_message(message.from_user.id, "Клиент добавлен!")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)
