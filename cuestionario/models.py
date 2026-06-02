from django.db import models
from django.contrib.auth.models import User
from cursos.models import Clase


class Cuestionario(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    catequista = models.ForeignKey(User, on_delete=models.CASCADE)

    tiempo_limite = models.IntegerField(null=True, blank=True)  # minutos
    es_unico = models.BooleanField(default=True)

    fecha_limite = models.DateTimeField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Pregunta(models.Model):
    TIPOS = (
        ('multiple', 'Opción única'),
        ('checkbox', 'Casillas'),
        ('texto', 'Respuesta corta'),
    )

    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE)
    enunciado = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    puntaje = models.IntegerField(default=1)

    retroalimentacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.enunciado


class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto = models.CharField(max_length=200)
    es_correcta = models.BooleanField(default=False)


class Intento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE)
    puntaje = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)


class Respuesta(models.Model):
    intento = models.ForeignKey(Intento, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto = models.TextField(null=True, blank=True)
    opcion = models.ForeignKey(Opcion, null=True, blank=True, on_delete=models.CASCADE)