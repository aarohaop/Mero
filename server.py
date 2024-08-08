import telegram.ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pymongo.mongo_client import MongoClient
import requests
import string
import random

# Text template for balance information
BALANCE_TEXT = """User: {username}
Publisher Earnings: {pbalance}
Referral Earnings: {rbalance}
Total Earnings: {tbalance}"""

# Generate a random string
def end_gen(length):
    letters = string.ascii_lowercase + string.digits + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

# MongoDB connection URI
uri = "mongodb+srv://aaroha:aaroha@cluster0.xfupmjy.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['TeleUsers']
collection = db['TeleAuth']

# Check if user is authenticated
def is_auth(uname):
    query = {"_id": uname}
    result = collection.find_one(query)
    return result

# User login function
def login(uname, api_key):
    d_check = is_auth(uname)
    if d_check is None:
        document = {'_id': uname, 'api_key': api_key}
        collection.insert_one(document)
        return True
    else:
        return False

# User logout function
def logout(uname):
    query = {'_id': uname}
    result = collection.find_one(query)
    if result is not None:
        collection.delete_one(query)
        return True
    else:
        return False

# Generate a shortened link
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

# Check user's balance
def shortner_balance(username, API, URL):
    try:
        response = requests.get(f'https://{URL}/api?api={API}')
        resp = response.json()
        
        if resp['status'] == 1:
            username = resp['username']
            pbalance = resp['publisher_earnings']
            rbalance = resp['referral_earnings']
            tbalance = resp['total_earnings']
            return BALANCE_TEXT.format(username=username, pbalance=pbalance, rbalance=rbalance, tbalance=tbalance)
        
        elif resp['status'] == 2:  
            return "Your Account is Pending"
        
        elif resp['status'] == 3:
            return "Your Account is Banned"
        
    except Exception as e:
        return str(e)

# Start command handler
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Sign Up", url="https://ez4short.xyz/auth/signup")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Lado Khau.", reply_markup=reply_markup)

# Login command handler
def api_Login(update, context):
    user = update.message.from_user
    api_key = context.args[0]
    username = user.username
    resp = login(username, api_key)
    if resp:
        update.message.reply_text("You have successfully logged in.")
    else:
        update.message.reply_text("You are already logged in.")

# Logout command handler
def api_Logout(update, context):
    user = update.message.from_user
    username = user.username
    resp = logout(username)
    if resp:
        update.message.reply_text("You are logged out successfully.")
    else:
        update.message.reply_text("You haven't logged in yet. Please login first.")

# Check balance command handler
def api_CheckBalance(update, context):
    user = update.message.from_user
    username = user.username
    
    # Fetch the user details from the database
    user_data = is_auth(username)
    
    if user_data is not None:
        API = user_data['api_key']
        URL = "ez4short.xyz"  # Base URL
        
        balance_message = shortner_balance(username, API, URL)
        update.message.reply_text(balance_message)
    else:
        update.message.reply_text("You haven't logged in yet. Please login first.")

# Get API token instructions handler
def get_api(update, context):
    keyboard = [
        [InlineKeyboardButton("Get Token", url="https://ez4short.xyz/member/tools/api")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = """• First visit ez4short.xyz/member/tools/api
• Copy the API TOKEN and come back to the bot.
• Input /login <API_KEY> to log in.
• Now the bot will be successfully connected to your ez4short.xyz account."""
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

# Handle generic messages
def handle_message(update, context):
    message = update.message.text
    user = update.message.from_user
    username = user.username
    if is_auth(username) is not None:
        caption = link_gen(username, message)
        update.message.reply_text(caption)
    else:
        update.message.reply_text("Please login first using /login <API_KEY>.")

# Features command handler
def feature(update, context):
    features_text = """
    Available Features:
    1. /login <API_KEY> - Log in with your API key.
    2. /logout - Log out from the bot.
    3. /balance - Check your current balance.
    4. /get_api - Get the link to retrieve your API token.
    5. Send a URL to shorten it.
    """
    update.message.reply_text(features_text)

# Main function to run the bot
def main():
    bot = telegram.Bot("7163612647:AAFpZ3iSUfv8TZFpKd50-N5RRgN-2z7DWmM")
    updater = telegram.ext.Updater(bot.token, use_context=True)
    disp = updater.dispatcher
    disp.add_handler(telegram.ext.CommandHandler('start', start))
    disp.add_handler(telegram.ext.CommandHandler('login', api_Login))
    disp.add_handler(telegram.ext.CommandHandler('logout', api_Logout))
    disp.add_handler(telegram.ext.CommandHandler('balance', api_CheckBalance))
    disp.add_handler(telegram.ext.CommandHandler('get_api', get_api))
    disp.add_handler(telegram.ext.CommandHandler('feature', feature))
    disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, handle_message))
    updater.start_polling()

# Start the bot with drop_pending_updates set to True
    updater.start_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
