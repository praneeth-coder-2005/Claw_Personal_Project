import logging
import telebot
from telebot import types
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
import re

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store post data
posts = {}

# Store temporary post data
temp_post_data = {}

# States
states = {}

def set_state(chat_id, state):
    states[chat_id] = state

def get_state(chat_id):
    return states.get(chat_id)


@bot.message_handler(commands=['start'])
def start(message):
    """Sends the welcome message and options."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Create Post", callback_data="create_post"))
    keyboard.add(types.InlineKeyboardButton("List Posts", callback_data="list_posts"))
    bot.send_message(message.chat.id, "Welcome! What would you like to do?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'create_post')
def create_post_handler(call):
    """Handles the create post option."""
    keyboard = create_post_menu_keyboard()
    bot.edit_message_text(
        text="Let's start creating your movie post. What details you need to update?",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == 'tmdb_id')
def tmdb_id_handler(call):
    """Handles the TMDb ID input request."""
    bot.edit_message_text(
        text="Please enter the movie name to search on TMDb:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    set_state(call.message.chat.id, "waiting_tmdb_query")

@bot.message_handler(func=lambda message: get_state(message.chat.id) == "waiting_tmdb_query")
def process_tmdb_query(message):
    """Process the TMDb query."""
    movie_name = message.text
    temp_post_data[message.chat.id] = {'movie_name': movie_name}
    movies = search_movie_tmdb(movie_name)
    if movies:
        keyboard = types.InlineKeyboardMarkup()
        for movie in movies:
            keyboard.add(types.InlineKeyboardButton(movie['title'], callback_data=f"tmdb_select_{movie['id']}"))
        bot.send_message(message.chat.id, "Please select the movie from the list:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "No movies found with that name. Please try again.")
    set_state(message.chat.id, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tmdb_select_'))
def process_tmdb_selection(call):
    """Handles the TMDb movie selection and stores the movie ID and details."""
    movie_id = call.data.split('_')[-1]
    movie_details = fetch_movie_details_tmdb(movie_id)

    if movie_details:
        temp_post_data[call.message.chat.id]['tmdb_id'] = movie_id
        temp_post_data[call.message.chat.id]['movie_details'] = movie_details
        temp_post_data[call.message.chat.id]['poster_url'] = f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path', '')}"
        bot.edit_message_text(
            text=f"Selected movie: {movie_details.get('title')}. Moving back to create post options.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_post_menu_keyboard()
        )
    else:
        bot.edit_message_text(
            text="Failed to fetch movie details. Please try again.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )


@bot.callback_query_handler(func=lambda call: call.data == 'poster_link')
def poster_link_handler(call):
    """Handles the poster link input request."""
    if 'poster_url' in temp_post_data.get(call.message.chat.id, {}):
        bot.edit_message_text(
            text=f"Poster from TMDB is taken. If you want to change provide the link.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_post_menu_keyboard()
        )
        set_state(call.message.chat.id, "waiting_poster_link")
    else:
        bot.edit_message_text(
            text="Please enter the poster link:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        set_state(call.message.chat.id, "waiting_poster_link")

@bot.message_handler(func=lambda message: get_state(message.chat.id) == "waiting_poster_link")
def process_poster_link(message):
    """Process the poster link."""
    poster_link = message.text
    temp_post_data[message.chat.id]['poster_url'] = poster_link
    bot.send_message(
        message.chat.id,
        text="Poster link is saved. Going back to Create Post options.",
        reply_markup=create_post_menu_keyboard()
    )
    set_state(message.chat.id, None)


@bot.callback_query_handler(func=lambda call: call.data == 'add_download_link')
def add_download_link_handler(call):
    """Handles the request to add download links."""
    temp_post_data[call.message.chat.id]['download_links'] = temp_post_data.get(call.message.chat.id, {}).get('download_links', {})
    bot.edit_message_text(
        text="Please enter the title for the download link:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    set_state(call.message.chat.id, "waiting_download_title")

@bot.message_handler(func=lambda message: get_state(message.chat.id) == "waiting_download_title")
def process_download_title(message):
    """Processes the download link title."""
    title = message.text
    temp_post_data[message.chat.id]['current_download_title'] = title
    bot.send_message(message.chat.id, "Please enter the download link URL:")
    set_state(message.chat.id, "waiting_download_link")


@bot.message_handler(func=lambda message: get_state(message.chat.id) == "waiting_download_link")
def process_download_link(message):
    """Processes the download link URL."""
    url = message.text
    title = temp_post_data[message.chat.id].get('current_download_title', 'Unknown')
    download_links = temp_post_data[message.chat.id].get('download_links', {})
    download_links[title] = url
    temp_post_data[message.chat.id]['download_links'] = download_links
    bot.send_message(
        message.chat.id,
        text="Download link added. What do you want to do next?",
        reply_markup=create_download_link_keyboard()
    )
    set_state(message.chat.id, None)


@bot.callback_query_handler(func=lambda call: call.data == 'download_done')
def download_done(call):
    """Process the download link."""
    bot.edit_message_text(
        text="All download links are saved. Going back to Create Post options.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=create_post_menu_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'done')
def done_handler(call):
    """Handles the 'Done' button click, finalizes and displays the code."""
    if 'movie_details' not in temp_post_data.get(call.message.chat.id, {}):
        bot.edit_message_text(
            text="Movie details is not selected. Please select from TMDb ID.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        return

    bot.edit_message_text(
        text="Please enter the post title for remember.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    set_state(call.message.chat.id, 'waiting_post_title')


@bot.message_handler(func=lambda message: get_state(message.chat.id) == 'waiting_post_title')
def process_post_title(message):
    """Process the post title and generate code."""
    post_title = message.text
    movie_details = temp_post_data[message.chat.id].get('movie_details')
    poster_url = temp_post_data[message.chat.id].get('poster_url', None)
    download_links = temp_post_data[message.chat.id].get('download_links', {})

    if movie_details:
      updated_template = update_post_template(
          POST_TEMPLATE, movie_details, poster_url, download_links
      )

      # Store post data for edit
      post_id = len(posts) + 1
      posts[post_id] = {
        'title': post_title,
        'code': updated_template
      }
      
      temp_post_data.pop(message.chat.id, None)
      set_state(message.chat.id, None)

      #Removed parse_mode and send normal HTML code
      bot.send_message(message.chat.id, f"Your post '{post_title}' is created!\n\n"
                      "```html\n"
                      f"{updated_template}\n"
                      "```")
    else:
        bot.send_message(message.chat.id, "Movie details not found. Please select a movie using TMDb ID first.")


@bot.callback_query_handler(func=lambda call: call.data == 'list_posts')
def list_handler(call):
  """List saved post title."""
  if posts:
    bot.edit_message_text(
        text="Here is list of post, Which post you want to edit?",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=create_post_list_keyboard(posts)
    )
  else:
    bot.edit_message_text(
        text="No posts available right now. Please create a post first.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_post_'))
def edit_post_handler(call):
  """Edit saved posts."""
  post_id = int(call.data.split('_')[-1])
  post_data = posts.get(post_id)

  if post_data:
      temp_post_data[call.message.chat.id] = {}
      temp_post_data[call.message.chat.id]['edit_post_id'] = post_id
    
    #Re-initialize the context data to edit the post again.
      bot.edit_message_text(
          text=f"Edit the post: {post_data['title']}. What details you need to update?",
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          reply_markup=create_post_menu_keyboard()
      )
  else:
    bot.edit_message_text(
          text="Post not found",
          chat_id=call.message.chat.id,
          message_id=call.message.message_id
      )


def main():
    """Start the bot."""
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
