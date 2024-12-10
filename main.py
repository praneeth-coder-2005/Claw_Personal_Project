import datetime
import logging
import os
import time
from io import BytesIO

import requests
import telebot
from tqdm import tqdm

# --- Configuration ---

BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your actual bot token
OMDB_API_KEY = "YOUR_OMDB_API_KEY"  # Replace with your actual OMDb API key

# --- Logging ---

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# --- Bot Initialization ---

bot = telebot.TeleBot(BOT_TOKEN)

# --- Global Variables ---

user_data = {}  # To store user-specific data during file upload


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


def get_file_size(url):
    """Gets the file size from the Content-Length header."""
    try:
        response = requests.head(url)
        response.raise_for_status()
        file_size = int(response.headers.get('content-length', 0))
        return file_size
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting file size: {e}")
        return 0


def download_file(url, file_name, message):
    """Downloads the file from the URL with a progress bar."""
    file_size = get_file_size(url)
    if file_size == 0:
        bot.send_message(message.chat.id, "Could not determine file size.")
        return None

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Use tqdm for progress bar (without Telegram updates)
        with open(file_name, 'wb') as f, tqdm(
                desc=f"Downloading {file_name}",
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        return file_name

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file: {e}")
        bot.send_message(message.chat.id, f"Error downloading the file: {e}")
        return None


def upload_large_file_to_telegram(file_name, message):
    """Uploads large files to Telegram using file chunking."""
    try:
        with open(file_name, 'rb') as f:
            file_size = os.path.getsize(file_name)

            # Send initial message
            bot.send_message(message.chat.id, f"Uploading {file_name}...")

            part_size = 50 * 1024 * 1024  # 50MB chunks
            parts = range(0, file_size, part_size)
            total_parts = len(parts)

            # Use a unique file_id
            file_id = f"{message.chat.id}_{time.time()}"  

            for i, part in enumerate(parts):
                file_part = BytesIO(f.read(part_size))
                bot.send_chat_action(message.chat.id, 'upload_document')

                # Send the file part with caption and progress
                bot.send_document(
                    message.chat.id,
                    file_part,
                    visible_file_name=file_name,  # Use original file name
                    caption=f"Uploading: {file_name}\nPart {i+1}/{total_parts}",
                    file_id=file_id,  # Use the same file_id for all parts
                    file_part=i,  # Part number
                    file_total_parts=total_parts  # Total number of parts
                )

    except Exception as e:
        logger.error(f"Error uploading large file to Telegram: {e}")
        bot.send_message(message.chat.id, f"Error uploading the file to Telegram: {e}")


def file_size_str(file_size):
    """Converts file size to human-readable string."""
    if file_size < 1024:
        return f"{file_size} B"
    elif file_size < 1024 * 1024:
        return f"{file_size / 1024:.2f} KB"
    elif file_size < 1024 * 1024 * 1024:
        return f"{file_size / (1024 * 1024):.2f} MB"
    else:
        return f"{file_size / (1024 * 1024 * 1024):.2f} GB"


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
            telebot.types.InlineKeyboardButton('Movie Ratings', callback_data='movie_ratings'),
            telebot.types.InlineKeyboardButton('URL Upload', callback_data='url_upload')
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
        elif call.data == "url_upload":
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "Send me the URL of the file you want to upload:")
            bot.register_next_step_handler(call.message, process_url_upload)
        elif call.data == "rename":
            bot.answer_callback_query(call.id)
            message = call.message
            bot.send_message(message.chat.id, "Enter a new file name (without extension):")
            bot.register_next_step_handler(message, process_rename)
        elif call.data == "default" or call.data == "cancel":
            bot.answer_callback_query(call.id)
            message = call.message
            process_file_upload(message, custom_file_name=None)  # Use default name if "default" is clicked
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
                markup.add(telebot.types.InlineKeyboardButton(f"{title} ({year})",callback_data=title))
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


def process_url_upload(message):
    """Handles the URL upload request."""
    try:
        url = message.text.strip()
        file_name = os.path.basename(url)
        file_size = get_file_size(url)

        if file_size == 0:
            bot.send_message(message.chat.id, "Invalid URL or unable to get file size.")
            return

        # Extract original file name and extension
        original_file_name, original_file_ext = os.path.splitext(file_name)

        # Show options for renaming or using the default name
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton('Default', callback_data='default'),
            telebot.types.InlineKeyboardButton('Rename', callback_data='rename')
        )

        bot.send_message(
            message.chat.id,
            f"File: {original_file_name}{original_file_ext}\n"
            f"Size: {file_size_str(file_size)}\n"
            f"Choose an option:",
            reply_markup=markup
        )

        # Store user data for later use
        user_data[message.chat.id] = {'url': url, 'file_name': file_name, 'file_size': file_size}

    except Exception as e:
        logger.error(f"Error in process_url_upload: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_rename(message):
    """Handles the file renaming."""
    try:
        new_file_name = message.text.strip()

        # Get original file extension from user_data
        original_file_ext = os.path.splitext(user_data[message.chat.id]['file_name'])[1]

        # Combine new file name with original extension
        custom_file_name = f"{new_file_name}{original_file_ext}"

        process_file_upload(message, custom_file_name)

    except Exception as e:
        logger.error(f"Error in process_rename: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def process_file_upload(message, custom_file_name=None):  # FIXED: Handle file upload errors
    """Downloads and uploads the file."""
    try:
        url = user_data[message.chat.id]['url']
        file_size = user_data[message.chat.id]['file_size']
        original_file_name = user_data[message.chat.id]['file_name']

        if custom_file_name is None:
            file_name = original_file_name
        else:
            file_name = custom_file_name

        # Download the file (progress bar handled within download_file)
        downloaded_file = download_file(url, file_name, message)

        if downloaded_file:
            try:
        # Upload the file to Telegram (handle large files)
                if file_size > 50 * 1024 * 1024:
                    upload_large_file_to_telegram(downloaded_file, message)
                else:
                    with open(downloaded_file, 'rb') as f:
                        bot.send_chat_action(message.chat.id, 'upload_document')
                        bot.send_document(
                            chat_id=message.chat.id,
                            document=f,
                            caption=f"Uploaded {file_name} ({file_size_str(file_size)})"
                        )

                # Remove the downloaded file after uploading (only if upload was successful)
                os.remove(downloaded_file)

            except Exception as e:
                logger.error(f"Error uploading the file to Telegram: {e}")
                bot.send_message(message.chat.id, f"Error uploading the file to Telegram: {e}")

    except Exception as e:
        logger.error(f"Error in process_file_upload: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
    
    
