import qrcode
from io import BytesIO
from django.core.files import File

def generar_qr_usuario(perfil):

    data = str(perfil.id)

    qr = qrcode.make(data)

    buffer = BytesIO()
    qr.save(buffer, format='PNG')

    nombre_archivo = f'qr_{perfil.id}.png'

    perfil.qr.save(nombre_archivo, File(buffer), save=True)