import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for Blogger API
BLOGGER_API_KEY = 'AIzaSyDV5u4do3xDEPXStyhn6_-LoZddDYOYP5o'
BLOGGER_API_NAME = 'blogger'
BLOGGER_API_VERSION = 'v3'
BLOGGER_BLOG_ID = 'your_blog_id'  # Replace with your Blogger blog ID

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7994627923:AAHngHVsK2VS4eWZ9CJ6hzv-1cwz8x-eisc'

# Set up authentication for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate_blogger():
    """Authenticate and return the Blogger API service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created
    # automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build(BLOGGER_API_NAME, BLOGGER_API_VERSION, credentials=creds)
    return service

def start(update: Update, context: CallbackContext):
    """Handle /start command."""
    update.message.reply_text("Welcome! Use /newpost to create a new post.")

def new_post(update: Update, context: CallbackContext):
    """Handle /newpost command."""
    update.message.reply_text("Please send me the title of your new blog post.")

    # Wait for the title input
    return 'WAIT_FOR_TITLE'

def handle_message(update: Update, context: CallbackContext):
    """Handle messages from users."""
    user_message = update.message.text
    
    if 'WAIT_FOR_TITLE' in context.user_data:
        # Store the title of the post
        context.user_data['title'] = user_message
        update.message.reply_text("Now send me the content of your blog post.")
        context.user_data['state'] = 'WAIT_FOR_CONTENT'
    elif 'WAIT_FOR_CONTENT' in context.user_data:
        # Store the content of the post
        context.user_data['content'] = user_message
        # Create the post on Blogger
        create_blogger_post(context.user_data['title'], context.user_data['content'])
        update.message.reply_text("Your post has been published on Blogger!")
        del context.user_data  # Clear user data after post

def create_blogger_post(title, content):
    """Create a new post on Blogger."""
    service = authenticate_blogger()
    posts = service.posts()
    new_post = {
        'title': title,
        'content': content,
    }
    posts.insert(blogId=BLOGGER_BLOG_ID, body=new_post).execute()

def main():
    """Start the Telegram bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set up command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("newpost", new_post))

    # Set up message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
