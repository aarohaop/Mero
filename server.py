import telegram.ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pymongo.mongo_client import MongoClient
import requests
import string
import random

def end_gen(length):
    letters = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str

uri = "mongodb+srv://aaroha:aaroha@cluster0.xfupmjy.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['TeleUsers']
collection = db['TeleAuth']

# Authentication functions
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

# Link generator function
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

# Function to check balance
def check_balance(api_key):
    url = f"https://ez4short.xyz/api/balance?api={api_key}&format=json"  # Example URL, modify according to actual API documentation
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON
    else:
        return "Failed to retrieve balance."

# Handlers
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Sign Up", url="https://ez4short.xyz/auth/signup")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = '''Hello user! 👋😃

🚀 Welcome to @EZ4short_bot - Your Personal URL Shortener Bot. 🌐

Just send me a link, and I'll work my magic to shorten it for you. Plus, I'll keep track of your earnings! 💰💼

Get started now and experience the power of @EZ4short_bot. 💪🔗

⚡️Still Have Doubts?
⚡️Want to Report Any Bug?
😌Send Here @EZ4short_support'''
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def api_Login(update, context):
    user_rsp = update.message.text.split(" ")
    user = update.message.from_user
    username = user.username
    if len(user_rsp) == 1:
        update.message.reply_text("Please send login API in format of /login 12590xxxxxxxx")
    elif len(user_rsp) == 2:
        ser_rsp = login(username, user_rsp[1])
        if ser_rsp:
            update.message.reply_text(f"Welcome {username}, Now You Can Short Your Links")
        else:
            update.message.reply_text("You are already logged in.")
    else:
        update.message.reply_text("Please send API in format /login 12590xxxxxxxx")

def help(update, context):
    keyboard = [
        [InlineKeyboardButton("Get Help", url="https://t.me/ez4short_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = '''🤖 Welcome to EZ4short Bot!** 🌟

**Getting Started**

**Method 1: API Token Connection**
1️⃣ Visit the [API Tools Page](https://ez4short.xyz//member/tools/api).
2️⃣ Copy your API TOKEN.
3️⃣ Use the command `/login` in this chat, followed by your token.
4️⃣ The bot will be connected to your EZ4short.xyz account.

No account yet?
Register easily at https://ez4short.xyz//auth/signup.

Link Shortening Commands
- Simply send the URL you want to shorten.
- Receive your shortened link instantly.

Bulk Link Shortening
- Send multiple URLs in a message like this:
  - https://google.co
  - https://google.com
  - https://yourlink.com
- All links will be shortened and returned in one go'''
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def feature(update, context):
    update.message.reply_text("""Hello user! 👋

🌟 Explore the Features of @ez4short_bot Bot 🌟

🚀 Discover the power of this AI-driven, user-friendly bot. 🤖

✨ With @ez4short_bot Bot, you can easily shorten multiple links simultaneously.

❓ If you have any feature requests or questions, don't hesitate to reach out to us at @EZ4short_support""")

def handle_message(update, context):
    message = update.message
    user = update.message.from_user
    username = user.username
    if message.photo:
        photo_file_id = message.photo[-1].file_id
        caption = message.caption
        links = re.findall(r'(https?://\S+)', caption)
        filtered_list = [link for link in links if "t.me" not in link]
        short_link = []
        for link in filtered_list:
            short_link.append(link_gen(username, link))
            caption = caption.replace(link, f"{short_link[-1]}")
        context.bot.send_photo(chat_id=message.chat_id, photo=photo_file_id, caption=caption)
    elif message.text:
        if "http" in message.text:
            caption = message.text
            links = re.findall(r'(https?://\S+)', caption)
            filtered_list = [link for link in links if "t.me" not in link]
            short_link = []
            for link in filtered_list:
                short_link.append(link_gen(username, link))
                caption = caption.replace(link, f"{short_link[-1]} ")
            update.message.reply_text(caption)
        else:
            update.message.reply_text("Please send me any link or forward a whole post")
    else:
        update.message.reply_text("Please send me any link or forward a whole post")

def get_api(update, context):
    keyboard = [
        [InlineKeyboardButton("Get Token", url="https://ez4short.xyz/member/tools/api")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = """• First visit ez4short.xyz/member/tools/api
• Copy the API TOKEN and come back to the Bot.
• Input /token and paste the token copied from ez4short.xyz/member/tools/api
• Now the bot will be successfully connected to your ez4short.xyz account."""
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def api_Logout(update, context):
    user = update.message.from_user
    username = user.username
    resp = logout(username)
    if resp:
        update.message.reply_text("You are logged out successfully")
    else:
        update.message.reply_text("You haven't logged in yet. Please login first.")

def check_balance(api_key):
    url = f"https://ez4short.xyz/api/balance?api={api_key}&format=json"  # Modify according to actual API documentation
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Assuming the API returns JSON
        # You might need to adjust this based on the actual response structure
        return f"Your current balance is: {data.get('balance', 'Not available')}"
    except requests.RequestException as e:
        return f"Failed to retrieve balance: {e}"
    except ValueError:
        return "Failed to parse balance response."

# Main function to set up the bot
def main():
    bot = telegram.Bot("6548971110:AAGW5_X3noXCCZQWuXm-FtfDvPfS-tTKe7c")
    updater = telegram.ext.Updater(bot.token, use_context=True)
    disp = updater.dispatcher
    disp.add_handler(telegram.ext.CommandHandler('start', start))
    disp.add_handler(telegram.ext.CommandHandler('help', help))
    disp.add_handler(telegram.ext.CommandHandler('login', api_Login))
    disp.add_handler(telegram.ext.CommandHandler('get_api', get_api))
    disp.add_handler(telegram.ext.CommandHandler('logout', api_Logout))
    disp.add_handler(telegram.ext.CommandHandler('features', feature))
    disp.add_handler(telegram.ext.CommandHandler('balance', balance))  # Add the balance command handler
    disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, handle_message))
    updater.start_polling()

if __name__ == "__main__":
    main()
