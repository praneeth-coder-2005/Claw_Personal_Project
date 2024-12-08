import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle
import requests

# Set up logging to see detailed errors in logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variable to store user credentials for Google OAuth
creds = None

# Define the SCOPES for accessing Blogger
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Your Telegram bot token
TELEGRAM_BOT_TOKEN = '7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M'

# Function to authenticate with Google
def authenticate_google_account():
    """Authenticate and return the Blogger API service"""
    global creds
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('blogger', 'v3', credentials=creds)
        return service
    except HttpError as err:
        logger.error(f"An error occurred: {err}")
        return None

# Start command handler to initialize the bot and show welcome message
async def start(update: Update, context: CallbackContext):
    """Send a welcome message when the bot is started"""
    user = update.effective_user
    await update.message.reply_html(f"Hi {user.mention_html()}! I can help you edit and publish posts on your Blogger account.\nType /authenticate to get started.")

# Authenticate the user and connect to their Blogger account
async def authenticate(update: Update, context: CallbackContext):
    """Start the authentication process with Google and Blogger"""
    await update.message.reply_text("Redirecting to authenticate with Google. Please follow the instructions.")
    service = authenticate_google_account()
    if service:
        await update.message.reply_text("Authentication successful! You can now create and edit posts.")
        context.user_data['service'] = service
    else:
        await update.message.reply_text("Authentication failed. Try again later.")

# Handle posting new or edited posts
async def post_to_blogger(update: Update, context: CallbackContext):
    """Handles post creation and editing via bot commands"""
    service = context.user_data.get('service', None)
    if not service:
        await update.message.reply_text("You need to authenticate first. Use /authenticate.")
        return
    
    message = update.message.text[6:]  # Remove '/post ' from the message text
    if not message:
        await update.message.reply_text("Please provide the content for the post.")
        return
    
    blog_id = "your-blog-id"  # Replace with your Blogger's blog ID
    post_id = None

    try:
        # Check if there is an ongoing post edit or create a new one
        posts = service.posts().list(blogId=blog_id).execute()
        for post in posts.get('items', []):
            if post['title'] == "Draft Post":
                post_id = post['id']
                break

        if post_id:
            # Editing existing post
            post = service.posts().get(blogId=blog_id, postId=post_id).execute()
            post['content'] = message
            updated_post = service.posts().update(blogId=blog_id, postId=post_id, body=post).execute()
            await update.message.reply_text(f"Post updated: {updated_post['url']}")
        else:
            # Creating new post
            new_post = service.posts().insert(blogId=blog_id, body={
                'title': 'New Draft Post',
                'content': message
            }).execute()
            await update.message.reply_text(f"New post created: {new_post['url']}")

    except HttpError as error:
        await update.message.reply_text(f"An error occurred: {error}")

# Function to handle errors
async def error(update: Update, context: CallbackContext):
    """Log the error and notify the user"""
    logger.warning(f"Update {update} caused error {context.error}")
    await update.message.reply_text(f"An error occurred: {context.error}")

# Main function to set up the bot and handlers
def main():
    """Start the bot and set up the handlers"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("authenticate", authenticate))
    application.add_handler(CommandHandler("post", post_to_blogger))
    
    # Add message handler for other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, post_to_blogger))

    # Add error handler
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
