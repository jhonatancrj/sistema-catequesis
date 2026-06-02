from django.db import models

from usuarios.models import Perfil

from cursos.models import Curso

from sacramentos.models import Sacramento


class ResultadoCurso(models.Model):

    ESTADOS = (

        ('APROBADO', 'Aprobado'),

        ('REPROBADO', 'Reprobado'),
    )

    participante = models.ForeignKey(

        Perfil,

        on_delete=models.CASCADE,

        limit_choices_to={
            'rol': 'PARTICIPANTE'
        }
    )

    curso = models.ForeignKey(

        Curso,

        on_delete=models.CASCADE
    )

    sacramento = models.ForeignKey(

        Sacramento,

        on_delete=models.SET_NULL,

        null=True,

        blank=True
    )

    gestion = models.IntegerField()

    promedio_tareas = models.FloatField(
        default=0
    )

    promedio_cuestionarios = models.FloatField(
        default=0
    )

    faltas = models.IntegerField(
        default=0
    )

    estado_final = models.CharField(

        max_length=20,

        choices=ESTADOS
    )

    fecha_resultado = models.DateTimeField(
        auto_now_add=True
    )

    enviado_automaticamente = models.BooleanField(
        default=False
    )

    class Meta:

        unique_together = (
            'participante',
            'curso'
        )

        ordering = [
            '-fecha_resultado'
        ]

    def __str__(self):

        return (

            f"{self.participante.user.username} - "
            f"{self.estado_final}"
        )