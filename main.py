import telebot
from telebot import types
import re
import requests
import datetime
import json


with open('secrets.json', encoding='utf-8') as f:
    token = json.load(f)['BOT_API_KEY']


bot=telebot.TeleBot(token)


def log(message):
    print('\n', datetime.datetime.now())
    print("Message from {0} {1} (id = {2}) \n {3}".format(message.from_user.first_name, message.from_user.last_name, str(message.from_user.id), message.text))


@bot.message_handler(commands=['start'])
def start_message(message):
    s = """
    Hi! This is CurrencyExchange bot. I can help you compute currency convertation
    If you want to know, how much one currency equals to another, send me following message: "<how much> <from currency> to <currency>"
    For example: "100 USD to RUB"

    List of all available commands: /help
    """
    bot.send_message(message.chat.id, s)
    log(message)


@bot.message_handler(commands=['help'])
def start_message(message):
    s = """
    List of commands:
    /start - welcome message
    /convert <X> <currency1> to <currency2> - calculate how much X currency1 equals to currency2
    """
    bot.send_message(message.chat.id, s)
    log(message)
    

def compute(val, fromC, toC):
    """
    Function to compute currencies values

    :param val: amount of first currency
    :param fromC: currency to convert
    :param toC: target currency
    :returns: how much val of first currency equals to second, otherwise None
    """
    url = 'https://cdn.moneyconvert.net/api/latest.json'
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()['rates']
    
    try:
        result = float(val) * float(data[toC]) / float(data[fromC])
    except Exception as e:
        result = None
    return result


@bot.message_handler(commands=['convert'])
def convert(message):
    if re.fullmatch('^\/convert\s(\d+(\.\d+)?)\s([A-Za-z]+)\sto\s([A-Za-z]+)$', message.text):
        _, val, fromC, _, toC = message.text.split(' ')

        result = compute(val, fromC, toC)
        reply = f'{val} {fromC} = {result:.2f} {toC}' if result is not None else 'Incorrect currencies, try another request'
    else:
        reply = 'Type which currencies do you want to convert, like: "100 USD to RUB"'
    bot.send_message(message.chat.id, reply)
    log(message)


@bot.message_handler(content_types='text')
def message_reply(message):
    words = message.text.lower().split()
    if re.fullmatch('^(\d+(\.\d+)?)\s([A-Za-z]+)\sto\s([A-Za-z]+)$', message.text):
        val, fromC, _, toC = message.text.split(' ')

        result = compute(val, fromC, toC)
        reply = f'{val} {fromC} = {result:.2f} {toC}' if result is not None else 'Incorrect currencies, try another request'
    elif any(h in words for h in ['привет', 'здравствуйте', 'здарова', 'дарова']):
        reply = 'О, да вы из России! Здравствуйте'
    elif any(h in words for h in ['hello', 'hi', 'yo']):
        reply = 'Hello!'
    elif any(h in words for h in ['bye', 'goodbye', 'chiao']):
        reply = 'Goodbye! Hope i helped you!'
    else:
        reply = "I'm not so smart to understand anything you write, but i can reply to 'Hello' and 'Goodbye'"

    bot.send_message(message.chat.id, reply)
    log(message)


bot.infinity_polling()
