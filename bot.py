import telebot
from telebot import types
import sqlite3
from datetime import datetime
import requests
import json
import configparser
import random
from client import domanda, answer

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


def user_check_new(cid, db_file=DB_FILE):
    """
    Check if a user exists in the chatbot database
    """
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("select * from users where chat_id = ?", (cid,))
    results = cur.fetchone()
    conn.close()
    if results is None:
        return True
    else:
        return False


def ask_nickname(message, bot):
    """
    Ask preferred nickname to new users
    """
    # To be implemented
    # Temporary using Telegram Username
    # markup = types.ForceReply(selective=False)
    # bot.send_message(cid, "Write your username:", reply_markup=markup)
    nickname = message.chat.username
    return nickname



def ask_gdpr(cid, bot):
    """
    Ask GDPR consent to new users
    """
    # To be better implemented
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('GDPR - YES')
    #itembtn2 = types.KeyboardButton('no')
    markup.add(itembtn1)
    bot.send_message(cid, "Provide consent for GDPR. You can see our privacy policy at https://noi.bz.it/en/privacy-cookie-policy:", reply_markup=markup)
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
        # Put to False to limit games
        return True
    else:
        return True


def get_webcams():
    """
    Get three random webcams from opendatahub.bz.it
    Prepares dictionary for trivia
    """
    seed = random.randint(0, 10)
    link = f"https://tourism.opendatahub.bz.it/v1/WebcamInfo?pagenumber=1&pagesize=3&active=true&odhactive=true&seed={seed}&removenullvalues=false"
    results_json = requests.get(link)
    results = json.loads(results_json.text)
    webcams = results.get("Items")
    image_urls = [item.get("Webcamurl") for item in webcams]
    shortnames = [item.get("Shortname") for item in webcams]
    trivia = [{"key": i,  "url": url, "name": name} for (i, url, name) in zip([1, 2, 3], image_urls, shortnames)]
    return trivia


def setup_question(cid, referral, trivia, db_file=DB_FILE):
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    correct = random.randint(0, 2)
    url = trivia[correct].get("url")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("insert into answers (chat_id, referral, correct, url, timestamp) values (?, ?, ?, ?, ?)", (cid, referral, correct, url, ts))
    question_id = cur.lastrowid
    conn.commit()
    conn.close()
    return question_id, correct


def check_answer(question_id, answer_id, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        "select correct, url from answers where id = ?", (int(question_id),)
    )
    results = cur.fetchone()
    conn.close()
    return results



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
    "CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id text, points integer, referral text, correct integer, url text, timestamp text)"
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
def greet_user(message):
    cid = message.chat.id
    referral = telebot.util.extract_arguments(message.text)
    print("referral: ", referral)
    if user_check_new(cid):
        ask_gdpr(cid, bot)   
    # Check that the user did not play more than 3 times
    # with the same referral code
    else:
        if referral:
            if check_referral(cid, referral):
                trivia = get_webcams()
                question_id, correct = setup_question(cid, referral, trivia)
                question_text = f"{question_id} - Which one of the pictures is {trivia[correct].get('name')}?"
                domanda(trivia, question_text)
                bot.send_message(cid, question_text)
                for i, option in enumerate(trivia):
                    bot.send_message(cid, f"Image {i+1}")
                    bot.send_photo(cid, option.get("url"))
                markup = types.ReplyKeyboardMarkup(row_width=3)
                itembtn1 = types.KeyboardButton(f'Question {question_id} - Image 1')
                itembtn2 = types.KeyboardButton(f'Question {question_id} - Image 2')
                itembtn3 = types.KeyboardButton(f'Question {question_id} - Image 3')
                markup.add(itembtn1, itembtn2, itembtn3)
                bot.send_message(cid, question_text, reply_markup=markup)
                # Implement game using referral
            else:
                pass
                # Implement suggestion for other places to go


@bot.message_handler(func=lambda message: message.text == 'GDPR - YES')
def register_user(message):
    cid = message.chat.id
    gdpr = "consent"
    nickname = ask_nickname(message, bot)
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    user_registration(cid, nickname, gdpr, ts, db_file=DB_FILE)
    markup = types.ReplyKeyboardRemove(selective=False) 
    bot.send_message(cid, "Great, you are ready to play! Scan the QR code near you!", reply_markup=markup)


@bot.message_handler(regexp="^Question \d+ - Image [123]$")
def handle_quiz_answer(message):
    question_id = message.text.split(" - ")[0][9:].strip()
    answer_id = message.text[-1:].strip()
    correct, url = check_answer(question_id, answer_id)
    answer("The correct answer is:", correct, url)
    


@bot.message_handler()
def debug(message):
    print("message not handled", message)


# Start polling for incoming messages
bot.infinity_polling()
