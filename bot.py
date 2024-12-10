import datetime
import logging

import requests
import telebot

# --- Configuration ---

BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'  # Replace with your actual bot token
TMDB_API_KEY = "bb5f40c5be4b24660cbdc20c2409835e"  # Replace with your actual TMDb API key

# --- Logging ---

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# --- Bot Initialization ---

bot = telebot.TeleBot(BOT_TOKEN)


# --- Helper Functions ---

def _make_tmdb_api_request(url):
    """Makes a request to the TMDb API and handles errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making TMDb API request: {e}")
        return None


def get_movie_details(movie_name):
    """Fetches movie details from TMDb API."""
    # 1. Search for the movie to get the TMDb ID
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    search_data = _make_tmdb_api_request(search_url)

    if search_data and search_data['results']:
        movie_id = search_data['results'][0]['id']

        # 2. Get movie details using the TMDb ID
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        details_data = _make_tmdb_api_request(details_url)

        if details_data:
            # Extract and format movie details (use Markdown for better readability)
            title = details_data['title']
            year = details_data['release_date'][:4]  # Extract year from release date
            overview = details_data['overview']
            genres = ", ".join([genre['name'] for genre in details_data['genres']])
            poster_path = details_data['poster_path']
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "N/A"
            vote_average = details_data['vote_average']
            vote_count = details_data['vote_count']

            movie_info = f"""
            *Title:* {title} ({year})
            *Overview:* {overview}
            *Genres:* {genres}
            *Poster:* {poster_url}
            *Vote Average:* {vote_average} ({vote_count} votes)
            *TMDb ID:* {movie_id}
            """
            return movie_info
        else:
            return "Error fetching movie details."
    else:
        return "Movie not found."


def search_movies(movie_name):
    """Searches for movies with similar names using TMDb API."""
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    search_data = _make_tmdb_api_request(search_url)

    if search_data and search_data['results']:
        return search_data['results']
    else:
        return []


def get_current_time():
    """Returns the current time as a formatted string."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def get_current_date():
    """Returns the current date as a formatted string."""
    return datetime.datetime.now().strftime("%Y-%m-%d")


# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    try:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton('Time', callback_data='time'),
            telebot.types.InlineKeyboardButton('Date', callback_data='date'),
            telebot.types.InlineKeyboardButton('Movie Details', callback_data='movie_details')
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
        else:  # Handle movie selection callbacks
            bot.answer_callback_query(call.id)
            movie_name = call.data
            movie_info = get_movie_details(movie_name)
            bot.send_message(call.message.chat.id, movie_info, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in callback_query: {e}")
        bot.send_message(call.message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Message Handlers ---

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    try:
        movie_name = message.text
        movies = search_movies(movie_name)

        if movies is None:
            bot.send_message(message.chat.id, "Movie search failed. Please try again later.")
            return

        if len(movies) == 1:
            movie_info = get_movie_details(movies[0]['title'])  # Use 'title' from TMDb results
            bot.send_message(message.chat.id, movie_info, parse_mode='Markdown')
        elif len(movies) > 1:
            markup = telebot.types.InlineKeyboardMarkup()
            for movie in movies:
                title = movie['title']  # Use 'title' from TMDb results
                year = movie['release_date'][:4]  # Extract year from release date
                markup.add(telebot.types.InlineKeyboardButton(f"{title} ({year})", callback_data=title))
            bot.send_message(message.chat.id, "Select the correct movie:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Movie not found.")

    except Exception as e:
        logger.error(f"Error in process_movie_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
