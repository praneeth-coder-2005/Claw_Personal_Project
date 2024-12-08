from flask import Flask, jsonify, request
from pyrogram import Client, filters
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Telegram Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

bot = Client("custom_blog_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Storage file for blog posts
BLOG_FILE = "blogs.json"

# Ensure storage exists
if not os.path.exists(BLOG_FILE):
    with open(BLOG_FILE, "w") as f:
        json.dump([], f)


def load_blogs():
    """Load blogs from the storage."""
    with open(BLOG_FILE, "r") as f:
        return json.load(f)


def save_blogs(blogs):
    """Save blogs to the storage."""
    with open(BLOG_FILE, "w") as f:
        json.dump(blogs, f, indent=4)


@bot.on_message(filters.command("post") & filters.private)
async def post_blog(client, message):
    """Handles the /post command to add a new blog post."""
    try:
        if len(message.command) < 3:
            await message.reply_text("Usage: /post <title> <content>")
            return

        title = message.command[1]
        content = " ".join(message.command[2:])
        logger.info(f"Received post: Title='{title}' Content='{content[:30]}...'")

        # Save blog
        blogs = load_blogs()
        blogs.append({"title": title, "content": content})
        save_blogs(blogs)

        await message.reply_text(f"Blog post added! Total posts: {len(blogs)}")
    except Exception as e:
        logger.error(f"Error posting blog: {e}")
        await message.reply_text("Failed to add the post. Check logs.")


@bot.on_message(filters.command("list") & filters.private)
async def list_blogs(client, message):
    """Handles the /list command to show all blog posts."""
    try:
        blogs = load_blogs()
        if not blogs:
            await message.reply_text("No blogs found.")
            return

        blog_list = "\n\n".join(
            [f"{idx+1}. **{blog['title']}**\n{blog['content'][:50]}..." for idx, blog in enumerate(blogs)]
        )
        await message.reply_text(f"Blogs:\n\n{blog_list}")
    except Exception as e:
        logger.error(f"Error listing blogs: {e}")
        await message.reply_text("Failed to list the posts. Check logs.")


@app.route("/")
def index():
    """API to check Flask is running."""
    return "Custom Blog Bot is running!"


@app.route("/blogs", methods=["GET"])
def get_blogs():
    """API to fetch all blogs."""
    blogs = load_blogs()
    return jsonify(blogs)


if __name__ == "__main__":
    # Start Flask app
    app.run(host="0.0.0.0", port=8080)
