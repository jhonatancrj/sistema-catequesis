# prueba_drive.py

from tareas.drive_service import subir_archivo_drive

ruta = "media/test.txt"  # crea este archivo
nombre = "test_subida.txt"

link = subir_archivo_drive(ruta, nombre)

print("Archivo subido:", link)