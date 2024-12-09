import logging
import os
import pickle
from webbrowser import open_new

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
blog_id = "YOUR_BLOG_ID"  # Replace with your actual blog ID

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
            auth_url, _ = flow.authorization_url(prompt='consent')
            open_new(auth_url)  # Open the authorization URL in a new browser window
            authorization_response = input(
                "Enter the authorization response URL: "
            )
            flow.fetch_token(authorization_response=authorization_response)
            creds = flow.credentials
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
        # Parse the command arguments
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Please provide the PostId, Title, and Content."
            )
            return

        post_id, title, content = args[0], args[1], " ".join(args[2:])

        # Get the existing post
        post = blogger.posts().get(blogId=blog_id, postId=post_id).execute()

        # Update the title and content
        post["title"] = title
        post["content"] = content

        # Update the post using the Blogger API
        blogger.posts().update(blogId=blog_id, postId=post_id, body=post).execute()
        await update.message.reply_text(f"Post updated with title: {title}")

    except RefreshError as e:
        logger.error(f"Error editing post: {e}")
        await update.message.reply_text(
            "Invalid JWT Signature. Please check your service account key."
        )

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
    
