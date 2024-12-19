POST_TEMPLATE = """
<!--Movie Post Layout with TMDb Integration-->
<!--Permanent Thumbnail for Blogger-->
<img alt="Movie Thumbnail" id="thumbnail-helper" src="https://image.tmdb.org/t/p/w500/dYck0PrLbnmUsme75R8rRYLOcTv.jpg" style="display: none;" />

<!--Meta Tag for Blogger Thumbnail (used by Blogger)-->
<meta content="https://image.tmdb.org/t/p/w500/dYck0PrLbnmUsme75R8rRYLOcTv.jpg" id="og-thumbnail" property="og:image"></meta>

<div class="movie-post">
  <!--Movie Header-->
  <div class="movie-header">
    <!--Movie Poster (Visible Only Once Inside the Post)-->
    <img alt="Movie Poster" class="movie-poster" id="movie-poster" src="{poster_url}" />

    <!--Movie Details Section-->
    <div class="movie-details">
      <h2 class="movie-title" id="movie-title">{movie_title}</h2>
      <p class="release-date" id="release-date"><strong>Release Date:</strong> {release_date}</p>
      <p class="rating" id="rating"><strong>Rating:</strong> {rating}</p>
      <p class="genre" id="genre"><strong>Genre:</strong> {genre}</p>
      <p class="runtime" id="runtime"><strong>Runtime:</strong> {runtime}</p>
    </div>
  </div>

  <!--Movie Synopsis Section-->
  <div class="movie-description">
    <h3>Synopsis</h3>
    <p id="movie-synopsis">{synopsis}</p>
  </div>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Links</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #fff;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #1e1e1e;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        }}
        h1 {{
            text-align: center;
            color: #ffc107;
        }}
        .links-section {{
            margin-top: 20px;
        }}
        .links-section h2 {{
            margin-bottom: 10px;
            font-size: 18px;
            color: #00ccff;
        }}
        .link-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #252525;
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }}
        .link-item span {{
            font-size: 14px;
            color: #fff;
        }}
        .link-item a {{
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 14px;
            color: #fff;
            background: #ff5722;
            transition: background 0.3s ease;
        }}
        .link-item a:hover {{
            background: #e64a19;
        }}
        .tg-button {{
            background: #007BFF;
        }}
        .tg-button:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Telegram Files</h1>
 
           {download_links}
        </div>
    </div>
</body>
  </html>
  
    


<!-- CSS for the Dark Theme and Button Text Visibility -->

<style>

  .download-links {{

    margin-top: 20px;

  }}

  .download-links h3 {{

    color: #ff6f61;

    font-size: 24px;

    margin-bottom: 15px;

  }}

  .file-block {{

    background-color: #333;

    padding: 15px;

    margin-bottom: 20px;

    border-radius: 8px;

  }}

  .file-block p {{

    color: #fff;

    font-size: 14px;

    margin: 0;

  }}

  .button-container {{

    display: flex;

    justify-content: flex-start;

    gap: 10px;

    margin-top: 10px;

  }}

  .button {{

    background-color: #ff6f61;

    color: white;

    border: none;

    padding: 10px 20px;

    border-radius: 5px;

    font-size: 14px;

    cursor: pointer;

    transition: background-color 0.3s ease;

  }}

  .button a {{

    color: white;

    text-decoration: none;

  }}

  .button:hover {{

    background-color: #e14e43;

  }}

  .button a:hover {{

    color: white;

  }}

  .button tg-gofile:hover {{

    background-color: #e14e43;

  }}

</style>




 
    
    </div>

 

<!--Dark Theme CSS Styling-->
<style>
  body {{
    font-family: 'Arial', sans-serif;
    background-color: #121212;
    color: #ddd;
    margin: 0;
    padding: 0;
  }}

  .movie-post {{
    width: 100%;
    max-width: 800px;
    margin: 50px auto;
    background-color: #1a1a1a;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    padding: 20px;
  }}

  .movie-header {{
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }}

  .movie-poster {{
    width: 150px;
    height: 225px;
    border-radius: 8px;
    object-fit: cover;
    margin-right: 20px;
  }}

  .movie-details {{
    flex-grow: 1;
  }}

  .movie-title {{
    font-size: 24px;
    margin: 0;
    font-weight: bold;
    color: #fff;
  }}

  .movie-details p {{
    font-size: 14px;
    margin: 5px 0;
  }}

  .movie-description {{
    margin-top: 30px;
  }}

  .movie-description h3 {{
    font-size: 22px;
    color: #ff6f61;
    margin-bottom: 10px;
  }}

  .movie-description p {{
    font-size: 16px;
    line-height: 1.5;
    color: #ccc;
  }}

  .download-section {{
    margin-top: 20px;
    padding: 15px;
    background-color: #1a1a1a;
    border: 1px solid #333;
    border-radius: 10px;
  }}

  .download-section h3 {{
    font-size: 20px;
    color: #ff6f61;
    margin-bottom: 10px;
  }}

  .tg-files ul {{
    padding-left: 20px;
  }}

  .tg-files li {{
    margin: 5px 0;
  }}

  .tg-files .tg-link {{
    color: #61dafb;
    text-decoration: none;
    font-size: 16px;
  }}

  .tg-files .tg-link:hover {{
    text-decoration: underline;
  }}

  .download-links {{
    margin-top: 10px;
  }}

  .download-thumbnail {{
    width: 120px;
    height: 80px;
    margin: 5px;
    border: 2px solid #333;
    border-radius: 8px;
    object-fit: cover;
    transition: transform 0.3s, box-shadow 0.3s;
  }}

  .download-thumbnail:hover {{
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  }}

  /* Ensure Thumbnail Helper is hidden */
  #thumbnail-helper {{
    display: none; /* Ensure it doesn't show up */
  }}
</style>

<!--JavaScript to Fetch and Populate Movie Details-->
<script>
  // Your TMDb API Key
  const tmdbApiKey = 'bb5f40c5be4b24660cbdc20c2409835e';

  // Replace with the movie's TMDb ID
  const tmdbMovieId = '1396917'; // Example: Replace with your TMDb ID

  // Manually set the Thumbnail Image Link (Replace this URL with your desired thumbnail URL)
  const manualThumbnailUrl = 'https://image.tmdb.org/t/p/w500/your_thumbnail_image_path.jpg'; // Replace with your thumbnail image link

  // Fetch Movie Details from TMDb API
  async function fetchMovieDetails(movieId) {{
    const url = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${tmdbApiKey}&language=en-US`;

    try {{
      const response = await fetch(url);
      const data = await response.json();

      // Populate movie details in the post
      if (data) {{
        document.getElementById('movie-title').innerText = data.title || 'Unknown Title';
        document.getElementById('release-date').innerText = `Release Date: ${data.release_date || 'Unknown'}`;
        document.getElementById('rating').innerText = `Rating: ${data.vote_average || 'Unknown'}`;
        document.getElementById('genre').innerText = `Genre: ${data.genres.map(genre => genre.name).join(', ') || 'Unknown'}`;
        document.getElementById('runtime').innerText = `Runtime: ${data.runtime ? `${data.runtime} minutes` : 'Unknown'}`;
        document.getElementById('movie-synopsis').innerText = data.overview || 'No Synopsis Available';

        // Update movie poster dynamically (poster fetched from TMDb)
        const posterUrl = `https://image.tmdb.org/t/p/w500${data.poster_path}`;
        document.getElementById('movie-poster').src = posterUrl;

        // Update Blogger thumbnail helper image (hidden) with manually set thumbnail image
        document.getElementById('thumbnail-helper').src = manualThumbnailUrl; // Ensure Blogger picks up this image

        // Update og:image meta tag for better social media preview with manually set thumbnail image
        document.getElementById('og-thumbnail').setAttribute('content', manualThumbnailUrl); // Update the meta tag dynamically
      }}
    }} catch (error) {{
      console.error('Error fetching movie details:', error);
    }}
  }}

  // Call the fetchMovieDetails function on page load
  window.onload = function () {{
    fetchMovieDetails(tmdbMovieId); // Replace tmdbMovieId with the actual movie ID
  }};
    </script>
"""
