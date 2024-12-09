import telebot
import datetime

# Bot token (already replaced)
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
        telebot.types.InlineKeyboardButton('Set Reminder', callback_data='set_reminder'),
        telebot.types.InlineKeyboardButton('Get My ID', callback_data='get_id'),
        telebot.types.InlineKeyboardButton('Forward Message', callback_data='forward_message'),
        telebot.types.InlineKeyboardButton('Extract Text', callback_data='extract_text')
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
    elif call.data == "set_reminder":
        bot.answer_callback_query(call.id, text="Send me a message in the format 'reminder <minutes> <message>'")
        bot.register_next_step_handler(call.message, process_reminder)
    elif call.data == "get_id":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Your Telegram ID: {call.from_user.id}")
    elif call.data == "forward_message":
        bot.answer_callback_query(call.id, text="Forward the message you want to me")
        bot.register_next_step_handler(call.message, process_forward_message)
    elif call.data == "extract_text":
        bot.answer_callback_query(call.id, text="Send me a photo with text to extract")
        bot.register_next_step_handler(call.message, process_extract_text)

def process_reminder(message):
    """Processes the reminder message and sets a reminder."""
    try:
        parts = message.text.split(' ', 2)
        minutes = int(parts[1])
        reminder_text = parts[2]
        bot.send_message(message.chat.id, f"Reminder set for {minutes} minutes!")
        time.sleep(minutes * 60)  # Wait for the specified time
        bot.send_message(message.chat.id, f"Reminder: {reminder_text}")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Invalid reminder format. Use 'reminder <minutes> <message>'")

def process_forward_message(message):
    """Forwards the received message to the user."""
    if message.forward_from:
        bot.send_message(message.chat.id, f"Forwarded message:\n\n{message.text}")
    else:
        bot.send_message(message.chat.id, "Please forward a message to me.")

def process_extract_text(message):
    """Extracts text from the photo and sends it to the user."""
    # This is a placeholder. You'll need to use an OCR library (like pytesseract) to implement this.
    bot.send_message(message.chat.id, "This feature is not yet implemented.")
    # Example implementation with pytesseract (you'll need to install it: pip install pytesseract)
    # if message.photo:
    #     file_id = message.photo[-1].file_id
    #     file_info = bot.get_file(file_id)
    #     downloaded_file = bot.download_file(file_info.file_path)
    #     with open("image.jpg", 'wb') as new_file:
    #         new_file.write(downloaded_file)
    #     try:
    #         from PIL import Image
    #         import pytesseract
    #         text = pytesseract.image_to_string(Image.open('image.jpg'))
    #         bot.reply_to(message, f"Extracted text:\n\n{text}")
    #     except:
    #         bot.reply_to(message, "Error extracting text.")
    # else:
    #     bot.reply_to(message, "Please send a photo with text.")


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
