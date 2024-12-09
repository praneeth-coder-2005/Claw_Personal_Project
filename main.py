import telebot

# Replace 'YOUR_BOT_TOKEN' with the actual token from BotFather
BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'

bot = telebot.TeleBot(BOT_TOKEN)

# Handle '/start' and '/help' commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy! I'm a simple Telegram bot. \n"
                         "Use /hello to greet me. \n"
                         "Use /info to get some info.")

# Handle '/hello' command
@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Hello there!")

# Handle '/info' command
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "I'm a bot created with Python and the Telebot library.")

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "I received your message: " + message.text)

# Start listening for messages
bot.infinity_polling() 
