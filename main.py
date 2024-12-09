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
            return "Movie not found."

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie details: {e}")
        return "Error fetching movie data."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&t={movie_name}"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data['Response'] == 'True':
            ratings = data['Ratings']
            rating_str = ""
            for rating in ratings:
                source = rating['Source']
                value = rating['Value']
                rating_str += f"{source}: {value}\n"
            return rating_str
        else:
            return "Movie not found."

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie ratings: {e}")
        return "Error fetching movie data."


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&s={movie_name}"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data['Response'] == 'True':
            return data['Search']
        else:
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for movies: {e}")
        return None  # Return None to indicate an error


def get_streaming_availability(movie_name):
    """Fetches streaming availability from Watchmode API."""
    base_url = "https://api.watchmode.com/v1/title/"
    
    try:
        search_url = f"https://api.watchmode.com/v1/search/?apiKey={WATCHMODE_API_KEY}&search_field=name&search_value={movie_name}"
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data['title_results']:
            movie_id = search_data['title_results'][0]['id']

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
# ... (same as before)

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
    # ... (same as before)

def process_streaming_availability(message):
    """Processes the movie title and sends streaming availability."""
    # ... (same as before)

# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
