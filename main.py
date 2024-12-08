import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import sys

# Set up logging for debugging purposes
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
BOT_TOKEN = "7994627923:AAHngHVsK2VS4eWZ9CJ6hzv-1cwz8x-eisc"

# Blogger API credentials and setup
SCOPES = ['https://www.googleapis.com/auth/blogger']
CLIENT_SECRET_PATH = 'client_secret.json'  # path to your OAuth2 client secret JSON

# Set up Blogger API
def get_blogger_service():
    try:
        if not os.path.exists(CLIENT_SECRET_PATH):
            raise FileNotFoundError(f"Client secret file not found at {CLIENT_SECRET_PATH}")
        credentials = Credentials.from_service_account_file(CLIENT_SECRET_PATH, scopes=SCOPES)
        service = build('blogger', 'v3', credentials=credentials)
        logger.info("Blogger service successfully created.")
        return service
    except Exception as e:
        logger.error(f"Error creating Blogger service: {e}")
        sys.exit(1)

# Fetch blog posts
def get_blog_posts(blog_id):
    try:
        service = get_blogger_service()
        posts = service.posts().list(blogId=blog_id).execute()
        if 'items' in posts:
            logger.info(f"Found {len(posts['items'])} posts.")
            return posts['items']
        else:
            logger.warning("No posts found.")
            return []
    except Exception as e:
        logger.error(f"Error fetching blog posts: {e}")
        return []

# Command handler for /start
async def start(update: Update, context):
    try:
        await update.message.reply_text('Hello! I am your Blogger Telegram Bot. You can edit blog posts using me.')
    except Exception as e:
        logger.error(f"Error in /start command: {e}")

# Command handler for viewing blog posts
async def view_posts(update: Update, context):
    try:
        blog_id = "737863940949257967"  # Blog ID provided by you
        posts = get_blog_posts(blog_id)

        if posts:
            post_list = "\n".join([f"{post['title']}" for post in posts])
            await update.message.reply_text(f"Here are your blog posts:\n{post_list}")
        else:
            await update.message.reply_text("No blog posts found.")
    except Exception as e:
        logger.error(f"Error in /view_posts command: {e}")

# Command handler for editing a post
async def edit_post(update: Update, context):
    try:
        if context.args:
            post_title = " ".join(context.args)  # Join the arguments to form the post title
            blog_id = "737863940949257967"  # Blog ID provided by you
            
            # Fetch the blog posts
            posts = get_blog_posts(blog_id)
            
            for post in posts:
                if post['title'].lower() == post_title.lower():
                    await update.message.reply_text(f"Found post: {post['title']}. Please send the new content.")
                    # Store post data in context for later
                    context.user_data['post_to_edit'] = post
                    return
            await update.message.reply_text("Post not found. Please check the title and try again.")
        else:
            await update.message.reply_text("Please provide the title of the post you want to edit.")
    except Exception as e:
        logger.error(f"Error in /edit command: {e}")

# Message handler for receiving new content to update the post
async def handle_message(update: Update, context):
    try:
        if 'post_to_edit' in context.user_data:
            post = context.user_data['post_to_edit']
            new_content = update.message.text

            # Update the post with new content
            service = get_blogger_service()
            updated_post = service.posts().update(
                blogId="737863940949257967",  # Blog ID provided by you
                postId=post['id'],
                body={'content': new_content}
            ).execute()

            await update.message.reply_text(f"Post '{post['title']}' updated successfully!")
            del context.user_data['post_to_edit']  # Clear the post edit context
        else:
            await update.message.reply_text("You need to start an edit by using /edit <post_title>.")
    except Exception as e:
        logger.error(f"Error in handling message: {e}")
        await update.message.reply_text("An error occurred while updating the post.")

async def main():
    try:
        # Create an Application object with your bot's token
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handler for /start
        application.add_handler(CommandHandler("start", start))

        # Add command handler for viewing blog posts
        application.add_handler(CommandHandler("view_posts", view_posts))

        # Add command handler for editing a post
        application.add_handler(CommandHandler("edit", edit_post))

        # Add message handler for receiving new content for posts
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Start polling for updates from Telegram
        await application.run_polling()
    
    except Exception as e:
        logger.error(f"Error during bot execution: {e}")
        sys.exit(1)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
