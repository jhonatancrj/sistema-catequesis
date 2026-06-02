import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCOPES = ['https://www.googleapis.com/auth/drive']

SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credenciales.json')


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service


def subir_archivo_drive(ruta_archivo, nombre_archivo):
    service = get_drive_service()

    FOLDER_ID = '1gu6q3HyaSQCmcIuowiQVsQBZjKKlH-vz'

    file_metadata = {
        'name': nombre_archivo,
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(
        ruta_archivo,
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()

    file_id = file.get('id')

    # hacer público
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    link = f"https://drive.google.com/file/d/{file_id}/view"

    return link