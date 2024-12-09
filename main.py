from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"

# Scopes required for Blogger API
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_on_vps():
    """Authenticate the user using OAuth 2.0."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    # Use a local server for authentication (works on VPS)
    credentials = flow.run_local_server(port=8080, open_browser=False)
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
