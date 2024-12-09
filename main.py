from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Path to the client credentials JSON file
CLIENT_CREDENTIALS = "Client_credentials.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def authenticate_with_console():
    """Authenticate the user manually in headless environments."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS, SCOPES)
    
    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt="consent")
    print("Please visit this URL to authorize the application:")
    print(auth_url)
    
    # Prompt user for the authorization code
    auth_code = input("Enter the authorization code: ").strip()
    
    # Fetch the credentials using the authorization code
    credentials = flow.fetch_token(code=auth_code)
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
