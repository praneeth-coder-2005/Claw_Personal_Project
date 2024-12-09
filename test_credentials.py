import os
import json
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.exceptions import RefreshError

# Replace with your actual bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7704211647:AAGslX2jlqGpzeXbJlX61egbMHb8eotNxs4")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Service account key (updated with your provided key)
SERVICE_ACCOUNT_KEY = {
  "type": "service_account",
  "project_id": "blogger-test-441717",
  "private_key_id": "b5058d9596683941c93d5cafe9237198cd6b8869",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJrA93XyB71z+X\nWTS5HsrOZeZXAPaZqv1ym9MEJgWg8oxjWyU1gC0UkuNWsjWFpTm+C3j9EA5GoIrg\nHk0tzqKNEgQFCKtgV9Gxkk2BVQICMPMTddwI4IQQTtDBVtDwnNoVdanxlc0Em4H/\ncgOycPEtsSsPcwViYNTtV4+db1HAkSRdXaJ0HGS/uUiTR1lxjJc0PIrPsX6+Y99R\n6P7vMpRenr2Q43KZRSIztOZ8txSi377YmErIE9qQEmjcjekkbg/ldjTMR08AwUEA\njQYtRFf9l/waRyX+yALpSd9Vv0ktK+OwwY5Uukk6iMEKmB7DQ+L/KQQYobNO1pDY\nV3762S3XAgMBAAECggEAFLoFxud0b7XiF7x30jTLdCX94+A59/YeYTqJl+oOdwmm\niwmRi+uV9oDYM49SN9+QzSrhruSJCxIx47HJjdUoWKZK2neXIWo1J3JZW9rwP2hn\new8IY7Mrb3+iLdSt2aTNNxpmMmmKbhhLZoUBw0OfTepg+hAAtCkuiQwQOwZ3WPqD\nDAxbl/vk7SyR8DonyWnMQInMbvp3FcGV35SybjHS+c3hwmRuBzanX+l3dz/eAUVB\nRYBBsdbfwMvtW9tAjbuRVz7qQLSuulFlOtOZvRHLuv6pVTWK8gzi4Jik+GtJqm3H\nSOtnnXUShFN6MTicNjNGIMXhaxWfbuP+sJaOati1gQKBgQDsVXBzvUolhpnOoxwL\nYzRFErx2uTl927KBOeXxMeqc9IPqiOjNsQzROysEfb05M2rDkzooFFe+TNjqgbvD\nCwgWa41XzFuQAsfunY1mJT524hGlgSV7msRb7KMJVU836ATKzwy8qQr7NGcrgB9N\nXD3kPScrPduYtfTjLzAjfHXpVwKBgQDadDuRVK+p2czTF7ZkoUKS/zwLxchUfmdE\nUX7mojqjabEuDIOIDc10ZDN6K4vVpyqKxx/fKLNTv0ZCGhvZUxH5mOoA6YlxJw4v\nqIoywMuj7FyJV9u07yqYAznnWYllctvkHqAQyZbxYmUQ3jDt4JdXtni6PaYjjCbZ\nXcZ+sUGPgQKBgB/Yd3mxFQ+vboRQqFPEf2ObXbflx6B0/T26joiMwF9791agMjad\nV+vNvEMzqk7N5eIKsbh63UPBWP5okuN6VhGnVnlxORlTtpspsccE18DvP498so9Q\nUItOfL2iODWBVzv44G9/m9Izwn8zGYS0HEboEqIaCMAwLJp8XlE50S2rAoGAIhKr\nD9nzpDxydCJosn1sktz4kqWAv50PolpLvtFi8AYWOqZ9BYWRnCvc05tjLinqusag\nNAB3KALXhIvp+BW64gF1zjqe02VSEyDonU3w9VpyfIGVpT0AmcE3ENyoT4iAv63/\nLV8kCfZc6Sqe2xuCv42YewQOm9DKZnD3+t7O6QECgYEAw6MxYmlDLx+7XgX19HLy\nivrp2quA+00f1JjIK026BcC5jKxxfPGfpwQpdKd5LYhkAveA4kNhfNh4eOOYKmi3\nthutsRyD5b4AaT+uTiHz4Eq82p7cO0Hq813dfgP7UIh6DKqm502H32hxae1yTT44\nkmtsFS6Wqr5wQey7PxehCUY=\n-----END PRIVATE KEY-----\n",
  "client_email": "blogger-test@blogger-test-441717.iam.gserviceaccount.com",
  "client_id": "109126077830572082410",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/blogger-test%40blogger-test-441717.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_KEY, scopes=SCOPES
)

# Authenticate with the Blogger API
blogger = build('blogger', 'v3', credentials=credentials)

# Replace with your actual blog ID
blog_id = '737863940949257967'  

async def create_draft_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Creates a draft post on the blog."""
    try:
        title = update.message.text.replace('/createdraft ', '')

        # Create the post body
        body = "This is a draft post created from my Telegram bot!"

        # Create the post using the Blogger API
        post = {
            'kind': 'blogger#post',
            'blog': {
                'id': blog_id
            },
            'title': title,
            'content': body
        }
        blogger.posts().insert(blogId=blog_id, body=post, isDraft=True).execute()
        await update.message.reply_text(f'Draft post created with title: {title}')

    except RefreshError as e:
        logger.error(f"Error creating post: {e}")
        await update.message.reply_text('Invalid JWT Signature. Please check your service account key.')

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        await update.message.reply_text('Error creating post.')

def main():
    """Starts the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register the command handler
    application.add_handler(CommandHandler("createdraft", create_draft_post))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
        
