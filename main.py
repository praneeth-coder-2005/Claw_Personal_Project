import telebot
import datetime
import requests
import logging

# --- Configuration ---

BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'
OMDB_API_KEY = "a3b61eaa"

# --- Logging ---

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# --- Bot Initialization ---

bot = telebot.TeleBot(BOT_TOKEN)

# --- Helper Functions ---

def get_current_time():
    """Returns the current time as a formatted string."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def get_current_date():
    """Returns the current date as a formatted string."""
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_movie_details(movie_name):
    """Fetches movie details from OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&t={movie_name}"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data['Response'] == 'True':
            # ... (extract movie details as before) ...
            return movie_info
        else:
            return "Movie not found."

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie details: {e}")
        return "Error fetching movie data."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    # ... (same as before) ...


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    # ... (same as before) ...


# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    try:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton('Time', callback_data='time'),
            telebot.types.InlineKeyboardButton('Date', callback_data='date'),
            telebot.types.InlineKeyboardButton('Movie Details', callback_data='movie_details'),
            telebot.types.InlineKeyboardButton('Movie Ratings', callback_data='movie_ratings')
        )
        bot.reply_to(message, "Hello! I'm a helpful bot. Choose an option:", reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        bot.reply_to(message, "Oops! Something went wrong. Please try again later.")


# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handles inline button callbacks."""
    try:
        if call.data == "time":
            bot.answer_callback_query(call.id, text=f"Current time: {get_current_time()}")
        elif call.data == "date":
            bot.answer_callback_query(call.id, text=f"Today's date: {get_current_date()}")
        elif call.data == "movie_details":
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "Send me a movie title to get details")
            bot.register_next_step_handler(call.message, process_movie_request)
        elif call.data == "movie_ratings":
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "Send me a movie title to get ratings")
            bot.register_next_step_handler(call.message, process_movie_rating_request)

    except Exception as e:
        logger.error(f"Error in callback_query: {e}")
        bot.send_message(call.message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Message Handlers ---

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    # ... (same as before)


def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    # ... (same as before)


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
    
