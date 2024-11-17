from flask import Flask, request
from doc_retrieval import retrieve_document_ids
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Set your Google credentials file and folder ID
SERVICE_ACCOUNT_FILE = 'csxl-academic-advising-feature.json'
folder_id = '1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om'

@app.route('/notifications', methods=['POST'])
def notifications():
    # Check if it's a valid notification
    resource_state = request.headers.get('X-Goog-Resource-State')

    # If the resource state indicates a folder update, call the document retrieval functions
    if resource_state == 'update':
        print("Change detected in Google Drive folder.")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])
        retrieve_document_ids(folder_id, creds)

    return '', 200  # Return 200 OK to acknowledge receipt

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)