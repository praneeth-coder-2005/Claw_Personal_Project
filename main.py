from flask import Flask, jsonify, render_template
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import sqlite3
import os
import logging
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Environment Variables for Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Initialize Pyrogram Client with persistent session
bot = Client(
    "custom_blog_bot",  # Session file name
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="./"  # Ensures session file is saved in the current directory
)

# SQLite database file
DB_FILE = "blogs.db"


def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()


# Initialize the database
init_db()


def add_blog(title, content):
    """Add a new blog post to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blogs (title, content) VALUES (?, ?)", (title, content))
        conn.commit()


def get_all_blogs():
    """Retrieve all blog posts from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM blogs")
        return cursor.fetchall()


@bot.on_message(filters.command("post") & filters.private)
async def post_blog(client, message):
    """Handles the /post command to add a new blog post."""
    try:
        if len(message.command) < 3:
            await message.reply_text(
                "Usage: /post <title> <content>\n\nExample: /post My First Blog This is the blog content."
            )
            return

        # Extract title and content
        title = message.command[1]
        content = " ".join(message.command[2:])
        logger.info(f"Adding blog post: Title='{title}', Content='{content[:30]}...'")

        # Save the blog post to the database
        add_blog(title, content)
        await message.reply_text(f"Blog post added successfully!\n\n**Title**: {title}")
    except Exception as e:
        logger.error(f"Error in post_blog: {e}", exc_info=True)
        await message.reply_text("An error occurred while adding the blog post.")


@bot.on_message(filters.command("list") & filters.private)
async def list_blogs(client, message):
    """Handles the /list command to list all blog posts."""
    try:
        blogs = get_all_blogs()
        if not blogs:
            await message.reply_text("No blog posts found.")
            return

        blog_list = "\n\n".join(
            [f"{blog[0]}. **{blog[1]}**\n{blog[2][:50]}..." for blog in blogs]
        )
        await message.reply_text(f"Blog Posts:\n\n{blog_list}")
    except Exception as e:
        logger.error(f"Error in list_blogs: {e}", exc_info=True)
        await message.reply_text("An error occurred while listing the blog posts.")


@app.route("/")
def index():
    """Health check endpoint."""
    logger.info("Health check endpoint accessed.")
    return "Custom Blog Bot is running!"


@app.route("/blogs", methods=["GET"])
def api_get_blogs():
    """API endpoint to retrieve all blogs."""
    blogs = get_all_blogs()
    return jsonify([{"id": blog[0], "title": blog[1], "content": blog[2]} for blog in blogs])


@app.route("/render", methods=["GET"])
def render_blogs():
    """Render all blogs in an HTML template."""
    blogs = get_all_blogs()
    return render_template("blogs.html", blogs=blogs)


def run_flask():
    """Start the Flask app."""
    logger.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=8080)


def run_bot():
    """Start the Pyrogram bot with flood wait handling."""
    while True:
        try:
            logger.info("Starting the Pyrogram bot...")
            bot.run()  # Keeps the bot running indefinitely
        except FloodWait as e:
            logger.warning(f"Flood wait error: Waiting for {e.value} seconds before retrying...")
            time.sleep(e.value)  # Wait for the required time before retrying
        except Exception as e:
            logger.error(f"Failed to start the bot: {e}", exc_info=True)
            break  # Exit if an unknown error occurs


# HTML Template for Blogs
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Posts</title>
</head>
<body>
    <h1>Blog Posts</h1>
    <ul>
        {% for blog in blogs %}
        <li>
            <h2>{{ blog[1] }}</h2>
            <p>{{ blog[2] }}</p>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# Save the HTML template
os.makedirs("templates", exist_ok=True)
with open("templates/blogs.html", "w") as f:
    f.write(HTML_TEMPLATE)


if __name__ == "__main__":
    # Use threading to run Flask and the bot concurrently
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run the bot (this blocks the main thread)
    run_bot()
