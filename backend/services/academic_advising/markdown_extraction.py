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


def retrieve_documents(folder_id):

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # create drive api client
    service = build("drive", "v3", credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    parsed_files = []

    for file in files:
        # print(f"Document ID: {file['id']}, Document Name: {file['name']}")

        markdown = export_markdown(file["id"], service)

        # now parse the markdown by header
        if markdown:
            parsed = parse_markdown(markdown)

            # for header, content in parsed:
            #     print(f"Header: {header}\nContent: {content}\n")

        parsed_files += [file["id"], file["name"], parsed]

    return parsed_files


def export_markdown(real_file_id, service):
    """Download a Document file in markdown format.
    Args:
        real_file_id : file ID of any workspace document format file
        service :
    Returns :

    Load pre-authorized user credentials from the environment.
    """
    try:
        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id, mimeType="text/markdown")

        file = io.BytesIO()

        response = request.execute()
        file.write(response)
        file.seek(0)

        markdown_text = file.getvalue().decode("utf-8")
        # print(markdown_text)

        # if response:
        #     directory_path = "documents"
        #     file_name = name
        #     file_path = os.path.join(directory_path, file_name)
        #     with open(file_path, "wb") as md_file:
        #         md_file.write(response)

        #         print(f"Markdown content saved to {file_name}")

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

        # Skip headers with no content
        # if body:

        parsed_data.append([header, body])

    return parsed_data


# if __name__ == "__main__":

#   print(retrieve_documents("1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om"))
