from app import bot, db
from app.models import TelegramUser, User


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


@bot.message_handler(commands=['clients'])
def client_command(message):
    telegram_user = TelegramUser.query.get(message.from_user.id)
    bot.send_message(telegram_user.chat_id,
                     "Список ваших клиентов")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)
