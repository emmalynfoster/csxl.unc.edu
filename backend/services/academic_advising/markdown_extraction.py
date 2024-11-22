import io

# import os
import re

# import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents.readonly",
]


def retrieve_document(file_id):

    """
        Retrieve the markdown format given
    """

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # create drive api client
    service = build("drive", "v3", credentials=creds)
    
    return parse_markdown(export_markdown(file_id, service))

def retrieve_documents(folder_id):

    """
        Parses through a folder and extracts the data based on MIME types, accepted types include document, shortcut

        Args:
            folder_id: ID of the target Google Drive folder, which can be found in 
    """

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # create drive api client
    service = build("drive", "v3", credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, fields="files").execute()
    files = results.get("files", [])

    parsed_files = []

    for file in files:
        mimeType = file.get("mimeType")

        # print(mimeType)
        # print(file)
        # print(file['shortcutDetails']['targetId'])

        markdown = None

        # Different handlers to extract file id based on MIME type
        if mimeType == 'application/vnd.google-apps.shortcut':
            markdown = export_markdown(file['shortcutDetails']['targetId'], service)
        
        if mimeType == 'application/vnd.google-apps.document':
            markdown = export_markdown(file["id"], service)

        if markdown:
                parsed = parse_markdown(markdown)

                # for header, content in parsed:
                #     print(f"Header: {header}\nContent: {content}\n")

                parsed_files += [file["id"], file["name"], parsed]    


    return parsed_files


def export_markdown(file_id, service):
    """Download a Document file in markdown format.
    Args:
        file_id : file ID of a 'application/vnd.google-apps.document' MIME type file
        service : drive api client
    Returns : 
        the contents of the document in markdown format, as bytes

    Load pre-authorized user credentials from the environment.
    """
    try:

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id, mimeType="text/markdown")

        file = io.BytesIO()

        response = request.execute()
        file.write(response)
        file.seek(0)

        markdown_text = file.getvalue().decode("utf-8")

        return markdown_text

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.getvalue()


def parse_markdown(markdown):
    """Parse markdown content by extracting headers and their content."""

    pattern = r"^(#{1,6}\s.+?)(?=\n#{1,6}\s|$)(.*?)(?=\n#{1,6}\s|\Z)"

    matches = re.findall(pattern, markdown, re.DOTALL | re.MULTILINE)

    parsed_data = []
    for header, body in matches:
        header = header.strip()
        body = body.strip()

        parsed_data.append([header, body])

    return parsed_data


if __name__ == "__main__":

    print(retrieve_documents("1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"))
    # print(retrieve_documents("1fAwD7P4MVDDza_7qKL5fTuXi0pJgOGZ4"))
