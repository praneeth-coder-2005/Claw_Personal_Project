import telebot
import datetime
import requests

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
            title = data['Title']
            year = data['Year']
            plot = data['Plot']
            poster = data['Poster']
            imdb_rating = data['imdbRating']
            return f"Title: {title}\nYear: {year}\nPlot: {plot}\nIMDb Rating: {imdb_rating}\nPoster: {poster}"
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


# --- Command Handler ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Sends a welcome message and inline buttons."""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton('Time', callback_data='time'),
        telebot.types.InlineKeyboardButton('Date', callback_data='date'),
        telebot.types.InlineKeyboardButton('Movie Details', callback_data='movie_details'),
        telebot.types.InlineKeyboardButton('Movie Ratings', callback_data='movie_ratings')
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
    elif call.data == "movie_details":
        bot.answer_callback_query(call.id, text="Send me a movie title to get details")
        bot.register_next_step_handler(call.message, process_movie_request)
    elif call.data == "movie_ratings":
        bot.answer_callback_query(call.id, text="Send me a movie title to get ratings")
        bot.register_next_step_handler(call.message, process_movie_rating_request)

def process_movie_request(message):
    """Processes the movie title and sends movie details."""
    movie_name = message.text
    movie_info = get_movie_details(movie_name)
    bot.send_message(message.chat.id, movie_info)

def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    movie_name = message.text
    movie_ratings = get_movie_rating(movie_name)
    bot.send_message(message.chat.id, movie_ratings)

# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
