import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Load credentials from JSON file
with open('my_credentials.json', 'r') as f:
    credentials_info = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=SCOPES
)

# Authenticate with the Blogger API
try:
    blogger = build('blogger', 'v3', credentials=credentials)

    # Get the list of blogs (this requires authentication)
    blogs = blogger.blogs().listByUser(userId='self').execute()

    if blogs['items']:
        print("Credentials are valid!")
        for blog in blogs['items']:
            print(f"Blog Name: {blog['name']}, Blog ID: {blog['id']}")
    else:
        print("No blogs found. Make sure your credentials have access to Blogger.")

except Exception as e:
    print(f"Error: {e}")
    print("Credentials might be invalid or lack necessary permissions.")
  
