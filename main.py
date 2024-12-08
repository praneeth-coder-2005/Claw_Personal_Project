import logging
import telegram
from google.oauth2 import service_account
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio

# Set up the bot token (replace with your bot token)
BOT_TOKEN = '7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M'

# Set the path to the service account file (service.json)
SERVICE_ACCOUNT_FILE = 'service.json'

# Set the required scopes for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Set up logging to capture detailed logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Change from INFO to DEBUG for more detailed logs
)
logger = logging.getLogger(__name__)

# Command handler to fetch blogs
async def get_blogs(update: Update, context: CallbackContext) -> None:
    try:
        logger.debug("Fetching blogs...")

        # Fetch blogs for the authenticated user
        request = service.blogs().listByUser(userId='self')
        response = request.execute()

        # Extract blog titles from the response
        blogs = response.get('items', [])
        if blogs:
            blog_titles = [blog['name'] for blog in blogs]
            message = "Your Blogs:\n" + "\n".join(blog_titles)
        else:
            message = "No blogs found for this account."
        
        # Send the list of blogs as a message to the user
        await update.message.reply_text(message)
        logger.debug("Blogs sent to user.")

    except Exception as e:
        logger.error(f"Error while fetching blogs: {e}")
        await update.message.reply_text("An error occurred while fetching blogs.")
        logger.exception("Exception traceback:")

# Main function to start the bot
async def main() -> None:
    try:
        logger.info("Starting the bot...")

        # Create the Application and pass it your bot's token
        application = Application.builder().token(BOT_TOKEN).build()

        # Register the /blogs command handler
        application.add_handler(CommandHandler('blogs', get_blogs))

        # Start the Bot with polling
        logger.info("Bot started successfully, running polling...")
        await application.run_polling()

    except Exception as e:
        logger.error(f"An error occurred while starting the bot: {e}")
        logger.exception("Exception traceback:")

if __name__ == '__main__':
    try:
        logger.info("Initializing bot application...")
        
        # Simply run the bot using the `run_polling()` method directly
        asyncio.run(main())

    except Exception as e:
        logger.error(f"Fatal error during bot execution: {e}")
        logger.exception("Exception traceback:")
