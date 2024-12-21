import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import requests

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Function to search for movies on TMDB
def search_movie(query, api_key):
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": query}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return None


# Function to get movie details from TMDB
def get_movie_details(movie_id, api_key):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a movie name to search for."
    )


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text
    tmdb_api_key = os.getenv("TMDB_API_KEY")

    if not movie_name or not tmdb_api_key:
        await update.message.reply_text("Please Enter the Movie name or Bot not configured yet !")
        return

    search_results = search_movie(movie_name, tmdb_api_key)

    if search_results:
        keyboard = [
            [
                InlineKeyboardButton(
                    movie["title"], callback_data=f"movie_id_{movie['id']}"
                )
            ]
            for movie in search_results[:5]  # Limit to 5 results
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Select a movie from the list:", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("No movies found with that name.")


async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    if callback_data.startswith("movie_id_"):
        movie_id = callback_data.split("_")[-1]
        tmdb_api_key = os.getenv("TMDB_API_KEY")

        movie_details = get_movie_details(movie_id, tmdb_api_key)

        if movie_details:
            movie_title = movie_details["title"]
            tmdb_id = movie_details["id"]
            poster_path = movie_details["poster_path"]
            poster_url = (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path
                else "No poster available"
            )
            response_message = (
                f"Title: {movie_title}\n"
                f"TMDB ID: {tmdb_id}\n"
                f"Poster: {poster_url}"
            )
            await query.edit_message_text(response_message)
        else:
            await query.edit_message_text("Failed to fetch movie details.")


def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        print("Please set the TELEGRAM_BOT_TOKEN in the .env file.")
        return

    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    app.add_handler(CallbackQueryHandler(handle_button_click))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
