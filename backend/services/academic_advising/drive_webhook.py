from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
import uuid

from markdown_extraction import get_document_ids

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def subscribe_to_document_changes(folder_id, webhook_url):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build("drive", "v3", credentials=creds)

    # Create a unique ID for your webhook channel
    channel_id = str(uuid.uuid4())

    # Set up the webhook channel request
    request_body = {
        "id": channel_id,
        "type": "web_hook",
        "address": webhook_url,
        "params": {
            "ttl": "2592000"  # Channel expiration (optional, 30 days in seconds)
        },
    }

    # Subscribe to changes for each document

    files = get_document_ids(folder_id)

    for file in files:
        response = (
            drive_service.files().watch(fileId=file["id"], body=request_body).execute()
        )
        print("Webhook subscription created:", response)


if __name__ == "__main__":
    folder_id = (
        "1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"  # Specify your document ID here
    )
    webhook_url = "https://slick-cycles-grow.loca.lt/notifications"  # Your webhook URL
    subscribe_to_document_changes(folder_id, webhook_url)
