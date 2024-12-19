import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    CallbackContext,
)
from telegram.ext import filters as Filters
from config import BOT_TOKEN
from post_template import POST_TEMPLATE
from utils import (
    search_movie_tmdb,
    fetch_movie_details_tmdb,
    create_post_menu_keyboard,
    create_download_link_keyboard,
    format_download_links,
    update_post_template,
    create_post_list_keyboard
)
import queue
from telegram import Bot

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store post data
posts = {}

#Store Temp Post Data
temp_post_data = {}


def start(update: Update, context: CallbackContext) -> None:
    """Sends the welcome message and options."""
    keyboard = [
        [InlineKeyboardButton("Create Post", callback_data="create_post")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome! What would you like to do?", reply_markup=reply_markup)

def create_post_handler(update: Update, context: CallbackContext) -> None:
    """Handles the create post option."""
    query = update.callback_query
    query.answer()  # Acknowledge the callback
    query.edit_message_text(
        text="Let's start creating your movie post. What details you need to update?",
        reply_markup=create_post_menu_keyboard()
    )

def tmdb_id_handler(update: Update, context: CallbackContext) -> None:
    """Handles the TMDb ID input request."""
    query = update.callback_query
    query.answer()
    query.edit_message_text("Please enter the movie name to search on TMDb:")
    context.user_data['stage'] = "waiting_tmdb_query"

def process_tmdb_query(update: Update, context: CallbackContext) -> None:
    """Process the TMDb query."""
    movie_name = update.message.text
    context.user_data['movie_name'] = movie_name
    movies = search_movie_tmdb(movie_name)
    if movies:
        keyboard = [
            [InlineKeyboardButton(movie['title'], callback_data=f"tmdb_select_{movie['id']}")] for movie in movies
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please select the movie from the list:", reply_markup=reply_markup)
    else:
       update.message.reply_text("No movies found with that name. Please try again.")
       
def process_tmdb_selection(update: Update, context: CallbackContext) -> None:
    """Handles the TMDb movie selection and stores the movie ID and details."""
    query = update.callback_query
    query.answer()
    movie_id = query.data.split('_')[-1]
    movie_details = fetch_movie_details_tmdb(movie_id)
    
    if movie_details:
      context.user_data['tmdb_id'] = movie_id
      context.user_data['movie_details'] = movie_details
      context.user_data['poster_url'] = f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path', '')}"
      query.edit_message_text(
        text=f"Selected movie: {movie_details.get('title')}. Moving back to create post options.",
        reply_markup=create_post_menu_keyboard()
      )
    else:
       query.edit_message_text("Failed to fetch movie details. Please try again.")


def poster_link_handler(update: Update, context: CallbackContext) -> None:
    """Handles the poster link input request."""
    query = update.callback_query
    query.answer()
    if 'poster_url' in context.user_data:
        query.edit_message_text(
            text=f"Poster from TMDB is taken. If you want to change provide the link.",
            reply_markup=create_post_menu_keyboard()
        )
        context.user_data['stage'] = "waiting_poster_link"
    else:
        query.edit_message_text("Please enter the poster link:")
        context.user_data['stage'] = "waiting_poster_link"

def process_poster_link(update: Update, context: CallbackContext) -> None:
    """Process the poster link."""
    poster_link = update.message.text
    context.user_data['poster_url'] = poster_link
    update.message.reply_text(
        text=f"Poster link is saved. Going back to Create Post options.",
        reply_markup=create_post_menu_keyboard()
    )


def add_download_link_handler(update: Update, context: CallbackContext) -> None:
    """Handles the request to add download links."""
    query = update.callback_query
    query.answer()
    context.user_data['download_links'] = context.user_data.get('download_links', {})
    query.edit_message_text("Please enter the title for the download link:")
    context.user_data['stage'] = "waiting_download_title"


def process_download_title(update: Update, context: CallbackContext) -> None:
    """Processes the download link title."""
    title = update.message.text
    context.user_data['current_download_title'] = title
    update.message.reply_text("Please enter the download link URL:")
    context.user_data['stage'] = "waiting_download_link"

def process_download_link(update: Update, context: CallbackContext) -> None:
    """Processes the download link URL."""
    url = update.message.text
    title = context.user_data.get('current_download_title', 'Unknown')
    download_links = context.user_data.get('download_links', {})
    download_links[title] = url
    context.user_data['download_links'] = download_links
    update.message.reply_text(
        text="Download link added. What do you want to do next?",
        reply_markup = create_download_link_keyboard()
    )
    context.user_data['stage'] = None

def download_done(update: Update, context: CallbackContext) -> None:
    """Process the download link."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
         text="All download links are saved. Going back to Create Post options.",
         reply_markup=create_post_menu_keyboard()
    )

def done_handler(update: Update, context: CallbackContext) -> None:
    """Handles the 'Done' button click, finalizes and displays the code."""
    query = update.callback_query
    query.answer()

    if 'movie_details' not in context.user_data:
      query.edit_message_text("Movie details is not selected. Please select from TMDb ID.")
      return

    query.edit_message_text("Please enter the post title for remember.")
    context.user_data['stage'] = 'waiting_post_title'

def process_post_title(update: Update, context: CallbackContext) -> None:
    """Process the post title and generate code."""
    post_title = update.message.text
    movie_details = context.user_data.get('movie_details')
    poster_url = context.user_data.get('poster_url', None)
    download_links = context.user_data.get('download_links', {})
    
    updated_template = update_post_template(
        POST_TEMPLATE, movie_details, poster_url, download_links
    )
    
    # Store post data for edit
    post_id = len(posts) + 1
    posts[post_id] = {
      'title': post_title,
      'code': updated_template
    }
    
    context.user_data.clear()

    update.message.reply_text(f"Your post '{post_title}' is created!\n\n"
    "```html\n"
    f"{updated_template}\n"
    "```", parse_mode='MarkdownV2')
    
def list_handler(update: Update, context: CallbackContext) -> None:
  """List saved post title."""
  if posts:
    update.message.reply_text("Here is list of post, Which post you want to edit?", reply_markup=create_post_list_keyboard(posts))
  else:
    update.message.reply_text("No posts available right now. Please create a post first.")

def edit_post_handler(update: Update, context: CallbackContext) -> None:
  """Edit saved posts."""
  query = update.callback_query
  query.answer()
  post_id = int(query.data.split('_')[-1])
  post_data = posts.get(post_id)

  if post_data:
    context.user_data['edit_post_id'] = post_id
    
    #Re-initialize the context data to edit the post again.
    temp_post_data['movie_details'] = None
    temp_post_data['poster_url'] = None
    temp_post_data['download_links'] = {}
    
    query.edit_message_text(
      text=f"Edit the post: {post_data['title']}. What details you need to update?",
      reply_markup=create_post_menu_keyboard()
    )
  else:
    query.edit_message_text("Post not found")


def main() -> None:
    """Start the bot."""
    update_queue = queue.Queue()
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot, update_queue=update_queue) # Correct way to initialize updater
    dp = updater.dispatcher # Corrected this line

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", list_handler))
    
    dp.add_handler(CallbackQueryHandler(create_post_handler, pattern='create_post'))
    dp.add_handler(CallbackQueryHandler(tmdb_id_handler, pattern='tmdb_id'))
    dp.add_handler(CallbackQueryHandler(poster_link_handler, pattern='poster_link'))
    dp.add_handler(CallbackQueryHandler(add_download_link_handler, pattern='add_download_link'))
    dp.add_handler(CallbackQueryHandler(process_tmdb_selection, pattern='tmdb_select_'))
    dp.add_handler(CallbackQueryHandler(download_done, pattern='download_done'))
    dp.add_handler(CallbackQueryHandler(done_handler, pattern='done'))
    dp.add_handler(CallbackQueryHandler(edit_post_handler, pattern='edit_post_'))
    
    #Handle normal text messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, 
        lambda update, context: (
           process_tmdb_query(update, context) if context.user_data.get('stage') == 'waiting_tmdb_query' else
           process_poster_link(update, context) if context.user_data.get('stage') == 'waiting_poster_link' else
           process_download_title(update, context) if context.user_data.get('stage') == 'waiting_download_title' else
           process_download_link(update, context) if context.user_data.get('stage') == 'waiting_download_link' else
           process_post_title(update,context) if context.user_data.get('stage') == 'waiting_post_title' else None
    )
    ))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
