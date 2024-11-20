from flask import Flask, jsonify, request
from markdown_extraction import retrieve_document
from google.oauth2.service_account import Credentials
from calendar_retrieval import (
    retrieve_calendar_event,
)  # Import the function to retrieve calendar events

app = Flask(__name__)

# Set your Google credentials file and document ID
SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
document_id = "1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"  # Specify the document ID you want to track


@app.route("/notifications", methods=["POST"])
def notifications():
    # Print the incoming request body for debugging
    print("Request Body:", request.get_data())

    # Get the resource state (this can help determine if it's a Google Calendar or Google Drive event)
    resource_state = request.headers.get("X-Goog-Resource-State")
    resource_id = request.headers.get("X-Goog-Resource-ID")

    print(f"Resource State: {resource_state}, Resource ID: {resource_id}")

    # If the resource state indicates a document update, call the document retrieval function
    if resource_state == "update" and resource_id == "ygSz8V6TC_qXp3KUyMP22QxyBt4":
        print(f"Change detected in document with ID: {document_id}")
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
        )
        # print(retrieve_document(document_id))

    # If the event is related to Google Calendar
    elif resource_id == "EYJsStzAQ9YDxcmsfYkmdrr58Cs":
        print(f"Change detected in calendar event with ID: {resource_id}")
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )
        calendar_event_data = retrieve_calendar_event(
            resource_id, creds
        )  # Fetch updated event
        print("Calendar Event Data:", calendar_event_data)

    return "", 200  # Return 200 OK to acknowledge receipt


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
