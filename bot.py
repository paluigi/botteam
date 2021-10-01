import telebot
import sqlite3
from datetime import datetime
import requests
import json
import configparser

# Temporary imports
import random
import string

# End Temporary

# Importing config parser to get secrets
config = configparser.ConfigParser()
config.read("secret.ini")

# Constants definition
TOKEN = config["DEFAULT"]["token"]
DB_FILE = "bozenbot.db"
HELP_MSG = "I'm a polite bot, built for the NOI Hackathon"  # Insert list of commands with explaination


# Functions definition
def user_registration(cid, nickname, gdpr, ts, db_file=DB_FILE):
    """
    Register new users in the chatbot database
    """
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("insert into users values (?, ?, ?, ?)", (cid, nickname, gdpr, ts))
    conn.commit()
    conn.close()
    return True


def user_check(cid, db_file=DB_FILE):
    """
    Check if a user exists in the chatbot database
    """
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("select * from users where chat_id = ?", (cid,))
    results = cur.fetchone()
    conn.close()
    if results is None:
        return False
    else:
        return True


def ask_nickname():
    """
    Ask preferred nickname to new users
    """
    # To be implemented
    # Temporary random function
    letters = string.ascii_letters
    nickname = "".join(random.choices(letters, k=10))
    return nickname


def ask_gdpr():
    """
    Ask GDPR consent to new users
    """
    # To be implemented
    return "consent"


def check_referral(cid, referral, db_file=DB_FILE):
    """
    Check that the user did not play over three times from the same referral
    Answers table get resetted at midnight
    """
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        "select * from answers where chat_id = ? AND referral = ?", (cid, referral)
    )
    results = cur.fetchall()
    conn.close()
    # play maximum three times from the same referral
    if len(results) > 3:
        return False
    else:
        return True


# Process setup
# Create bot instance
bot = telebot.TeleBot(TOKEN, parse_mode=None, threaded=False)
# Create database and tables
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS users (chat_id text, nickname text, gdpr text, timestamp text)"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS answers (chat_id text, points integer, referral text, timestamp text)"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS leaderboard (chat_id text, score integer, timestamp text)"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS playpoints (referral text, lat integer, lon text)"
)
conn.commit()
conn.close()
# To be implemented
# Populate playpoints table


# Send message for info
@bot.message_handler(commands=["help"])
def send_info(message):
    bot.reply_to(message, HELP_MSG)


# Send message for start
@bot.message_handler(commands=["start"])
def register_user(message):
    cid = message.chat.id
    referral = telebot.util.extract_arguments(message.text)
    if user_check(cid):
        # continue to play
        pass
    else:
        nickname = ask_nickname()
        gdpr = ask_gdpr()
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        user_registration(cid, nickname, gdpr, ts, db_file=DB_FILE)
    # Check that the user did not play more than 3 times
    # with the same referral code
    if check_referral(cid, referral):
        # Implement game using referral
        pass
    else:
        pass
        # Implement suggestion for other places to go


# Start polling for incoming messages
bot.infinity_polling()
