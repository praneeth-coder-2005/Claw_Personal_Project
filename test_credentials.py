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
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7704211647:AAGslX2jlqGpzeXbJlX61egbMHb8eotNxs4")  # Replace YOUR_BOT_TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Service account key (updated with your provided key)
SERVICE_ACCOUNT_KEY = {
    "type": "service_account",
    "project_id": "blogger-test-441717",
    "private_key_id": "a547cd94ae14deb99dce4465c7876b7a4affea9c",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDHxXgKQX9PCiWU\njgtxdoLse6zAk1+VJVP7gh4pHt5xEn39prsburs41PlKjN9OxJXao5P1HCA9UdFF\nytAdC9vNHjHwc+I4EZJwgn8EbbtPmrYzVpmLMCgo2FYo7q4BXmQGW4MDyVEcqGn3\nUKsQR+uakC0Uuvnplq6XC2TD0rtFn29/cKnmZ8LliiS/9LRDq9MSPFB766uG72C+\nASSpHh4vjqdLXMI0ePTKZ4MUD+ddkyzWGOdrCCdqrF968YuyBeXglh2nknF1A4id\nVeLlNBlwjO3tzReWQKp8gRP698NYvLzdU9eBs83Yx255Niurr/bAGzLE1NBtlIrD\n3U1mMRgFAgMBAAECggEAKh+WVztGV+lA0Vk+Snd91dWiMJ0iq3VKhx8BsxQCPX9z\nt5d/nrI6JhqqUjDwKVDEdGzHlwiON7/Xy8qfJXDJsS+rwhL9YWs7IKQzmkB1Haz2\nvE6HY9UMssgjKtBhOoKnvrtvHc5GXy+X4IFPAMjZgibiipt+dOXD/K93WN9Hg79i\nCAG1SNCkifo4exgyMfPyTNXN7vFMAusa6yPhNgm8Tj/MwdgqBZXfhOcgrLP+2oes\nQFacfn/7uVZYV+gqAxo8ZBFhDQ6StIKHoaQzbz4KwZds0DJ8Iq/9/8Du1nMgBEZ0\nTe5blqv5LHeGcqkP3QL4I3/cEc2H1lLlK/uSAv8RwQKBgQDzVES66CDxRSnQTHsh\nWJd79b/X9Rfjk9Fmfjs+GR7HKwc5ZzAeB+hrl911QbcpY2ZWADlGi0kveSj6zfnj\n2dobUWRqvTmusPysE7uvzFkyqXkPdkReL35gxGJAetwTwfcztpUCmo01vku26IRW\n3+Da+dc5tJk4/LSL/gH4/SHbkQKBgQDSLIwccchgr2xYIbqlyu+B6JhbBUtvsQkV\niD9YcEPEBTZmW66ZIz+UKyK/JfBEoJiRQSfXwx2cFuVXjh0PP0veJ0Wcfeg0uzkU\nqm6gevSwSIKMuN3z3SH5/cuGnRnOY5PlXN0l1s0VSenVIMY8f7qipd1s3u0R4HUT\ntWlAZITzNQKBgQDaUcRs8nMEJqsSklxzmdooxWDAcc5iSTE7RYz/9WfxCUEtFtFM\nUIoPZy2y1ChzgRTDmuXIzpX2ez3ycbaA4ejYU9nGD0te2ruJ5Raj77QkSXwuDE3h\nN7mrNuh0tAcbzw9uHaZqtKJ4Euo6DTsX+zzzG/EofEpxoAKaDGhWrz+ekQKBgQDN\nWCbgl67eACcMCJBS8e6F71oD/C1TCBZHCmJRpwYem7Ul1sfE6TJyMp71QTz54CqQ\nKKej4Aeq/JfArqHnxsD6YUZa+o0IEDBZ55bEhr1RCtc6ZFi+rbxHgtb6Q73170aN\nnuiW0sJ23UtwJ2BntagEx6eKelgH0lSxF9qoxk07TQKBgQCIIHyYVwIFhySWlaZa\nubNS2npk5l5uUdOh33HBPcYuI1JBSrwaSaYGCylc4Aet/7FtPTzCuZ5uvlmdOTuy\n53aJSSHk2APFWmV/Alz+ARvDIfFOXAi7Ilgga6qpChFI6au1z9eUQvI6aD7Q80cx\nKfbHHXCTEZyQqd8ykVPXGZa9Tg==\n-----END PRIVATE KEY-----\n",
    "client_email": "blogger-test@blogger-test-441717.iam.gserviceaccount.com",
    "client_id": "111585980206887361113",
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
        
