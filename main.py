from flask import Flask, jsonify, request, render_template
from pyrogram import Client, filters
import sqlite3
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

# Telegram Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

bot = Client("custom_blog_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# SQLite setup
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


# Bot Command: Post a blog entry
@bot.on_message(filters.command("post") & filters.private)
async def post_blog(client, message):
    """Handles the /post command to add a new blog."""
    try:
        if len(message.command) < 3:
            await message.reply_text("Usage: /post <title> <content>\n\nExample: /post My First Blog This is the blog content.")
            return

        # Extract title and content
        title = message.command[1]
        content = " ".join(message.command[2:])
        logger.info(f"Adding blog post: Title='{title}', Content='{content[:30]}...'")

        # Save the blog post
        add_blog(title, content)
        await message.reply_text(f"Blog post added successfully!\n\n**Title**: {title}")
    except Exception as e:
        logger.error(f"Error in post_blog: {e}", exc_info=True)
        await message.reply_text("An error occurred while adding the blog post.")


# Bot Command: List all blogs
@bot.on_message(filters.command("list") & filters.private)
async def list_blogs(client, message):
    """Handles the /list command to list all blog posts."""
    try:
        blogs = get_all_blogs()
        if not blogs:
            await message.reply_text("No blog posts found.")
            return

        blog_list = "\n\n".join([f"{blog[0]}. **{blog[1]}**\n{blog[2][:50]}..." for blog in blogs])
        await message.reply_text(f"Blog Posts:\n\n{blog_list}")
    except Exception as e:
        logger.error(f"Error in list_blogs: {e}", exc_info=True)
        await message.reply_text("An error occurred while listing the blog posts.")


# Flask Endpoint: Get all blogs (API)
@app.route("/blogs", methods=["GET"])
def api_get_blogs():
    """API endpoint to retrieve all blogs."""
    blogs = get_all_blogs()
    return jsonify([{"id": blog[0], "title": blog[1], "content": blog[2]} for blog in blogs])


# Flask Endpoint: Render all blogs as HTML
@app.route("/")
def render_blogs():
    """Render all blogs in an HTML template."""
    blogs = get_all_blogs()
    return render_template("blogs.html", blogs=blogs)


# Start the Flask app in a separate thread
def run_flask():
    logger.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=8080)


# Start the bot in its own thread
def run_bot():
    try:
        logger.info("Starting the Pyrogram bot...")
        bot.start()
        logger.info("Bot has started successfully. Listening for commands...")

        # Keep the bot running
        bot.idle()
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")


# HTML Template for blogs
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
