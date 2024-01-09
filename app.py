import telebot
from datetime import datetime
from extensions import APIException, ExchangeService, HTTPClient, logger
from config import token, keys
from constants import (
    AMOUNT_TYPE_ERROR_TEXT,
    GREETING_TEXT,
    OFFER_TEXT,
    VALUES_TEXT,
    WELL_DONE_TEXT,
)


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def greet(message: telebot.types.Message):
    text = GREETING_TEXT
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = VALUES_TEXT

    for key in keys.keys():
        text = '\n'.join((text, key))

    bot.reply_to(message, text)


@bot.message_handler(content_types=['audio', 'video'])
def success(message: telebot.types.Message):
    bot.reply_to(message, WELL_DONE_TEXT)


@bot.message_handler(content_types='text')
def convert(message: telebot.types.Message):
    http_client = HTTPClient()
    exchange_service = ExchangeService(http_client)

    try:
        base, quote, amount = message.text.split(' ')
        base = base.lower()
        quote = quote.lower()
        result = exchange_service.get_price(base, quote, float(amount))
    except APIException as e:
        logger.error(
            f"ERROR - {datetime.now().strftime('%H:%M:%s')} - %s\n", e.message
        )
        bot.send_message(message.chat.id, e.message)
        bot.reply_to(message, e)
    except ValueError as e:
        logger.error(
            f"ERROR - {datetime.now().strftime('%H:%M:%s')} - %s\n", e
        )
        bot.send_message(message.chat.id, AMOUNT_TYPE_ERROR_TEXT)
    else:
        text = OFFER_TEXT.format(
            amount=amount,
            base=base,
            quote=quote,
            result=result,
        )
        bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
