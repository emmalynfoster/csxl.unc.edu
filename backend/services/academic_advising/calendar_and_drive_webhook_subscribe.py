from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
import uuid

from .markdown_extraction import get_document_ids

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar",
]

calendar_id = "cs.unc.edu_340oonr4ec26n1fo9l854r3ip8@group.calendar.google.com"
folder_id = "1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"
webhook_url = "https://csxl.unc.edu/api/webhook"


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


def subscribe_to_calendar_changes(calendar_id, webhook_url):  # type: ignore
    # Authenticate using service account
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    calendar_service = build("calendar", "v3", credentials=creds)

    # Create a unique ID for your webhook channel
    channel_id = str(uuid.uuid4())

    # Set up the webhook channel request
    request_body = {
        "id": channel_id,
        "type": "web_hook",
        "address": webhook_url,
        "params": {
            "ttl": "2592000"  # Channel expiration (optional, 30 days in seconds), you need to look into auto-renewing subscription
        },
    }

    # Subscribe to changes for the specified calendar
    response = (
        calendar_service.events()
        .watch(calendarId=calendar_id, body=request_body)
        .execute()
    )
    print("Webhook subscription created:", response)
