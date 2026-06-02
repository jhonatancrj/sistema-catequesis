from django.contrib import admin
from .models import Curso, Inscripcion


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'fecha_inicio',
        'fecha_fin',
        'fecha_limite_inscripcion',
        'estado',
        'fecha_creacion'
    )

    search_fields = ('nombre', 'descripcion')

    list_filter = (
        'estado',
        'fecha_inicio',
        'fecha_fin'
    )

    filter_horizontal = ('catequistas',)


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'participante',
        'curso',
        'fecha_inscripcion',
        'estado'
    )

    list_filter = (
        'estado',
        'curso'
    )

    search_fields = (
        'participante__user__username',
        'curso__nombre'
    )