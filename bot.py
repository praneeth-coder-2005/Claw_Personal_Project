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
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making TMDb API request: {e}")
        return None

def get_movie_details(movie_id):
    """Fetches movie details from TMDb API using the movie ID and also returns the image URL."""
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    details_data = _make_tmdb_api_request(details_url)

    if details_data:
        try:
            title = details_data.get('title', 'N/A')
            release_date = details_data.get('release_date', 'N/A')
            year = release_date[:4] if release_date != 'N/A' else 'N/A'
            overview = details_data.get('overview', 'N/A')
            genres = ", ".join([genre['name'] for genre in details_data.get('genres', [])]) or "N/A"
            poster_path = details_data.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None #Poster url can also be none

            vote_average = details_data.get('vote_average', 'N/A')
            vote_count = details_data.get('vote_count', 'N/A')
            runtime = details_data.get('runtime', 'N/A')
            tagline = details_data.get('tagline', 'N/A')
            budget = details_data.get('budget', 'N/A')
            revenue = details_data.get('revenue', 'N/A')

            movie_info = f"""
            🎬 *{title}* ({year})

            **Tagline:** {tagline}
            **Overview:** {overview}
            **Genres:** {genres}
            **Release Date:** {release_date}
            **Runtime:** {runtime} minutes
            **Budget:** ${budget:,}
            **Revenue:** ${revenue:,}
            **Vote Average:** {vote_average} ({vote_count} votes)

            **TMDb ID:** [{movie_id}](https://www.themoviedb.org/movie/{movie_id}) ( {movie_id} )
            """
            return movie_info, poster_url
        except Exception as e:
            logger.error(f"Error formatting movie details: {e}")
            return "Error formatting movie details.", None
    else:
        return "Error fetching movie details.", None

def search_movies(movie_name):
    """Searches for movies with similar names using TMDb API."""
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    search_data = _make_tmdb_api_request(search_url)

    if search_data and search_data.get('results'):
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
            movie_id = call.data  # Use the TMDb ID
            movie_info, poster_url = get_movie_details(movie_id)

            if poster_url:
                bot.send_photo(call.message.chat.id, photo=poster_url, caption=movie_info, parse_mode='Markdown')
            else:
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

        if not movies:
            bot.send_message(message.chat.id, "Movie not found. Please try a different title.")
            return

        if len(movies) == 1:
            movie_id = movies[0]['id']  # Use 'id' from TMDb results
            movie_info, poster_url = get_movie_details(movie_id)
            if poster_url:
               bot.send_photo(message.chat.id, photo=poster_url, caption=movie_info, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, movie_info, parse_mode='Markdown')

        elif len(movies) > 1:
            markup = telebot.types.InlineKeyboardMarkup()
            for movie in movies:
                title = movie['title']
                year = movie['release_date'][:4] if movie.get('release_date') else 'N/A'
                movie_id = movie['id']
                markup.add(telebot.types.InlineKeyboardButton(f"{title} ({year})", callback_data=str(movie_id)))
            bot.send_message(message.chat.id, "Select the correct movie:", reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in process_movie_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")

# --- Start the Bot ---
if __name__ == '__main__':
    bot.infinity_polling()
