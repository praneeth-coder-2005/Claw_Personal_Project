import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set the path to the service account file (service.json)
SERVICE_ACCOUNT_FILE = 'service.json'

# Set the required scopes for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Authenticate using the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Blogger API client
service = build('blogger', 'v3', credentials=credentials)

# Make an API request (for example, list blogs for the authenticated user)
request = service.blogs().listByUser(userId='self')
response = request.execute()

# Print the response from the API
print(response)
