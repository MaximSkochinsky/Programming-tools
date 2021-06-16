import json
import re
from datetime import datetime

import telebot
from telebot import types

from models import TelegramUser, db, User, Client, Meeting

bot = telebot.TeleBot(token='', threaded=False)


def get_telegram_user(message):
    return TelegramUser.query.get(message.from_user.id)


def create_telegram_user(message):
    telegram_user = TelegramUser(id=message.from_user.id, first_name=message.from_user.first_name,
                                 username=message.from_user.username, last_name=message.from_user.last_name,
                                 chat_id=message.chat.id, state='new')
    telegram_user.state_data = json.dumps({})
    db.session.add(telegram_user)
    db.session.commit()
    return telegram_user


def client_card(client):
    return "Организация: {0} \nКлиент: {1}\nАдрес: <a href='{2}'>{2}</a>\nТелефон: {3}".format(
        client.organization_name, client.full_name, client.address, client.phone_number)


def show_menu(message, telegram_user):
    user = telegram_user.user

    if telegram_user.state == 'start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Клиенты'))
        bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)
        return True
    if telegram_user.state == 'client':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.InlineKeyboardButton('Назад'))
        for client in user.clients:
            markup.add(types.InlineKeyboardButton(client.full_name + ' из ' + client.organization_name))
        bot.send_message(message.chat.id, "Выберите клиента:", reply_markup=markup)
        return True
    if telegram_user.state == 'client_show':
        client_name = message.text.split(' из ')
        if len(client_name) == 2:
            client = Client.query.filter_by(full_name=client_name[0], organization_name=client_name[1]).first()
            if client:
                telegram_user.state_data = json.dumps({'client_id': client.id})
                db.session.commit()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.InlineKeyboardButton('Назад'))
                markup.add(types.InlineKeyboardButton('Встречи'))
                bot.send_message(message.chat.id, client_card(client),
                                 parse_mode='HTML', reply_markup=markup)
                return True
        bot.send_message(message.chat.id, 'Пожалуйста выберите клиента кнопкой.')
        return True

    state_data = json.loads(telegram_user.state_data)

    if telegram_user.state == 'meetings':
        client = Client.query.get(state_data['client_id'])
        if client:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('Назад'))
            markup.add(types.InlineKeyboardButton('Создать встречу'))
            meetings = Meeting.query.filter_by(user=user, client=client).all()
            if len(meetings) == 0:
                bot.send_message(message.chat.id, 'Не назначено ни одной встречи:', reply_markup=markup)
                return True
            for meeting in meetings:
                markup.add(types.InlineKeyboardButton(
                    'Встреча#{0}\nВремя: {1} \nМесто: {2} \nЦель: {3}'.format(
                        meeting.id,
                        meeting.datetime,
                        meeting.address,
                        meeting.goal)))
            bot.send_message(message.chat.id, 'Выберите встречу:', reply_markup=markup)
            return True
    if telegram_user.state == 'meetings_create':
        client = Client.query.get(state_data['client_id'])
        if state_data['meetings']['datetime'] is None:
            if message.text == 'Создать встречу':
                bot.send_message(message.chat.id, 'Введите время встречи в формате dd mm YY H:i:')
            else:
                try:
                    date_time_obj = datetime.strptime(message.text, '%d %m %y %H:%M')
                    state_data['meetings']['datetime'] = date_time_obj.strftime("%Y-%m-%d %H:%M")
                    telegram_user.state_data = json.dumps(state_data)
                    bot.send_message(message.chat.id, 'Введите место встречи:')
                except ValueError:
                    bot.send_message(message.chat.id,
                                     'Неверный формат даты. Введите время встречи в формате dd mm YYYY H:i:')
            return True
        if state_data['meetings']['place'] is None:
            state_data['meetings']['place'] = message.text
            telegram_user.state_data = json.dumps(state_data)
            bot.send_message(message.chat.id, 'Введите цель встречи:')
            return True
        if state_data['meetings']['goal'] is None:
            state_data['meetings']['goal'] = message.text
            telegram_user.state = 'meetings'
            telegram_user.state_data = json.dumps(state_data)
            meeting = Meeting()
            meeting.user = user
            meeting.client = client
            meeting.datetime = datetime.strptime(state_data['meetings']['datetime'], '%Y-%m-%d %H:%M')
            meeting.address = state_data['meetings']['place']
            meeting.goal = state_data['meetings']['goal']
            state_data['meetings'] = {}
            state_data['meetings']['datetime'] = None
            state_data['meetings']['place'] = None
            state_data['meetings']['goal'] = None
            telegram_user.state_data = json.dumps(state_data)
            db.session.add(meeting)
            db.session.commit()
            bot.send_message(message.chat.id, 'Встреча создана.')
            show_menu(message, telegram_user)
            return True
    if telegram_user.state == 'meetings_show':
        result = re.match(r'Встреча#(.+)', message.text)
        if result:
            meeting = Meeting.query.get(result.group(1))
        else:
            meeting = Meeting.query.get(state_data['meeting_id'])
        if meeting:
            state_data['meeting_id'] = meeting.id
            telegram_user.state_data = json.dumps(state_data)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('Назад'))
            markup.add(types.InlineKeyboardButton('Редактировать встречу'))
            markup.add(types.InlineKeyboardButton('Удалить встречу'))
            bot.send_message(message.chat.id, 'Встреча#{0}\nВремя: {1} \nМесто: {2} \nЦель: {3}'.format(
                meeting.id,
                meeting.datetime,
                meeting.address,
                meeting.goal))
            bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)
            return True
    if telegram_user.state == 'meetings_edit':
        meeting = Meeting.query.get(state_data['meeting_id'])
        if meeting:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton('Назад'))
            if message.text == 'Редактировать время':
                telegram_user.state = 'meetings_edit_date'
                bot.send_message(message.chat.id, 'Введите время встречи в формате dd mm YY H:i:', reply_markup=markup)
                return True
            if message.text == 'Редактировать место':
                telegram_user.state = 'meetings_edit_place'
                bot.send_message(message.chat.id, 'Введите место:', reply_markup=markup)
                return True
            if message.text == 'Редактировать цель':
                telegram_user.state = 'meetings_edit_goal'
                bot.send_message(message.chat.id, 'Введите цель:', reply_markup=markup)
                return True
            markup.add(types.InlineKeyboardButton('Редактировать время'))
            markup.add(types.InlineKeyboardButton('Редактировать место'))
            markup.add(types.InlineKeyboardButton('Редактировать цель'))
            bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)
            return True
    if telegram_user.state == 'meetings_edit_date':
        try:
            date_time_obj = datetime.strptime(message.text, '%d %m %y %H:%M')
            meeting = Meeting.query.get(state_data['meeting_id'])
            meeting.datetime = date_time_obj
            telegram_user.state = 'meetings_edit'
            bot.send_message(message.chat.id, 'Время обновлено')
        except ValueError:
            bot.send_message(message.chat.id,
                             'Неверный формат даты. Введите время встречи в формате dd mm YYYY H:i:')
            return True
        return show_menu(message, telegram_user)
    if telegram_user.state == 'meetings_edit_place':
        meeting = Meeting.query.get(state_data['meeting_id'])
        meeting.place = message.text
        telegram_user.state = 'meetings_edit'
        bot.send_message(message.chat.id, 'Место обновлено')
        return show_menu(message, telegram_user)
    if telegram_user.state == 'meetings_edit_goal':
        meeting = Meeting.query.get(state_data['meeting_id'])
        meeting.place = message.text
        telegram_user.state = 'meetings_edit'
        bot.send_message(message.chat.id, 'Цель обновлена')
        return show_menu(message, telegram_user)

    return False


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    telegram_user = get_telegram_user(message)

    if telegram_user is None:
        create_telegram_user(message)
        bot.send_message(message.chat.id, 'Неавторизованный пользователь. Для продолжения введите токен.')
        return

    if telegram_user.user is None:
        token = message.text.strip()
        user = User.query.filter_by(token=token).first()
        if user:
            telegram_user.user = user
            user.generate_token()
            telegram_user.state = 'start'
        else:
            bot.send_message(message.chat.id, 'Неверный токен. Для продолжения введите токен.')
            return
    state_data = json.loads(telegram_user.state_data)

    if message.text == 'Клиенты':
        telegram_user.state = 'client'

    if message.text == 'Назад':
        if telegram_user.state == 'client':
            telegram_user.state = 'start'
        if telegram_user.state == 'client_show':
            telegram_user.state = 'client'
        if telegram_user.state == 'meetings_create' or telegram_user.state == 'meetings':
            client = Client.query.get(state_data['client_id'])
            message.text = client.full_name + ' из ' + client.organization_name
            telegram_user.state = 'client_show'
        if telegram_user.state == 'meetings_show':
            telegram_user.state = 'meetings'
        if telegram_user.state == 'meetings_edit':
            telegram_user.state = 'meetings_show'
        if telegram_user.state == 'meetings_edit_date':
            telegram_user.state = 'meetings_edit'

    if ' из ' in message.text and telegram_user.state == 'client':
        telegram_user.state = 'client_show'

    if message.text == 'Встречи' and state_data['client_id']:
        telegram_user.state = 'meetings'

    if message.text == 'Создать встречу':
        state_data['meetings'] = {}
        state_data['meetings']['datetime'] = None
        state_data['meetings']['place'] = None
        state_data['meetings']['goal'] = None
        telegram_user.state_data = json.dumps(state_data)
        telegram_user.state = 'meetings_create'

    if telegram_user.state == 'meetings' and 'Встреча#' in message.text:
        telegram_user.state = 'meetings_show'

    if message.text == 'Удалить встречу':
        meeting = Meeting.query.get(state_data['meeting_id'])
        if meeting:
            telegram_user.state = 'meetings'
            state_data['meeting_id'] = None
            telegram_user.state_data = json.dumps(state_data)
            db.session.delete(meeting)
            db.session.commit()

    if message.text == 'Редактировать встречу':
        telegram_user.state = 'meetings_edit'
    db.session.commit()
    if not show_menu(message, telegram_user):
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        show_menu(message, telegram_user)

    db.session.commit()


def init_app(app):
    bot.token = app.config.get('TELEGRAM_BOT')
