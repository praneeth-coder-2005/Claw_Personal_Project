import datetime
import logging
import os
import time
from io import BytesIO

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
    """Downloads the file from the URL and sends progress updates."""
    file_size = get_file_size(url)
    if file_size == 0:
        bot.send_message(message.chat.id, "Could not determine file size.")
        return None

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create a progress bar (using Unicode characters)
        progress_bar = ""
        progress_bar_length = 20  # Adjust the length of the progress bar

        with open(file_name, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Update progress in Telegram (every 10%)
                    if downloaded % (file_size // 10) == 0:
                        progress = int(downloaded / file_size * progress_bar_length)
                        progress_bar = "█" * progress + "░" * (progress_bar_length - progress)
                        try:
                            bot.edit_message_text(
                                chat_id=message.chat.id,
                                message_id=user_data[message.chat.id]['progress_message_id'],
                                text=f"Downloading: {file_name}\n"
                                     f"Progress: {downloaded / file_size * 100:.1f}%\n"
                                     f"`{progress_bar}`"  # Use Markdown for the progress bar
                            )
                        except telebot.apihelper.ApiException as e:
                            if 'retry_after' in e.result_json:
                                time.sleep(e.result_json['retry_after'])
                                # Retry the update
                                bot.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=user_data[message.chat.id]['progress_message_id'],
                                    text=f"Downloading: {file_name}\n"
                                         f"Progress: {downloaded / file_size * 100:.1f}%\n"
                                         f"`{progress_bar}`"  # Use Markdown for the progress bar
                                )
                            else:
                                raise e  # Re-raise the exception if it's not a FloodWait

        return file_name

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file: {e}")
        bot.send_message(message.chat.id, "Error downloading the file.")
        return None


def upload_large_file_to_telegram(file_name, message):
    """Uploads large files (up to 2GB) to Telegram using file chunking."""
    try:
        with open(file_name, 'rb') as f:
            file_size = os.path.getsize(file_name)

            # Send initial message with progress bar
            progress_message = bot.send_message(message.chat.id, "Uploading...")
            user_data[message.chat.id]['progress_message_id'] = progress_message.message_id

            part_size = 50 * 1024 * 1024  # 50MB chunks
            parts = range(0, file_size, part_size)
            total_parts = len(parts)

            # Use a unique file_id (you can generate a random ID if needed)
            file_id = f"{message.chat.id}_{time.time()}"

            # Create a progress bar (using Unicode characters)
            progress_bar = ""
            progress_bar_length = 20  # Adjust the length of the progress bar

            for i, part in enumerate(parts):
                file_part = BytesIO(f.read(part_size))
                bot.send_chat_action(message.chat.id, 'upload_document')

                # Use the correct method for uploading file parts
                bot.send_file(
                    message.chat.id,
                    file_part,
                    file_id=file_id,
                    file_part=i,
                    file_total_parts=total_parts,
                    caption=f"Uploading: {file_name}\n"
                            f"Progress: {i / total_parts * 100:.1f}%\n"
                            f"`{progress_bar}`"  # Use Markdown for the progress bar
                )

                # Update the progress bar
                progress = int((i + 1) / total_parts * progress_bar_length)
                progress_bar = "█" * progress + "░" * (progress_bar_length - progress)

    except Exception as e:
        logger.error(f"Error uploading large file to Telegram: {e}")
        bot.send_message(message.chat.id, "Error uploading the file to Telegram.")


def progress_callback(chat_id, progress_bar):
    """Callback function for updating the progress bar in Telegram."""
    def inner(current, total):
        progress_bar.update(current - progress_bar.n)
        # Update progress in Telegram (every 10%)
        if progress_bar.n % (total // 10) == 0:
            try:
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=user_data[chat_id]['progress_message_id'],
                    caption=f"Uploading: {progress_bar.desc}\n"
                            f"Progress: {progress_bar.n / total * 100:.1f}%"
                )
            except telebot.apihelper.ApiException as e:
                if 'retry_after' in e.result_json:
                    time.sleep(e.result_json['retry_after'])
                    # Retry the update
                    bot.edit_message_caption(
                        chat_id=chat_id,
                        message_id=user_data[chat_id]['progress_message_id'],
                        caption=f"Uploading: {progress_bar.desc}\n"
                                f"Progress: {progress_bar.n / total * 100:.1f}%"
                    )
                else:
                    raise e  # Re-raise the exception if it's not a FloodWait
    return inner


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


def process_file_upload(message, custom_file_name=None):
    """Downloads and uploads the file."""
    try:
        url = user_data[message.chat.id]['url']
        file_size = user_data[message.chat.id]['file_size']
        original_file_name = user_data[message.chat.id]['file_name']

        if custom_file_name is None:
            file_name = original_file_name
        else:
            file_name = custom_file_name

        # Send a message with a progress bar
        progress_message = bot.send_message(message.chat.id, "Downloading...")
        user_data[message.chat.id]['progress_message_id'] = progress_message.message_id

        # Download the file
        downloaded_file = download_file(url, file_name, message)

        if downloaded_file:
            # Upload the file to Telegram (handle large files)
            if file_size > 50 * 1024 * 1024:  # If file size is greater than 50MB
                upload_large_file_to_telegram(downloaded_file, message)
            else:
                # Use regular upload for smaller files
                with open(downloaded_file, 'rb') as f:
                    bot.send_chat_action(message.chat.id, 'upload_document')
                    bot.send_document(
                        chat_id=message.chat.id,
                        document=f,
                        caption=f"Uploaded {file_name} ({file_size_str(file_size)})"
                    )

            # Remove the downloaded file after uploading
            os.remove(downloaded_file)

    except Exception as e:
        logger.error(f"Error in process_file_upload: {e}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
        
