import datetime
import logging

import requests
import telebot

# --- Configuration ---

BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'
OMDB_API_KEY = "a3b61eaa"

# --- Logging ---

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# --- Bot Initialization ---

bot = telebot.TeleBot(BOT_TOKEN)


# --- Helper Functions ---

def _make_omdb_api_request(url):
    """Makes a request to the OMDb API and handles errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['Response'] == 'True':
            return data
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making OMDb API request: {e}")
        return None


def get_movie_details(movie_name):
    """Fetches movie details from OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&t={movie_name}"
    data = _make_omdb_api_request(complete_url)

    if data:
        # Extract and format movie details (use Markdown for better readability)
        title = data['Title']
        year = data['Year']
        rated = data['Rated']
        released = data['Released']
        runtime = data['Runtime']
        genre = data['Genre']
        director = data['Director']
        writer = data['Writer']
        actors = data['Actors']
        plot = data['Plot']
        language = data['Language']
        country = data['Country']
        awards = data['Awards']
        poster = data['Poster']
        imdb_rating = data['imdbRating']
        imdb_votes = data['imdbVotes']
        imdb_id = data['imdbID']

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
        return "Error fetching movie data or movie not found."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&t={movie_name}"
    data = _make_omdb_api_request(complete_url)

    if data:
        ratings = data['Ratings']
        rating_str = ""
        for rating in ratings:
            source = rating['Source']
            value = rating['Value']
            rating_str += f"{source}: {value}\n"
        return rating_str
    else:
        return "Error fetching movie data or movie not found."


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&s={movie_name}"
    data = _make_omdb_api_request(complete_url)

    if data:
        return data['Search']
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


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
