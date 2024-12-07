import io
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from backend.env import getenv


# During testing (outside of stage branch) bring the credentials .json to the root directory, and make sure it is included in the .gitignore
# SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"

# For deployment (on stage branch) establish the .json as an environmental variable in the cloudapps deployment and retrieve the credentials from the environement.
SERVICE_ACCOUNT_FILE = getenv("GOOGLE-CREDS")

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
        if mimeType == "application/vnd.google-apps.document":
            document_id = file["id"]
            markdown = export_markdown(file["id"], service)

        if markdown:
            parsed_sections = parse_markdown(markdown)

            # Filter out sections containing anchors in the body
            parsed_sections = [
                section for section in parsed_sections if not contains_anchor_in_content(section[1])
            ]

            # Transform parsed data into the required structure
            structured_data = {
                "title": file["name"],
                "link": f"https://docs.google.com/document/d/{document_id}",
                "sections": [
                    {
                        "title": remove_anchor_from_title(section[0]),  # Remove anchor formatting from title
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


def contains_anchor_in_content(content: str) -> bool:
    """Check if the content contains any Markdown anchor references (e.g., {#anchor-id})"""
    return bool(re.search(r'\[.*\]\(#\S*\)', content))

def remove_anchor_from_title(title: str) -> str:
    """Remove anchor formatting from title (e.g., {#anchor-id})"""
    return re.sub(r"{#\S+}", "", title)



if __name__ == "__main__":
   print(retrieve_documents("1fAwD7P4MVDDza_7qKL5fTuXi0pJgOGZ4"))
    