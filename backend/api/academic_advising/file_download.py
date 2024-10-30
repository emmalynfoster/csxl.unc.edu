import io
import os

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'csxl-academic-advising-feature.json'
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents.readonly']

def retrieve_documents(folder_id, creds):

    service = build('drive', 'v3', credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    for file in files:
        print(f"Document ID: {file['id']}, Document Name: {file['name']}")
        export_pdf(file['id'], file['name'], creds)

def export_pdf(real_file_id, name, creds):
  """Download a Document file in PDF format.
  Args:
      real_file_id : file ID of any workspace document format file
  Returns : IO object with location

  Load pre-authorized user credentials from the environment.
  """

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)

    file_id = real_file_id

    data = service.files().export(fileId=file_id, mimeType="application/pdf").execute()
    if data:
        directory_path = 'documents'
        file_name = name
        file_path = os.path.join(directory_path, file_name)
        # assert os.path.isfile(file_path)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(data)

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None


if __name__ == "__main__":
  creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

  retrieve_documents("1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om", creds)
