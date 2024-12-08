import os
import logging
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Your API key and bot token
API_KEY = 'AIzaSyDV5u4do3xDEPXStyhn6_-LoZddDYOYP5o'  # You can remove this if not using public API
BOT_TOKEN = '7994627923:AAHngHVsK2VS4eWZ9CJ6hzv-1cwz8x-eisc'
BLOG_ID = '737863940949257967'  # Replace with your actual Blog ID

# Define the scope for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Telegram bot setup
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Setting up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to authenticate the user using OAuth 2.0
def authenticate_blogger():
    creds = None
    # The token.json stores the user's access and refresh tokens
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

    service = build('blogger', 'v3', credentials=creds)
    return service

# Function to create a new blog post
def create_blogger_post(title, content):
    try:
        service = authenticate_blogger()
        posts = service.posts()
        new_post = {
            'title': title,
            'content': content,
        }
        # Insert new post
        post = posts.insert(blogId=BLOG_ID, body=new_post).execute()
        return f"Post created successfully! Title: {post['title']}"
    except Exception as e:
        return f"An error occurred: {e}"

# Function to handle /start command
def start(update, context):
    update.message.reply_text("Welcome to Blogger Bot! Use /createpost to create a blog post.")

# Function to handle /createpost command
def create_post(update, context):
    try:
        title = ' '.join(context.args[:1])  # Get the title of the post
        content = ' '.join(context.args[1:])  # Get the content of the post

        if not title or not content:
            update.message.reply_text("Please provide both title and content for the post.")
            return

        result = create_blogger_post(title, content)
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# Adding handlers to the dispatcher
start_handler = CommandHandler('start', start)
create_post_handler = CommandHandler('createpost', create_post)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(create_post_handler)

# Start the bot
updater.start_polling()
