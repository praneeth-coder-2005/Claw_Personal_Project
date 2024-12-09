from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_with_console():
    """Authenticate the user using OAuth 2.0 with console fallback."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    print("Opening authentication URL in the terminal...")
    credentials = flow.run_console()  # Works in headless environments
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
    creds = authenticate_with_console()
    list_blogs(creds)
