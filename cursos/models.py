from django.db import models
from usuarios.models import Perfil
from sacramentos.models import Sacramento

class Curso(models.Model):
    ESTADOS = (
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('FINALIZADO', 'Finalizado'),
    )

    nombre = models.CharField(max_length=150)
    imagen = models.ImageField(
        upload_to='cursos/',
        null=True,
        blank=True
    )
    descripcion = models.TextField()

    sacramento = models.ForeignKey(
        Sacramento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    lista_enviada = models.BooleanField(default=False)
    fecha_envio_lista = models.DateTimeField(null=True, blank=True)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_limite_inscripcion = models.DateField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='ACTIVO'
    )

    catequistas = models.ManyToManyField(
        Perfil,
        limit_choices_to={'rol': 'CATEQUISTA'},
        related_name='cursos'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

from django.db import models
from usuarios.models import Perfil
from .models import Curso

class Inscripcion(models.Model):
    ESTADOS = (
        ('INSCRITO', 'Inscrito'),
        ('CANCELADO', 'Cancelado'),
    )

    participante = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'PARTICIPANTE'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='INSCRITO'
    )

    class Meta:
        unique_together = ('participante', 'curso')

    def __str__(self):
        return f"{self.participante.user.username} - {self.curso.nombre}"

class Clase(models.Model):

    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='clases'
    )

    titulo = models.CharField(max_length=200, default='Clase')

    descripcion = models.TextField(blank=True)

    fecha = models.DateField()

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.curso.nombre} - {self.titulo}"
    

## asistencia##
class Asistencia(models.Model):

    ESTADOS = (
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('PERMISO', 'Permiso'),
    )

    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )

    participante = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'PARTICIPANTE'}
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS
    )

    observacion = models.TextField(blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('clase', 'participante')

    def __str__(self):
        return f"{self.participante.user.username} - {self.estado}"