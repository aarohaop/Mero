import telegram.ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pymongo.mongo_client import MongoClient
import requests
import string
import random

def end_gen(length):
    letters = string.ascii_lowercase + string.digits + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

uri = "mongodb+srv://aaroha:aaroha@cluster0.xfupmjy.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['TeleUsers']
collection = db['TeleAuth']

# User login
def is_auth(uname):
    query = {"_id": uname}
    result = collection.find_one(query)
    return result

def login(uname, api_key):
    d_check = is_auth(uname)
    if d_check is None:
        document = {'_id': uname, 'api_key': api_key}
        collection.insert_one(document)
        return True
    else:
        return False

def logout(uname):
    query = {'_id': uname}
    result = collection.find_one(query)
    if result is not None:
        collection.delete_one(query)
        return True
    else:
        return False

# Link generator
def link_gen(uname, long_link):
    if is_auth(uname) is not None:
        query = {"_id": uname}
        res = collection.find_one(query)
        api_key = res['api_key']
        url = f"https://ez4short.xyz/api?api={api_key}&url={long_link}&format=text"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.text
    else:
        return "You haven't logged in yet. Please login first."

def check_balance(uname):
    if is_auth(uname) is not None:
        query = {"_id": uname}
        res = collection.find_one(query)
        api_key = res['api_key']
        url = f"https://ez4short.xyz/api/balance?api={api_key}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('balance', 'Balance information not available.')
        else:
            return "Failed to retrieve balance. Please try again later."
    else:
        return "You haven't logged in yet. Please login first."

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Sign Up", url="https://ez4short.xyz/auth/signup")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to the bot! Please sign up first.", reply_markup=reply_markup)

def api_Login(update, context):
    user = update.message.from_user
    api_key = context.args[0]
    username = user.username
    resp = login(username, api_key)
    if resp:
        update.message.reply_text("You have successfully logged in.")
    else:
        update.message.reply_text("You are already logged in.")

def api_Logout(update, context):
    user = update.message.from_user
    username = user.username
    resp = logout(username)
    if resp:
        update.message.reply_text("You are logged out successfully.")
    elif not resp:
        update.message.reply_text("You haven't logged in yet. Please login first.")
    else:
        update.message.reply_text("Something went wrong.")

def api_CheckBalance(update, context):
    user = update.message.from_user
    username = user.username
    balance = check_balance(username)
    update.message.reply_text(f"Your balance is: {balance}")

def get_api(update, context):
    keyboard = [
        [InlineKeyboardButton("Get Token", url="https://ez4short.xyz/member/tools/api")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = """• First visit ez4short.xyz/member/tools/api
• Copy the API TOKEN and come back to the bot.
• Input /token and paste the token copied from ez4short.xyz/member/tools/api
• Now the bot will be successfully connected to your ez4short.xyz account."""
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def handle_message(update, context):
    message = update.message.text
    user = update.message.from_user
    username = user.username
    if is_auth(username) is not None:
        caption = link_gen(username, message)
        update.message.reply_text(caption)
    else:
        update.message.reply_text("Please login first using /login <API_KEY>.")

def main():
    bot = telegram.Bot("7163612647:AAFpZ3iSUfv8TZFpKd50-N5RRgN-2z7DWmM")
    updater = telegram.ext.Updater(bot.token, use_context=True)
    disp = updater.dispatcher
    disp.add_handler(telegram.ext.CommandHandler('start', start))
    disp.add_handler(telegram.ext.CommandHandler('help', help))
    disp.add_handler(telegram.ext.CommandHandler('login', api_Login))
    disp.add_handler(telegram.ext.CommandHandler('get_api', get_api))
    disp.add_handler(telegram.ext.CommandHandler('logout', api_Logout))
    disp.add_handler(telegram.ext.CommandHandler('features', feature))
    disp.add_handler(telegram.ext.CommandHandler('balance', api_CheckBalance))  # New handler for balance check
    disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, handle_message))
    updater.start_polling()

if __name__ == "__main__":
    main()
