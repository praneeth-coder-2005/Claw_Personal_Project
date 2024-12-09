from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"

# Scopes required for Blogger API
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_with_browser():
    """Authenticate the user using OAuth 2.0 with browser redirection."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    print("Redirecting to browser for Google login...")
    
    # Open browser, authenticate, and return to the script automatically
    credentials = flow.run_local_server(port=8080, open_browser=True)

    print("Authentication successful. Access token obtained.")
    return credentials

def list_blogs(credentials):
    """List blogs for the authenticated user."""
    service = build("blogger", "v3", credentials=credentials)
    blogs = service.blogs().listByUser(userId="self").execute()
    
    print("\nYour Blogs:")
    for blog in blogs.get("items", []):
        print(f"Blog ID: {blog['id']}, Blog Name: {blog['name']}, Blog URL: {blog['url']}")

if __name__ == "__main__":
    creds = authenticate_with_browser()
    list_blogs(creds)
