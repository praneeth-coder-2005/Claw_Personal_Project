# utils.py
import datetime
import logging
import os
import time
from io import BytesIO

import requests
import telebot

from config import OMDB_API_KEY  # Import from config.py

# --- Logging ---
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# --- Global Variables ---
user_data = {}  # To store user-specific data during file upload

# --- Helper Functions ---


def _make_omdb_api_request(url):
    """Makes a request to the OMDb API and handles errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["Response"] == "True":
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
        fields = [
            "Title",
            "Year",
            "Rated",
            "Released",
            "Runtime",
            "Genre",
            "Director",
            "Writer",
            "Actors",
            "Plot",
            "Language",
            "Country",
            "Awards",
            "Poster",
            "imdbRating",
            "imdbVotes",
            "imdbID",
        ]
        movie_info = "\n".join([f"*{field}:* {data[field]}" for field in fields])
        return movie_info
    else:
        return "Error fetching movie data or movie not found."


def get_movie_rating(movie_name):
    """Fetches movie ratings from OMDb API."""
    base_url = "http://www.omdbapi.com/?"
    complete_url = f"{base_url}apikey={OMDB_API_KEY}&t={movie_name}"
    data = _make_omdb_api_request(complete_url)

    if data:
        ratings = data["Ratings"]
        rating_str = ""
        for rating in ratings:
            source = rating["Source"]
            value = rating["Value"]
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
        return data["Search"]
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
        file_size = int(response.headers.get("content-length", 0))
        return file_size
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting file size: {e}")
        return 0


def download_file(url, file_name, message):
    """Downloads the file from the URL with a progress bar (in Telegram)."""
    file_size = get_file_size(url)
    if file_size == 0:
        bot.send_message(message.chat.id, "Could not determine file size.")
        return None

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Send initial message with progress bar
        progress_message = bot.send_message(
            message.chat.id, f"Downloading: {file_name}\nProgress: 0.0%"
        )
        user_data[message.chat.id]["progress_message_id"] = (
            progress_message.message_id
        )

        with open(file_name, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Update progress in Telegram (every 10%)
                    if downloaded % (file_size // 10) == 0:
                        try:
                            bot.edit_message_text(
                                chat_id=message.chat.id,
                                message_id=progress_message.message_id,
                                text=f"Downloading: {file_name}\nProgress: {downloaded / file_size * 100:.1f}%",
                            )
                        except telebot.apihelper.ApiException as e:
                            if "retry_after" in e.result_json:
                                time.sleep(e.result_json["retry_after"])
                                # Retry the update
                                bot.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=progress_message.message_id,
                                    text=f"Downloading: {file_name}\nProgress: {downloaded / file_size * 100:.1f}%",
                                )
                            else:
                                raise e

        # Final update to the progress bar
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=progress_message.message_id,
            text=f"Downloaded: {file_name}\nProgress: 100.0%",
        )
        return file_name

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file: {e}")
        bot.send_message(message.chat.id, f"Error downloading the file: {e}")
        return None


def upload_large_file_to_telegram(file_name, message):
    """Uploads large files to Telegram by splitting into smaller parts."""
    try:
        with open(file_name, "rb") as f:
            file_size = os.path.getsize(file_name)

            # Send initial message
            bot.send_message(message.chat.id, f"Uploading {file_name}...")

            part_size = 50 * 1024 * 1024  # 50MB chunks
            parts = range(0, file_size, part_size)
            total_parts = len(parts)

            for i, part in enumerate(parts):
                file_part = BytesIO(f.read(part_size))
                bot.send_chat_action(message.chat.id, "upload_document")

                # Send the file part with caption
                bot.send_document(
                    message.chat.id,
                    file_part,
                    visible_file_name=f"{os.path.splitext(file_name)[0]}.part{i+1}{os.path.splitext(file_name)[1]}",  # Add part number to file name
                    caption=f"Uploading: {file_name}\nPart {i+1}/{total_parts}",
                )

    except Exception as e:
        logger.error(f"Error uploading large file to Telegram: {e}")
        bot.send_message(
            message.chat.id, f"Error uploading the file to Telegram: {e}"
        )


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


def process_url_upload(message):
    """Handles the URL upload request."""
    try:
        url = message.text.strip()
        file_name = os.path.basename(url)
        file_size = get_file_size(url)

        if file_size == 0:
            bot.send_message(
                message.chat.id, "Invalid URL or unable to get file size."
            )
            return

        # Extract original file name and extension
        original_file_name, original_file_ext = os.path.splitext(file_name)

        # Show options for renaming or using the default name
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("Default", callback_data="default"),
            telebot.types.InlineKeyboardButton("Rename", callback_data="rename"),
        )

        bot.send_message(
            message.chat.id,
            f"File: {original_file_name}{original_file_ext}\n"
            f"Size: {file_size_str(file_size)}\n"
            f"Choose an option:",
            reply_markup=markup,
        )

        # Store user data for later use
        user_data[message.chat.id] = {
            "url": url,
            "file_name": file_name,
            "file_size": file_size,
        }

    except Exception as e:
        logger.error(f"Error in process_url_upload: {e}")
        bot.send_message(
            message.chat.id, "Oops! Something went wrong. Please try again later."
        )


def process_rename(message):
    """Handles the file renaming."""
    try:
        new_file_name = message.text.strip()

        # Get original file extension from user_data
        original_file_ext = os.path.splitext(
            user_data[message.chat.id]["file_name"]
        )[1]

        # Combine new file name with original extension
        custom_file_name = f"{new_file_name}{original_file_ext}"

        process_file_upload(message, custom_file_name)

    except Exception as e:
        logger.error(f"Error in process_rename: {e}")
        bot.send_message(
            message.chat.id, "Oops! Something went wrong. Please try again later."
        )


def process_file_upload(message, custom_file_name=None):
    """Downloads and uploads the file."""
    try:
        url = user_data[message.chat.id]["url"]
        file_size = user_data[message.chat.id]["file_size"]
        original_file_name = user_data[message.chat.id]["file_name"]

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
                    with open(downloaded_file, "rb") as f:
                        bot.send_chat_action(message.chat.id, "upload_document")
                        bot.send_document(
                            chat_id=message.chat.id,
                            document=f,  # Use 'document' instead of 'file_id'
                            caption=f"Uploaded {file_name} ({file_size_str(file_size)})",
                        )

                # Remove the downloaded file after uploading (only if upload was successful)
                os.remove(downloaded_file)

            except Exception as e:
                logger.error(f"Error uploading the file to Telegram: {e}")
                bot.send_message(
                    message.chat.id, f"Error uploading the file to Telegram: {e}"
                )

    except Exception as e:
        logger.error(f"Error in process_file_upload: {e}")
        bot.send_message(
            message.chat.id, "Oops! Something went wrong. Please try again later."
        )
        
