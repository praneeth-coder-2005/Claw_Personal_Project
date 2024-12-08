from pyrogram import Client, filters
import requests
from flask import Flask

# Replace these values with your API credentials and bot token
API_ID = 28293429  # Your API ID
API_HASH = "903eb1cc5328d00cb92f872d9d66c2c2"  # Your API Hash
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"  # Your Bot Token
BLOG_ID = "737863940949257967"  # Your Blogger Blog ID
API_KEY = "AIzaSyDV5u4do3xDEPXStyhn6_-LoZddDYOYP5o"  # Your Blogger API Key

# Initialize the Pyrogram Client with the provided credentials
app = Client(
    "blogger_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Initialize Flask app for health check
flask_app = Flask(__name__)

# Health check endpoint
@flask_app.route('/ping')
def ping():
    return "OK", 200

# Function to post a new blog article
def post_blog(title, content):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "title": title,
        "content": content
    }

    # Send POST request to Blogger API to create a new post
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return "Blog post published successfully!"
    else:
        return f"Error publishing blog post: {response.status_code}"

# Handle "/start" command
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! I'm your Blogger bot. Use /help to see available commands.")

# Handle "/help" command
@app.on_message(filters.command("help"))
def help(client, message):
    message.reply_text("""
I can help you with the following commands:

- /start: Welcome message
- /create_post <title> <content>: Create a new blog post with a title and content
    """)

# Handle "/create_post" command to create a new blog post
@app.on_message(filters.command("create_post"))
def create_post(client, message):
    # Extract the title and content from the message
    try:
        text = message.text.split(maxsplit=2)
        if len(text) < 3:
            message.reply_text("Please provide a title and content for the post. Example: /create_post MyTitle MyContent")
            return

        title = text[1]
        content = text[2]

        # Call the post_blog function to publish the post
        result = post_blog(title, content)
        message.reply_text(result)
    except Exception as e:
        message.reply_text(f"An error occurred: {str(e)}")

# Run both Pyrogram and Flask
if __name__ == "__main__":
    from threading import Thread

    # Start Flask server for health checks
    def start_flask():
        flask_app.run(host='0.0.0.0', port=8000)

    # Run Flask in a separate thread
    thread = Thread(target=start_flask)
    thread.start()

    # Run the Pyrogram bot
    app.run()
