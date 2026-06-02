from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CATEQUISTA', 'Catequista'),
        ('PARTICIPANTE', 'Participante'),
    )

    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('N', 'Prefiero no decirlo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=50, blank=True)
    departamento = models.CharField(max_length=50, blank=True)
    ciudad = models.CharField(max_length=50, blank=True)

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='PARTICIPANTE'
    )

    genero = models.CharField(
        max_length=1,
        choices=GENEROS,
        blank=True
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    qr = models.ImageField(upload_to='qr/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"


class Catequista(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100)
    experiencia = models.IntegerField()

class Participante(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    nombre_tutor = models.CharField(max_length=100, blank=True, null=True)
