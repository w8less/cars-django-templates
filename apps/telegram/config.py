from os import environ
import telebot

TOKEN = environ.get('TOKEN')

BOT = telebot.TeleBot(TOKEN)
