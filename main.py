from flask import Flask, jsonify, request
from pyrogram import Client, filters
import os
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Initialize Pyrogram Client
bot = Client("custom_blog_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


# Bot Command: Post a blog entry
@bot.on_message(filters.command("post") & filters.private)
async def post_blog(client, message):
    try:
        if len(message.command) < 3:
            await message.reply_text("Usage: /post <title> <content>")
            return

        title = message.command[1]
        content = " ".join(message.command[2:])

        logger.info(f"Received post command: Title='{title}', Content='{content[:30]}...'")

        # Save blog logic here (or forward to Blogger API if needed)
        await message.reply_text(f"Blog post added with title: {title}")
    except Exception as e:
        logger.error(f"Error in post_blog: {e}")
        await message.reply_text("An error occurred while adding the blog post.")


# Flask Endpoint: Health Check
@app.route("/")
def index():
    logger.info("Health check endpoint accessed.")
    return "Custom Blog Bot is running!"


# Start the Flask app in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=8080)


# Start the bot in its own thread
def run_bot():
    try:
        logger.info("Starting the Pyrogram bot...")
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")


if __name__ == "__main__":
    # Use threading to run Flask and the bot concurrently
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run the bot (this blocks the main thread)
    run_bot()
