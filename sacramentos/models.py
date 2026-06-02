from django.db import models

from usuarios.models import Perfil


# ===================================
# CATÁLOGO SACRAMENTOS
# ===================================

class Sacramento(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return self.nombre


# ===================================
# REGISTRO SACRAMENTAL
# ===================================

class RegistroSacramental(models.Model):

    participante = models.ForeignKey(

        Perfil,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        limit_choices_to={
            'rol': 'PARTICIPANTE'
        }
    )

    # ===================================
    # DATOS MANUALES
    # ===================================

    nombre_manual = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    apellido_manual = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    # ===================================
    # SACRAMENTO
    # ===================================

    sacramento = models.ForeignKey(

        Sacramento,

        on_delete=models.SET_NULL,

        null=True
    )

    # ===================================
    # DATOS SACRAMENTALES
    # ===================================

    fecha_sacramento = models.DateField()

    lugar_sacramento = models.CharField(
        max_length=255
    )

    parroco = models.CharField(
        max_length=255
    )

    # ===================================
    # BAUTIZO
    # ===================================

    fecha_bautizo = models.DateField(
        null=True,
        blank=True
    )

    # ===================================
    # PADRES
    # ===================================

    nombre_padre = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nombre_madre = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # ===================================
    # PADRINOS
    # ===================================

    padrino = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    madrina = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # ===================================
    # FECHA REGISTRO
    # ===================================

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        if self.participante:

            return (

                f"{self.participante.user.first_name} "
                f"{self.participante.user.last_name}"
            )

        return (
            f"{self.nombre_manual} "
            f"{self.apellido_manual}"
        )