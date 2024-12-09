import telebot
import datetime

# Replace 'YOUR_BOT_TOKEN' with the actual token from BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)

# Handle '/start' and '/help' commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy! I'm a helpful Telegram bot. \n"
                         "Here's what I can do:\n"
                         "/hello - Greet me.\n"
                         "/info - Get info about me.\n"
                         "/time - Get the current time.\n"
                         "/date - Get the current date.\n"
                         "/caps - Convert your text to ALL CAPS.")

# Handle '/hello' command
@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Hello there!")

# Handle '/info' command
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "I'm a bot created with Python and the Telebot library.")

# Handle '/time' command
@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    bot.reply_to(message, f"The current time is: {current_time}")

# Handle '/date' command
@bot.message_handler(commands=['date'])
def send_date(message):
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    bot.reply_to(message, f"Today's date is: {current_date}")

# Handle '/caps' command
@bot.message_handler(commands=['caps'])
def uppercase(message):
    text = message.text.replace('/caps ', '')  # Remove the command
    bot.reply_to(message, text.upper())

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "I received your message: " + message.text)

# Start listening for messages
bot.infinity_polling()
    
