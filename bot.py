from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '6548971110:AAGW5_X3noXCCZQWuXm-FtfDvPfS-tTKe7c'
API_URL = 'https://ez4short.xyz/member/tools/api'  # Replace with your balance API URL
API_KEY = '12b2d8281afa6d870f9b44bd0cba166704c7ea50'  # Replace with your API key

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /balance to check your balance.')

def balance(update: Update, context: CallbackContext) -> None:
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        balance = data.get('balance', 'Unavailable')
        update.message.reply_text(f'Your current balance is: {balance}')
    else:
        update.message.reply_text('Failed to retrieve balance. Please try again later.')

def main() -> None:
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('balance', balance))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
