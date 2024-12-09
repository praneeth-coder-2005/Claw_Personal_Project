import telebot
import datetime

# Replace 'YOUR_BOT_TOKEN' with the actual token from BotFather
BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'

bot = telebot.TeleBot(BOT_TOKEN)

# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/time')
    itembtn2 = telebot.types.KeyboardButton('/date')
    itembtn3 = telebot.types.KeyboardButton('/caps')
    markup.add(itembtn1, itembtn2, itembtn3)

    bot.reply_to(message, "Howdy! I'm a helpful Telegram bot. \n"
                         "Here's what I can do:\n"
                         "/hello - Greet me.\n"
                         "/info - Get info about me.\n"
                         "/time - Get the current time.\n"
                         "/date - Get the current date.\n"
                         "/caps - Convert your text to ALL CAPS.\n"
                         "/buttons - Show you some buttons.",
                         reply_markup=markup)

@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Hello there!")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "I'm a bot created with Python and the Telebot library.")

@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    bot.reply_to(message, f"The current time is: {current_time}")

@bot.message_handler(commands=['date'])
def send_date(message):
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    bot.reply_to(message, f"Today's date is: {current_date}")

@bot.message_handler(commands=['caps'])
def uppercase(message):
    text = message.text.replace('/caps ', '')
    bot.reply_to(message, text.upper())

# --- Inline Button Handler ---

@bot.message_handler(commands=['buttons'])
def send_buttons(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.InlineKeyboardButton('Time', callback_data='time')
    itembtn2 = telebot.types.InlineKeyboardButton('Date', callback_data='date')
    itembtn3 = telebot.types.InlineKeyboardButton('Caps', callback_data='caps')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Click a button:", reply_markup=markup)

# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "time":
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        bot.answer_callback_query(call.id, text=f"Current time: {current_time}")
    elif call.data == "date":
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        bot.answer_callback_query(call.id, text=f"Today's date: {current_date}")
    elif call.data == "caps":
        bot.answer_callback_query(call.id, text="Send me text to convert to CAPS")
        bot.register_next_step_handler(call.message, process_caps_text)

def process_caps_text(message):
    bot.send_message(message.chat.id, message.text.upper())

# Start listening for messages
bot.infinity_polling()
        
