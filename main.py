import logging
import telegram
from google.oauth2 import service_account
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Set up the bot token (replace with your bot token)
BOT_TOKEN = '7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M'

# Set the path to the service account file (service.json)
SERVICE_ACCOUNT_FILE = 'service.json'

# Set the required scopes for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Authenticate using the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Blogger API client
service = build('blogger', 'v3', credentials=credentials)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Command handler to fetch blogs
async def get_blogs(update: Update, context: CallbackContext) -> None:
    try:
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
    except Exception as e:
        logger.error(f"Error while fetching blogs: {e}")
        await update.message.reply_text("An error occurred while fetching blogs.")

# Main function to start the bot
async def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the /blogs command handler
    application.add_handler(CommandHandler('blogs', get_blogs))

    # Start the Bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
