import telebot
import datetime
import requests
import logging

# --- Configuration ---

BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'
OMDB_API_KEY = "a3b61eaa"
WATCHMODE_API_KEY = "5LJbT9QuNsWaL7CVKZEYJ9KGpmwiqHEhEFuxU1Ax"

# --- Logging ---

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Set logging level to DEBUG for detailed logs

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
            # Extract and format movie details (use Markdown for better readability)
            title = data['Title']
            year = data['Year']
            # ... (extract other details) ...
            movie_info = f"""
            *Title:* {title} ({year})
            *Rated:* {rated}
            *Released:* {released}
            *Runtime:* {runtime}
            *Genre:* {genre}
            *Director:* {director}
            *Writer:* {writer}
            *Actors:* {actors}
            *Plot:* {plot}
            *Language:* {language}
            *Country:* {country}
            *Awards:* {awards}
            *IMDb Rating:* {imdb_rating} ({imdb_votes} votes)
            *IMDb ID:* {imdb_id}
            *Poster:* {poster}
            """
            return movie_info
        else:
            return "Movie not found."

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie details: {e}")
        return "Error fetching movie data."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    # ... (similar structure as get_movie_details) ...


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    # ... (similar structure as get_movie_details) ...


def get_streaming_availability(movie_name):
    """Fetches streaming availability from Watchmode API."""
    base_url = "https://api.watchmode.com/v1/title/"
    
    try:
        # First, get the movie ID using the search API
        search_url = f"https://api.watchmode.com/v1/search/?apiKey={WATCHMODE_API_KEY}&search_field=name&search_value={movie_name}"
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data['title_results']:
            movie_id = search_data['title_results'][0]['id']

            # Now, use the movie ID to get streaming details
            details_url = f"{base_url}{movie_id}/sources/?apiKey={WATCHMODE_API_KEY}"
            details_response = requests.get(details_url)
            details_response.raise_for_status()
            details_data = details_response.json()

            streaming_sources = [source['name'] for source in details_data if source['type'] == 'subscription']
            return f"Streaming on: {', '.join(streaming_sources)}" if streaming_sources else "Not currently available on any streaming services."

        else:
            return "Movie not found on Watchmode."

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching streaming data: {e}")
        return f"Error fetching streaming data."


# --- Command Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    try:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton('Time', callback_data='time'),
            telebot.types.InlineKeyboardButton('Date', callback_data='date'),
            telebot.types.InlineKeyboardButton('Movie Details', callback_data='movie_details'),
            telebot.types.InlineKeyboardButton('Movie Ratings', callback_data='movie_ratings'),
            telebot.types.InlineKeyboardButton('Streaming Availability', callback_data='streaming_availability')
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
            bot.answer_callback_query(call.id, text="Send me a movie title to get details")
            bot.register_next_step_handler(call.message, process_movie_request)
        elif call.data == "movie_ratings":
            bot.answer_callback_query(call.id, text="Send me a movie title to get ratings")
            bot.register_next_step_handler(call.message, process_movie_rating_request)
        elif call.data == "streaming_availability":
            bot.answer_callback_query(call.id, text="Send me a movie title to check streaming availability")
            bot.register_next_step_handler(call.message, process_streaming_availability)
        else:  # Handle movie selection callbacks
            movie_name = call.data
            streaming_info = get_streaming_availability(movie_name)
            bot.send_message(call.message.chat.id, streaming_info)

    except Exception as e:
        logger.error(f"Error in callback_query: {e}")
        bot.send_message(call.message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Message Handlers ---

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    try:
        movie_name = message.text
        movies = search_movies(movie_name)

        if len(movies) == 1:
            movie_info = get_movie_details(movies[0]['Title'])
            bot.send_message(message.chat.id, movie_info, parse_mode='Markdown')
        elif len(movies) > 1:
            markup = telebot.types.InlineKeyboardMarkup()
            for movie in movies:
                title = movie['Title']
                year = movie['Year']
                markup.add(telebot.types.InlineKeyboardButton(f"{title} ({year})", callback_data=title))
            bot.send_message(message.chat.id, "Select the correct movie:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Movie not found.")

    except Exception as e:
        logger.error(f"Error in process_movie_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    try:
        movie_name = message.text
        movie_ratings = get_movie_rating(movie_name)
        bot.send_message(message.chat.id, movie_ratings)
    except Exception as e:
        logger.error(f"Error in process_movie_rating_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_streaming_availability(message):
    """Processes the movie title and sends streaming availability."""
    # ... (similar structure as process_movie_request) ...


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
    
