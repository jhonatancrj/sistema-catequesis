from django.db import models
from django.contrib.auth.models import User
from cursos.models import Clase  # ajusta según tu app
from django.utils import timezone

class Tarea(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()

    # 🔥 NUEVO
    permitir_tardia = models.BooleanField(default=False)
    fecha_limite_tardia = models.DateTimeField(null=True, blank=True)

    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    catequista = models.ForeignKey(User, on_delete=models.CASCADE)

    def esta_vencida(self):
        return timezone.now() > self.fecha_entrega

    def puede_entregar(self):
        ahora = timezone.now()

        if ahora <= self.fecha_entrega:
            return True

        if self.permitir_tardia and self.fecha_limite_tardia:
            return ahora <= self.fecha_limite_tardia

        return False


class EntregaTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)

    archivo_url = models.URLField(null=True, blank=True)
    archivo_nombre = models.CharField(max_length=255, blank=True)

    fecha_entrega = models.DateTimeField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacion = models.TextField(blank=True)  
    
#notificaciones
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mensaje
    
class MaterialTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='materiales')
    archivo_url = models.URLField()
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    
class ArchivoEntrega(models.Model):
    entrega = models.ForeignKey(EntregaTarea, on_delete=models.CASCADE, related_name='archivos')
    archivo_url = models.URLField()
    nombre = models.CharField(max_length=255)

from django.utils import timezone

