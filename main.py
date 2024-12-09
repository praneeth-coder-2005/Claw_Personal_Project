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

# --- Command Handler ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Sends a welcome message and inline buttons."""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton('Time', callback_data='time'),
        telebot.types.InlineKeyboardButton('Date', callback_data='date'),
        telebot.types.InlineKeyboardButton('Caps', callback_data='caps'),
        telebot.types.InlineKeyboardButton('Hello', callback_data='hello'),
        telebot.types.InlineKeyboardButton('Info', callback_data='info')
    )
    bot.reply_to(message, "Hello! I'm a helpful bot. Choose an option:", reply_markup=markup)

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
    elif call.data == "hello":
        bot.answer_callback_query(call.id)  # Clear the notification
        bot.send_message(call.message.chat.id, "Hello there!")
    elif call.data == "info":
        bot.answer_callback_query(call.id) 
        bot.send_message(call.message.chat.id, "I'm a bot created with Python and Telebot.")

def process_caps_text(message):
    """Processes the text sent after clicking the 'Caps' button."""
    bot.send_message(message.chat.id, message.text.upper())

# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling() 
    
