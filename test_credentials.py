import os
import json
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Replace with your actual bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Service account key (replace with your actual key)
SERVICE_ACCOUNT_KEY = {
    "type": "service_account",
    "project_id": "blogger-test-441717",
    "private_key_id": "854459011a60e5eb0a89aaaa4c682399979f2317",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDCGceDvFyynD3C\nL8QAnsqtFug2KWEc4Y/zEczPUYI8toP/OUMED8dMRoxUmxq+Ha7/Gfp1ZrA27eXL\nUnFoAVq5/b8MbH2WKd/DqKH14m4XQ6TccpQW9kIoH8t6IF6E/PT25B+gWq5Pthes\ntvSA7xlqmN9No4YlHOrLLUq3z79Esp+jBk/UhuI6it7K9ai6zL/rxouJD9EEhk99\nxL4cf/25SnlWfBO2B197l1ZMCHbsz8LewYqnHiEwBqn0zAavkrVfy+eV2LBjb+Qe\nT0tASzbxVUxoTI6AjAj4C2AuzzkZS3LvUgYeaee3CtS4FapyJJcFo9l1+StgoW8P\nDodCaqPNAgMBAAECggEACJior+prNpPZ3lxMM3TU6BaQITny7ZsFy4+ZwQLMoFC7\nBtYr5CWov3WOaH7YD9xzsCOf5owuOLiPiVI06JTKxlr5F51EcJ6ZJOq2hZPKKWib\nCBJhAaVVZ76EvftqBDzJwpd22Ry7BJe9c65EpOMx/nkXxrH70m/17Bqs6Pgf8fRd\ncvDt0NIiOTvLFahte2ZDh5+1vBXp4gFYD1oiA4Cx+gZVLxIEoVdtTVKh5Jv9icuq\n2xW6L80S3UQEhWia4pkvuNDVunbeOTmKD8iP6s9N/Of2mxAYsWQqq/MkpQBD+s5/\n1O5EpysHZeWFnMu7j6pQJlJPJ23bmKp6NEGg00PN5wKBgQDx66kLOjqTlEJurl/1\n7XGSipE90A6SPdh/weseJpiE4tEJXAFJbkO8SjLYovePWNiHzLnjsixCF+1ERsNK\nTFNZviaui4vqkCTPlpCzFUtIoXODntlAkxbe5g8MCi+zQa3bEtAK+A1dS4WfA0k/\nxARY2bl4P2YwqNtUGy3p5FWu2wKBgQDNZahviLTohp4j3gGCqQpN5CnwNG1s0tSd\nFvzUEx++zhFucYgXM/VTTlPvMkVqIfMHJIAb844DwV12T96jf1U0B44nmCkq5Oj6\nCrXYTO/leTU4Zsf0JCdpH3PUxREJpojEDj5eVg/BxZ+f9YG5XQmMN23jSXKm4cAe\ngQ5W0SvUdwKBgQC2dr47P6HqqYopnM+3120vz9+YNZKn7omaYpKJXSbwI3ryijhW\nQBpKq9QJ3XDG54X5dwpFmJ8VAqLsOksVgNfk+iyGva28Lxf0kmV1DPyJPWy4u1i1\nAbvgRrjWpeAwXbtZXqkXfNvnoAyaUIow1BFLSnw/G+JhlRpIJ2/L13JgvQKBgC9h\nef9wm7rgAu7nMZYAhJ3/OiVtEqj94YnzWZNabgJH6wF9MxWXKMp00SvmftjCyBsn\nsl3AS0xWeMboGcXBg9givgooMabxc0Tq35Pr+5MF6N7/5rRM+sJnPQMiCpIdVoNT\nfdOpKq1adz4hFjG6Yo9z4eeCc+5HOVhQEQy559B1AoGAREcHst06oOGOafCNpgj5\njhi8ohNkc/6nxtDqCug8+1JYvIsCJsLVhhKgwWeJ2poXhgM+ie5GqMcazS1haxRv\nxO89uZR7aafL/FqrZDHTu6mIKzb4BbRx7k1h5hjaHCulRneWUO+Ins/yxEaIz8iL\nPU3jN+3nLwCjo78xS3J0f0Y=\n-----END PRIVATE KEY-----\n",
    "client_email": "blogger-test@blogger-test-441717.iam.gserviceaccount.com",
    "client_id": "107062288693690040341",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/blogger-test%40blogger-test-441717.iam.gserviceaccount.com"
}

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_KEY, scopes=SCOPES
)

# Authenticate with the Blogger API
blogger = build('blogger', 'v3', credentials=credentials)

# Get the blog ID (replace with your actual blog ID)
blog_id = 'YOUR_BLOG_ID'  # Replace with your actual blog ID

def create_draft_post(update: Update, context):
    """Creates a draft post on the blog."""
    try:
        title = update.message.text.replace('/createdraft ', '')
        # Create the post body (replace with your desired content)
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
        update.message.reply_text(f'Draft post created with title: {title}')

    except Exception as e:
        print(f"Error creating post: {e}")
        update.message.reply_text('Error creating post.')

def main():
    """Starts the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Register the command handler
    dispatcher.add_handler(CommandHandler("createdraft", create_draft_post))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
