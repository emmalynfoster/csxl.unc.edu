from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests

SERVICE_ACCOUNT_FILE = 'csxl-academic-advising-feature.json'
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']

def subscribe_to_folder_changes(folder_id, webhook_url):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    # Create a unique ID for your webhook channel
    channel_id = "727a5eaf-0b0d-426a-b7ba-fb59dedda7e8"  # You can generate a unique identifier for this

    # Set up the webhook channel request
    request_body = {
        "id": channel_id,
        "type": "web_hook",
        "address": webhook_url,
        "params": {
            "ttl": "2592000"  # Channel expiration (optional, 30 days in seconds), we need to look into auto-renewing subscription
        }
    }

    # Subscribe to changes for the specified folder
    response = drive_service.files().watch(fileId=folder_id, body=request_body).execute()
    print("Webhook subscription created:", response)

if __name__ == "__main__":
    folder_id = '1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om' 
    # ngrok sessions expire after several hours on the free plan. 
    # If you restart ngrok, it will generate a new URL, so you’ll need to update your webhook subscription with the new URL.
    # When moving to production, you'll want a consistent public URL, provided by a hosting service (e.g., AWS, Heroku).
    webhook_url = 'https://nine-stars-attend.loca.lt/notifications' 
    subscribe_to_folder_changes(folder_id, webhook_url)