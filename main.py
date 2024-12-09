import datetime
import logging
import os
import re
import time
from io import BytesIO

import requests
import telebot
from tqdm import tqdm

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

# ... (Other helper functions: _make_omdb_api_request, get_movie_details,
#      get_movie_rating, search_movies, get_current_time, get_current_date) ...


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

        # Create a progress bar
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name, ascii=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
                    progress_bar.update(len(chunk))
                    # Update progress in Telegram (every 10%)
                    if progress_bar.n % (file_size // 10) == 0:
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=user_data[message.chat.id]['progress_message_id'],
                            text=f"Downloading: {file_name}\n"
                                 f"Progress: {progress_bar.n / file_size * 100:.1f}%"
                        )
        progress_bar.close()
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

            # Create a progress bar
            progress_bar = tqdm(total=total_parts, unit='parts', desc=file_name, ascii=True)

            for i, part in enumerate(parts):
                file_part = BytesIO(f.read(part_size))
                bot.send_chat_action(message.chat.id, 'upload_document')
                uploaded_part = bot.upload.saveBigFilePart(
                    file_id=message.chat.id,  # Use chat ID as a unique identifier
                    file_part=i,
                    file_total_parts=total_parts,
                    bytes=file_part
                )
                # Update progress bar and Telegram message
                progress_bar.update(1)
                if progress_bar.n % (total_parts // 10) == 0:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=user_data[message.chat.id]['progress_message_id'],
                        text=f"Uploading: {file_name}\n"
                             f"Progress: {progress_bar.n / total_parts * 100:.1f}%"
                    )
            progress_bar.close()

            # Send the final file
            bot.send_document(
                chat_id=message.chat.id,
                document=message.chat.id,  # Use chat ID as file_id
                caption=f"Uploaded {file_name} ({file_size_str(file_size)})"
            )

    except Exception as e:
        logger.error(f"Error uploading large file to Telegram: {e}")
        bot.send_message(message.chat.id, "Error uploading the file to Telegram.")


def progress_callback(chat_id, progress_bar):
    """Callback function for updating the progress bar in Telegram."""
    def inner(current, total):
        # ... (same as before) ...
    return inner


def file_size_str(file_size):
    """Converts file size to human-readable string."""
    # ... (same as before) ...


# --- Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    # ... (same as before) ...


# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handles inline button callbacks."""
    # ... (same as before) ...


# --- Message Handlers ---

def process_movie_request(message):
    """Processes the movie title and sends movie details or shows options."""
    # ... (same as before) ...


def process_movie_rating_request(message):
    """Processes the movie title and sends movie ratings."""
    # ... (same as before) ...


def process_url_upload(message):
    """Handles the URL upload request."""
    # ... (same as before) ...


def process_rename(message):
    """Handles the file renaming."""
    # ... (same as before) ...


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
    
