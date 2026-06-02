import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCOPES = ['https://www.googleapis.com/auth/drive.file']

CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')


def get_flow():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:8000/oauth2callback/'
    )
    return flow

from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
import io

def subir_archivo_drive(request, archivo):
    creds_data = request.session.get('credentials')

    if not creds_data:
        return None

    creds = Credentials(**creds_data)

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': archivo.name}

    fh = io.BytesIO(archivo.read())

    media = MediaIoBaseUpload(fh, mimetype=archivo.content_type)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')

    # hacer público
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"