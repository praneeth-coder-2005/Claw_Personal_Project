import datetime
import logging
import os
import time
from io import BytesIO

import requests
import telebot

# --- Configuration ---

BOT_TOKEN = '7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk'  # Replace with your actual bot token
OMDB_API_KEY = "a3b61eaa"  # Replace with your actual OMDb API key

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
        # ... (Extract and format movie details as before) ...
        return movie_info
    else:
        return "Error fetching movie data or movie not found."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    # ... (Implementation is the same as before) ...


def search_movies(movie_name):
    """Searches for movies with similar names using OMDb API."""
    # ... (Implementation is the same as before) ...


def get_current_time():
    """Returns the current time as a formatted string."""
    # ... (Implementation is the same as before) ...


def get_current_date():
    """Returns the current date as a formatted string."""
    # ... (Implementation is the same as before) ...


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
                                    # ... (same as before) ...
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
            # ... (Implementation is the same as before) ...

    except Exception as e:
        logger.error(f"Error uploading large file to Telegram: {e}")
        bot.send_message(message.chat.id, "Error uploading the file to Telegram.")


def progress_callback(chat_id, progress_bar):
    """Callback function for updating the progress bar in Telegram."""
    # ... (Implementation is the same as before) ...


def file_size_str(file_size):
    """Converts file size to human-readable string."""
    # ... (Implementation is the same as before) ...


# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    # ... (Implementation is the same as before) ...


# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handles inline button callbacks."""
    # ... (Implementation is the same as before) ...


# --- Message Handlers ---

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    # ... (Implementation is the same as before) ...


def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    # ... (Implementation is the same as before) ...


def process_url_upload(message):
    """Handles the URL upload request."""
    # ... (Implementation is the same as before) ...


def process_rename(message):
    """Handles the file renaming."""
    # ... (Implementation is the same as before) ...


def process_file_upload(message, custom_file_name=None):
    """Downloads and uploads the file."""
    # ... (Implementation is the same as before) ...


# --- Start the Bot ---

if __name__ == '__main__':
    bot.infinity_polling()
    
