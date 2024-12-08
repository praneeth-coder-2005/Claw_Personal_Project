from flask import Flask, request
from pyrogram import Client, filters
from googleapiclient.discovery import build
import logging
import os  # To fetch environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Environment Variables for Secrets
BLOGGER_API_KEY = os.getenv("BLOGGER_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Blogger API setup
blogger_service = build("blogger", "v3", developerKey=BLOGGER_API_KEY)

# Telegram Bot setup
bot = Client("blogger_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


@bot.on_message(filters.command("post") & filters.private)
async def post_to_blogger(client, message):
    try:
        # Extract title and content
        if len(message.command) < 3:
            await message.reply_text("Usage: /post <title> <content>")
            return

        title = message.command[1]
        content = " ".join(message.command[2:])

        # Log the operation
        logger.info(f"Attempting to post: Title='{title}', Content='{content[:30]}...'")

        # Create the blog post
        post = blogger_service.posts().insert(
            blogId=BLOG_ID,
            body={"title": title, "content": content}
        ).execute()

        post_url = post.get("url")
        await message.reply_text(f"Post published successfully! [View Post]({post_url})", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error posting to Blogger: {e}")
        await message.reply_text("Failed to publish the post. Please check logs.")


@app.route("/")
def index():
    return "Blogger Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    try:
        bot.process_update(update)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return "OK", 200


if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=8080)
