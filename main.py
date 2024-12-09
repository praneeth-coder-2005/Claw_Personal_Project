import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"
TOKEN_FILE = "token.pickle"  # Token file to store credentials
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_on_vps():
    """Authenticate the user and save token for future use."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)
            print("Loaded saved credentials.")
            return credentials

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    credentials = flow.run_local_server(port=8080, open_browser=False)

    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(credentials, token)
        print("Credentials saved for future use.")
    
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
