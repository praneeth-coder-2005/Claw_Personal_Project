from pyrogram import Client, filters
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Telegram Bot API credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram bot token
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API hash

# Email credentials
SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
SMTP_PORT = 587  # Gmail SMTP port
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Sender email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Sender email password
BLOGGER_EMAIL = os.getenv("BLOGGER_EMAIL")  # Blogger's secret email address

# Initialize Telegram Bot
bot = Client("blogger_email_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


def send_email(subject, body):
    """Send an email to Blogger's secret email address."""
    try:
        # Create email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = BLOGGER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, BLOGGER_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {BLOGGER_EMAIL}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


@bot.on_message(filters.command("post") & filters.private)
async def post_blog(client, message):
    """Handle the /post command to create a blog post."""
    if len(message.command) < 3:
        await message.reply_text("Usage: /post <title> <content>\n\nExample: /post My Blog Title Blog content goes here.")
        return

    # Extract title and content
    title = message.command[1]
    content = " ".join(message.command[2:])
    print(f"Received post: Title='{title}', Content='{content[:30]}...'")

    # Send email to Blogger
    if send_email(title, content):
        await message.reply_text(f"Blog post
