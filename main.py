import telebot
import datetime

# Replace 'YOUR_BOT_TOKEN' with the actual token from BotFather
BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'

bot = telebot.TeleBot(BOT_TOKEN)

# --- Helper Functions ---

def get_current_time():
    """Returns the current time as a formatted string."""
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def get_current_date():
    """Returns the current date as a formatted string."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")

# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Sends a welcome message and help information."""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.KeyboardButton('/time'),
        telebot.types.KeyboardButton('/date'),
        telebot.types.KeyboardButton('/caps'),
        telebot.types.KeyboardButton('/buttons')
    )

    bot.reply_to(message, 
                 "Howdy! I'm a helpful Telegram bot. \n"
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
    """Sends a hello message."""
    bot.reply_to(message, "Hello there!")

@bot.message_handler(commands=['info'])
def send_info(message):
    """Sends information about the bot."""
    bot.reply_to(message, "I'm a bot created with Python and the Telebot library.")

@bot.message_handler(commands=['time'])
def send_time(message):
    """Sends the current time."""
    bot.reply_to(message, f"The current time is: {get_current_time()}")

@bot.message_handler(commands=['date'])
def send_date(message):
    """Sends the current date."""
    bot.reply_to(message, f"Today's date is: {get_current_date()}")

@bot.message_handler(commands=['caps'])
def uppercase(message):
    """Converts the text after /caps to uppercase."""
    text = message.text.replace('/caps ', '')
    bot.reply_to(message, text.upper())

# --- Inline Button Handler ---

@bot.message_handler(commands=['buttons'])
def send_buttons(message):
    """Sends a message with inline buttons."""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton('Time', callback_data='time'),
        telebot.types.InlineKeyboardButton('Date', callback_data='date'),
        telebot.types.InlineKeyboardButton('Caps', callback_data='caps')
    )
    bot.send_message(message.chat.id, "Click a button:", reply_markup=markup)

# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handles inline button callbacks."""
    if call.data == "time":
        bot.answer_callback_query(call.id, text=f"Current time: {get_current_time()}")
    elif call.data == "date":
        bot.answer_callback_query(call.id, text=f"Today's date: {get_current_date()}")
    elif call.data == "caps":
        bot.answer_callback_query(call.id, text="Send me text to convert to CAPS")
        bot.register_next_step_handler(call.message, process_caps_text)

def process_caps_text(message):
    """Processes the text sent after clicking the 'Caps' button."""
    bot.send_message(message.chat.id, message.text.upper())

# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling() 
    
