from django.contrib import admin

from .models import ResultadoCurso


@admin.register(ResultadoCurso)
class ResultadoCursoAdmin(admin.ModelAdmin):

    list_display = (

        'participante',

        'curso',

        'sacramento',

        'estado_final',

        'gestion',

        'fecha_resultado'
    )

    search_fields = (

        'participante__user__first_name',

        'participante__user__last_name',

        'curso__nombre'
    )

    list_filter = (

        'estado_final',

        'gestion',

        'sacramento'
    )