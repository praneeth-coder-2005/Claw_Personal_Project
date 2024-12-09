import telebot
import datetime
import requests
import logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Set logging level to DEBUG for detailed logs

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

def get_movie_details(movie_name):
    """Fetches movie details from OMDb API."""
    api_key = "a3b61eaa"  # Your OMDb API key
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={api_key}&t={movie_name}"
    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            # ... (extract movie details as before) ...
            return movie_info
        else:
            return "Movie not found."
    else:
        return "Error fetching movie data."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    # ... (same as before) ...


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    # ... (same as before) ...


def get_streaming_availability(movie_name):
    """Fetches streaming availability from Watchmode API."""
    api_key = "5LJbT9QuNsWaL7CVKZEYJ9KGpmwiqHEhEFuxU1Ax"  # Your Watchmode API key
    base_url = "https://api.watchmode.com/v1/title/"
    
    try:
        # First, get the movie ID using the search API
        search_url = f"https://api.watchmode.com/v1/search/?apiKey={api_key}&search_field=name&search_value={movie_name}"
        search_response = requests.get(search_url)
        search_response.raise_for_status()  # Raise an exception for bad status codes
        search_data = search_response.json()

        if search_data['title_results']:
            movie_id = search_data['title_results'][0]['id']  # Get the first result's ID

            # Now, use the movie ID to get streaming details
            details_url = f"{base_url}{movie_id}/sources/?apiKey={api_key}"
            details_response = requests.get(details_url)
            details_response.raise_for_status()  # Raise an exception for bad status codes
            details_data = details_response.json()

            streaming_sources = []
            for source in details_data:
                if source['type'] == 'subscription':
                    streaming_sources.append(source['name'])
            if streaming_sources:
                return f"Streaming on: {', '.join(streaming_sources)}"
            else:
                return "Not currently available on any streaming services."
        else:
            return "Movie not found."
    except requests.exceptions.RequestException as e:
        return f"Error fetching streaming data: {e}"


# --- Command Handler ---

# ... (command handler: send_welcome) ...

# --- Callback Query Handler ---

# ... (callback query handler: callback_query) ...

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    # ... (same as before) ...

def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    # ... (same as before) ...

def process_streaming_availability(message):
    """Processes the movie title and sends streaming availability."""
    # ... (same as before) ...

# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
                
