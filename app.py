import telebot
from datetime import datetime

from extensions import ExchangeRatesAPI, APIException
from config import token, keys


bot = telebot.TeleBot(token)


@bot.message_handler(commands=('start', 'help'))
def greet(message: telebot.types.Message):
    text = 'Увидеть список доступных валют: /values.\nДля \
конвертации введите: <название конвертируемой валюты> \
<название валюты в которой хотите получить результат> \
<сумму конвертации>.\nУказывайте название валюты в единственном числе!!!'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=('values', ))
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'

    for key in keys.keys():
        text = '\n'.join((text, key))

    bot.reply_to(message, text)


@bot.message_handler(content_types=['audio', 'video'])
def success(message: telebot.types.Message):
    bot.reply_to(message, 'Well done!')


@bot.message_handler(content_types='text')
def convert(message: telebot.types.Message):
    try:
        base, quote, amount = message.text.split(' ')
        base = base.lower()
        quote = quote.lower()

        result = ExchangeRatesAPI.get_price(base, quote, float(amount))
        
        text = f'Цена {amount} {base} в {quote} составляет {result}'
        bot.send_message(message.chat.id, text)
    except APIException as e:
        bot.send_message(message.chat.id, 'Ошибка пользователя')
        bot.reply_to(message, e)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
        bot.reply_to(message, e)


bot.polling(none_stop=True)