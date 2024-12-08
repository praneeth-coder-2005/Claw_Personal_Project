from pyrogram import Client, filters
from googleapiclient.discovery import build

# Configuration
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"
API_ID = 123456  # Replace with your Pyrogram API ID
API_HASH = "your_api_hash"  # Replace with your Pyrogram API hash
BLOGGER_API_KEY = "AIzaSyDV5u4do3xDEPXStyhn6_-LoZddDYOYP5o"
BLOG_ID = "737863940949257967"

# Initialize Pyrogram Bot
app = Client("blogger_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Initialize Blogger API
blogger_service = build("blogger", "v3", developerKey=BLOGGER_API_KEY)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("Welcome to the Blogger Editor Bot! Use /newpost to create a new post.")

@app.on_message(filters.command("newpost"))
async def new_post(client, message):
    # Request title and content
    await message.reply("Send me the title of the blog post:")
    title_message = await app.listen(message.chat.id)  # Wait for user's reply
    title = title_message.text

    await message.reply("Now send me the content of the blog post:")
    content_message = await app.listen(message.chat.id)  # Wait for user's reply
    content = content_message.text

    # Add post to Blogger
    try:
        new_post = {
            "title": title,
            "content": content,
        }
        result = blogger_service.posts().insert(blogId=BLOG_ID, body=new_post).execute()
        post_url = result.get("url")
        await message.reply(f"Post published successfully! View it here: {post_url}")
    except Exception as e:
        await message.reply(f"Failed to publish post: {str(e)}")

# Run the bot
app.run()
