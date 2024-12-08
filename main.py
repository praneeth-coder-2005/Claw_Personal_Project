from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from googleapiclient.discovery import build

# Replace with your actual credentials
API_KEY = "AIzaSyDV5u4do3xDEPXStyhn6_-LoZddDYOYP5o"
TELEGRAM_BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"
BLOG_ID = "737863940949257967"

# Initialize the Blogger API service
blogger_service = build('blogger', 'v3', developerKey=API_KEY)

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Blogger Editor Bot!\n"
        "To create a post, use the command:\n"
        "/post <title> <content>"
    )

# Create a post handler
def post(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /post <title> <content>")
        return

    # Extract title and content
    title = args[0]
    content = " ".join(args[1:])

    try:
        # Create and publish a blog post
        post_body = {
            "title": title,
            "content": content
        }
        post = blogger_service.posts().insert(blogId=BLOG_ID, body=post_body, isDraft=False).execute()

        # Send the post URL to the user
        update.message.reply_text(f"Post published successfully! View it here: {post['url']}")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Main function
def main():
    # Create the Updater and pass it the bot token
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Register the command handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("post", post))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
