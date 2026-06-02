from django.contrib import admin
from .models import Perfil, Catequista, Participante

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'telefono', 'fecha_registro')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email')


@admin.register(Catequista)
class CatequistaAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'especialidad', 'experiencia')


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'nombre_tutor')

