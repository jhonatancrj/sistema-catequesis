from django.utils.timezone import now

def inscripcion_abierta(curso):
    return now().date() <= curso.fecha_limite_inscripcion
