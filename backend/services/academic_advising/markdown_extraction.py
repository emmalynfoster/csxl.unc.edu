import io
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents.readonly",
]


def retrieve_document(file_id: str):

    """
        Retrieve the markdown format 
        Args:
            file_id: the document ID of a single google drive file of MIME type 'application/vnd.google-apps.document'. 
            This can be found in the route when the document is open and the sharing file link.
        
        Returns:
            An array containing the contents of the file parsed by header exported to markdown formatting. 
    """

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # creates drive api client
        service = build("drive", "v3", credentials=creds)
    
        return parse_markdown(export_markdown(file_id, service))
    
    except HttpError as error:
        print(f"An error occurred: {error}")

        return None


def retrieve_documents(folder_id):  # type: ignore
    """
    Parses through a folder and extracts the data from each file based on MIME types. 
    Accepted MIME types include document and shortcut.

    Args:
        folder_id: ID of the target Google Drive folder, which can be found in the route/share link of the folder.
    
    Returns:
        A list of dictionaries, each representing a document with its metadata and structured sections.
    """

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Creates the Drive API client
    service = build("drive", "v3", credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, fields="files").execute()
    files = results.get("files", [])

    parsed_files = []

    for file in files:
        mimeType = file.get("mimeType")
        document_id = None
        markdown = None

        # Different handlers to extract file ID based on MIME type
        if mimeType == "application/vnd.google-apps.shortcut":
            document_id = file["shortcutDetails"]["targetId"]
            markdown = export_markdown(file["shortcutDetails"]["targetId"], service)
            # handle case for getting and ID from a shortcut

        if mimeType == "application/vnd.google-apps.document":
            document_id = file["id"]
            markdown = export_markdown(file["id"], service)

        if markdown:
            parsed_sections = parse_markdown(markdown)

            # Transform parsed data into the required structure
            structured_data = {
                "title": file["name"],
                "link": f"https://docs.google.com/document/d/{document_id}",
                "sections": [
                    {
                        "title": section[0].strip(),  # Include header format (e.g., #, ##)
                        "content": section[1].strip(),
                    }
                    for section in parsed_sections
                ],
            }

            parsed_files.append(structured_data)

    return parsed_files



def export_markdown(file_id, service): # type: ignore
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


def parse_markdown(markdown): # type: ignore
    """Parse markdown content by extracting headers and their content."""

    pattern = r"^(#{1,6}\s.+?)(?=\n#{1,6}\s|$)(.*?)(?=\n#{1,6}\s|\Z)"

    matches = re.findall(pattern, markdown, re.DOTALL | re.MULTILINE)

    parsed_data = []
    for header, body in matches:
        header = header.strip()
        body = body.strip()

        parsed_data.append([header, body])

    return parsed_data
    