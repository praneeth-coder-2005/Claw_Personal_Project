import os
import pickle
from webbrowser import open_new

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Path to your client credentials JSON file
CREDENTIALS_FILE = 'credentials.json'  # Replace with the actual file name

def authenticate():
    """Authenticates with the Blogger API and returns the service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')
            open_new(auth_url)  # Open the authorization URL in a new browser window
            authorization_response = input(
                "Enter the authorization response URL: "
            )
            flow.fetch_token(authorization_response=authorization_response)
            creds = flow.credentials
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # We're not building the service yet, just authenticating
    # return build("blogger", "v3", credentials=creds)  

if __name__ == "__main__":
    authenticate()
    print("Authentication complete. token.pickle file generated.")
        
