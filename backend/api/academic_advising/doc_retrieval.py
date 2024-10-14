from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'csxl-academic-advising-feature.json'
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/documents.readonly']

def retrieve_document_ids(folder_id, creds):

    service = build('drive', 'v3', credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    for file in files:
        print(f"Document ID: {file['id']}, Document Name: {file['name']}")
        print(get_document_content(file['id'], creds))


def get_document_content(document_id, creds):

    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=document_id).execute()

    text = ''
    for element in document.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for paragraph_element in element['paragraph'].get('elements', []):
                if 'textRun' in paragraph_element:
                    text += paragraph_element['textRun'].get('content', '')
    
    return text



if __name__ == '__main__':

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    retrieve_document_ids('1VqezCSGlXiztKeYOoMSN1l25idYlZ7Om', creds)