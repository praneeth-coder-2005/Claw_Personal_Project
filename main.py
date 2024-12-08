import os
import logging
import sqlite3
import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Environment Variables for Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "<your_bot_token>")
API_ID = int(os.getenv("API_ID", "<your_api_id>"))
API_HASH = os.getenv("API_HASH", "<your_api_hash>")

# Initialize Pyrogram Client with persistent session
bot = Client(
    "custom_blog_bot",  # Session file name
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# SQLite Database File
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
        # Check if the command has enough arguments
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


def main():
    """Run the bot with flood wait handling."""
    while True:
        try:
            logger.info("Starting the Pyrogram bot...")
            bot.run()  # Keeps the bot running indefinitely
        except FloodWait as e:
            logger.warning(f"Flood wait error: Waiting for {e.value} seconds before retrying...")
            time.sleep(e.value)  # Wait for the required time before retrying
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)
            break


if __name__ == "__main__":
    main()
