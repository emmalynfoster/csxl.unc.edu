"""
The Webhook Service allows the API to manipulate webhook data in the database.
"""

from google.oauth2.service_account import Credentials
from backend.services.academic_advising.drop_in import DropInService
from backend.services.academic_advising.document_services import DocumentService
from googleapiclient.discovery import build
import uuid
from fastapi import Request

__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly",
]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
calendar_id = "cs.unc.edu_340oonr4ec26n1fo9l854r3ip8@group.calendar.google.com"
folder_id = "1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"
webhook_url = "https://csxl-advising.apps.cloudapps.unc.edu/api/webhook/notifications"  # May need it to make it so that only google can send to the url / 423 students cant spam it in the /docs/


class WebhookService:
    """Service that performs all webhook actions"""

    def __init__(self):
        self.drive_channel_id = None
        self.calendar_channel_id = None

    def subscribe_to_document_and_calendar_changes(self):
        drive_service = build("drive", "v3", credentials=creds)
        calendar_service = build("calendar", "v3", credentials=creds)
        # Create unique ID for webhook channel
        self.drive_channel_id = str(uuid.uuid4())
        self.calendar_channel_id = str(uuid.uuid4())
        # Set up Drive webhook channel request
        drive_request_body = {
            "id": self.drive_channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "params": {
                "ttl": "2592000"  # Channel expiration (optional, 30 days in seconds)
            },
        }

        # Watch Drive folder
        try:
            drive_service.files().watch(
                fileId=folder_id, body=drive_request_body
            ).execute()
            print(f"Drive folder subscription created: {self.drive_channel_id}")
        except Exception as e:
            print(f"Error subscribing to Drive folder: {e}")

        # Set up Calendar webhook channel request
        calendar_request_body = {
            "id": self.calendar_channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "params": {
                "ttl": "2592000"  # Channel expiration (optional, 30 days in seconds)
            },
        }

        # Watch Calendar events
        try:
            calendar_service.events().watch(
                calendarId=calendar_id, body=calendar_request_body
            ).execute()
            print(f"Calendar subscription created: {self.calendar_channel_id}")
        except Exception as e:
            print(f"Error subscribing to Calendar events: {e}")

    def notification_handler(self, request):
        # Identifies the type of notification
        channel_id = request.headers.get("X-Goog-Channel-ID")
        # Debugging: Print channel ID for inspection
        print(f"Channel ID: {channel_id}")

        # Handle Calendar notifications
        if channel_id == self.calendar_channel_id:
            drop_in_service = DropInService()
            drop_in_service.reset_drop_ins()
            print(f"Updated Calendar Events: {drop_in_service.all()}")

        # Handle Drive notifications
        elif channel_id == self.drive_channel_id:
            document_service = DocumentService()
            # Fetch updated document data
            document_service.refresh_documents()
            print("Documents successfully refreshed in the database.")
        else:
            print("Unknown channel ID received.")
            return "", 404
        return "", 200  # Return 200 OK to acknowledge receipt
