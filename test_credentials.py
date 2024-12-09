import json
import logging
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Replace with your actual bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace with your actual blog ID
blog_id = "737863940949257967"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# Path to your client credentials JSON file
CREDENTIALS_FILE = "credentials.json"  # Replace with the actual file name

def authenticate():
    """Authenticates with the Blogger API and returns the service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("blogger", "v3", credentials=creds)

blogger = authenticate()  # Authenticate at the start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "Hello! Send me the command /editpost followed by the PostId, Title, and Content to edit a post."
    )

async def edit_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edits an existing post on the blog."""
    try:
        # ... (rest of your edit_post function)
    except Exception as e:
        logger.error(f"Error editing post: {e}")
        await update.message.reply_text("Error editing post.")

def main():
    """Starts the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("editpost", edit_post))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
                    
