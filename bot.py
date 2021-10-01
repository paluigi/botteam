import telebot
import sqlite3
import json
import configparser

# Importing config parser to get secrets
config = configparser.ConfigParser()
config.read('secret.ini')

# Constants definition
TOKEN = config["DEFAULT"]["token"]
DB_FILE = "bozenbot.db"
HELP_MSG = "I'm a polite bot, built for the NOI Hackathon"

bot = telebot.TeleBot(TOKEN, parse_mode=None, threaded=False)


# Send message for info
@bot.message_handler(commands=['help'])
def send_info(message):
    bot.reply_to(message, HELP_MSG)


# Start polling for incoming messages
bot.infinity_polling()
