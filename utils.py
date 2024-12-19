import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TMDB_API_KEY

def search_movie_tmdb(query):
    """Searches for a movie on TMDb based on the query and returns search results."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    try:
      response = requests.get(url)
      response.raise_for_status()  # Raise an exception for bad status codes
      data = response.json()
      return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error during TMDb API call: {e}")
        return []

def fetch_movie_details_tmdb(movie_id):
    """Fetches a movie's details on TMDb based on the movie ID."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
      response = requests.get(url)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.RequestException as e:
      print(f"Error during TMDb API call for movie details: {e}")
      return None

def create_post_menu_keyboard():
    """Creates inline keyboard for post creation options."""
    keyboard = [
      [InlineKeyboardButton("TMDb ID", callback_data='tmdb_id')],
      [InlineKeyboardButton("Poster Link", callback_data='poster_link')],
      [InlineKeyboardButton("Add Download Link", callback_data='add_download_link')],
      [InlineKeyboardButton("Done", callback_data='done')]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_download_link_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Another Download Link", callback_data='add_download_link')],
        [InlineKeyboardButton("Done", callback_data='download_done')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_post_list_keyboard(posts):
    keyboard = []
    for post_id, post_title in posts.items():
        keyboard.append([InlineKeyboardButton(post_title, callback_data=f'edit_post_{post_id}')])
    
    return InlineKeyboardMarkup(keyboard)

def format_download_links(download_links):
    """Formats download links into HTML structure."""
    formatted_links = ""
    for title, url in download_links.items():
      formatted_links += f"""
<div class="link-item">
    <span>{title}</span>
    <a href="{url}" class="tg-button">TG File</a>
</div>
      """
    return formatted_links

def update_post_template(template, movie_details, poster_url, download_links):
    """Updates the HTML template with movie details, poster URL, and download links."""
    formatted_download_links = format_download_links(download_links)

    updated_template = template.format(
        movie_title = movie_details.get('title', 'Unknown Title'),
        release_date = movie_details.get('release_date', 'Unknown'),
        rating = movie_details.get('vote_average', 'Unknown'),
        genre = ', '.join([genre['name'] for genre in movie_details.get('genres', [])]) if movie_details.get('genres') else 'Unknown',
        runtime = f"{movie_details.get('runtime', 'Unknown')} minutes",
        synopsis = movie_details.get('overview', 'No Synopsis Available'),
        poster_url = poster_url if poster_url else "https://via.placeholder.com/500x750.png?text=Poster", # Use placeholder if no poster_url
        download_links = formatted_download_links
    )
    return updated_template
