import telebot
import datetime
import requests
import logging

# Bot token (already replaced)
BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk' 

bot = telebot.TeleBot(BOT_TOKEN)

# Enable logging for debugging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) 

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
    api_key = "a3b61eaa"  # Your OMDb API key
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={api_key}&t={movie_name}"
    response = requests.get(complete_url)

    if response.status_code == 200:
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
    else:
        return "Error fetching movie data."


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    api_key = "a3b61eaa"  # Your OMDb API key
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={api_key}&s={movie_name}"
    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            movies = data['Search']
            return movies
        else:
            return []  # Return an empty list if no movies are found
    else:
        return []


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
            return "Movie not found on Watchmode."
    except requests.exceptions.RequestException as e:
        return f"Error fetching streaming data: {e}"


# --- Command Handler ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Sends a welcome message and inline buttons."""
    try:
        print("Entering send_welcome function")  # Debug print statement
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton('Time', callback_data='time'),
            telebot.types.InlineKeyboardButton('Date', callback_data='date'),
            telebot.types.InlineKeyboardButton('Movie Details', callback_data='movie_details'),
            telebot.types.InlineKeyboardButton('Movie Ratings', callback_data='movie_ratings'),
            telebot.types.InlineKeyboardButton('Streaming Availability', callback_data='streaming_availability')
        )
        bot.reply_to(message, "Hello! I'm a helpful bot. Choose an option:", reply_markup=markup)
        print("Sent welcome message")  # Debug print statement
    except Exception as e:
        print(f"Error in send_welcome: {e}")  # Print the error to the console
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
        print(f"Error in callback_query: {e}")
        bot.send_message(call.message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    try:
        movie_name = message.text
        movies = search_movies(movie_name)
        if len(movies) == 1:
            # Only one movie found, send details directly
            movie_info = get_movie_details(movies[0]['Title'])
            bot.send_message(message.chat.id, movie_info, parse_mode='Markdown')
        elif len(movies) > 1:
            # Multiple movies found, show inline buttons for selection
            markup = telebot.types.InlineKeyboardMarkup()
            for movie in movies:
                title = movie['Title']
                year = movie['Year']
                button_text = f"{title} ({year})"
                callback_data = title  # Use title as callback data
                markup.add(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))
            bot.send_message(message.chat.id, "Select the correct movie:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Movie not found.")
    except Exception as e:
        print(f"Error in process_movie_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    try:
        movie_name = message.text
        movie_ratings = get_movie_rating(movie_name)
        bot.send_message(message.chat.id, movie_ratings)
    except Exception as e:
        print(f"Error in process_movie_rating_request: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_streaming_availability(message):
    """Processes the movie title and sends streaming availability."""
    try:
        movie_name = message.text
        movies = search_movies(movie_name)
        if len(movies) == 1:
            # Only one movie found, send streaming availability directly
            streaming_info = get_streaming_availability(movies[0]['Title'])
            bot.send_message(message.chat.id, streaming_info)
        elif len(movies) > 1:
            # Multiple movies found, show inline buttons for selection
            markup = telebot.types.InlineKeyboardMarkup()
            for movie in movies:
                title = movie['Title']
                year = movie['Year']
                button_text = f"{title} ({year})"
                callback_data = title  # Use title as callback data
                markup.add(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))
            bot.send_message(message.chat.id, "Select the correct movie:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Movie not found.")
    except Exception as e:
        print(f"Error in process_streaming_availability: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
