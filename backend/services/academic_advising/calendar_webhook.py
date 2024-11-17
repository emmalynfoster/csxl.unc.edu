from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
import uuid

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def subscribe_to_calendar_changes(calendar_id, webhook_url):
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


if __name__ == "__main__":
    calendar_id = "08ed80cb371e555eb93f75e80acd265a11c39bebc7fc58d1049e070beee60b51@group.calendar.google.com"
    webhook_url = "https://sweet-hotels-watch.loca.lt/notifications"  # The URL where you want to receive the notifications
    subscribe_to_calendar_changes(calendar_id, webhook_url)
