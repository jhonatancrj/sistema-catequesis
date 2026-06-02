from tareas.models import EntregaTarea
from cuestionario.models import Intento
from cursos.models import Asistencia

def calcular_promedio_tareas(usuario, curso):
    tareas = EntregaTarea.objects.filter(id_usuario=usuario, id_tarea__id_clase__id_curso=curso)
    if tareas.exists():
        return sum([t.calificacion for t in tareas]) / tareas.count()
    return 0


def calcular_promedio_cuestionarios(usuario, curso):
    intentos = Intento.objects.filter(id_usuario=usuario, id_cuestionario__id_clase__id_curso=curso)
    if intentos.exists():
        return sum([i.puntaje for i in intentos]) / intentos.count()
    return 0


def contar_faltas(usuario, curso):
    faltas = Asistencia.objects.filter(
        id_usuario=usuario,
        id_clase__id_curso=curso,
        estado='AUSENTE'
    ).count()
    return faltas