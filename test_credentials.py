from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"

# Scopes required for Blogger API
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_on_vps():
    """Authenticate the user and save token for future use."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    credentials = flow.run_console()  # No browser needed, works via terminal
    print("Authentication successful.")
    return credentials

def list_blogs(credentials):
    """List blogs for the authenticated user."""
    service = build("blogger", "v3", credentials=credentials)
    blogs = service.blogs().listByUser(userId="self").execute()
    for blog in blogs.get("items", []):
        print(f"Blog ID: {blog['id']}, Blog Name: {blog['name']}, Blog URL: {blog['url']}")

if __name__ == "__main__":
    creds = authenticate_on_vps()
    list_blogs(creds)
