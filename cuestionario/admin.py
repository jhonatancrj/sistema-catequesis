from django.contrib import admin
from .models import Cuestionario, Pregunta, Opcion, Intento, Respuesta
class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 2

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'tipo', 'puntaje', 'cuestionario')
    list_filter = ('tipo', 'cuestionario')
    search_fields = ('enunciado',)

    inlines = [OpcionInline]

class PreguntaInline(admin.StackedInline):
    model = Pregunta
    extra = 1
    show_change_link = True

class CuestionarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'clase', 'catequista', 'fecha_limite', 'es_unico')
    list_filter = ('clase', 'es_unico')
    search_fields = ('titulo', 'descripcion')

    inlines = [PreguntaInline]

class IntentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cuestionario', 'puntaje', 'fecha')
    list_filter = ('cuestionario', 'fecha')
    search_fields = ('usuario__username',)

class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('intento', 'pregunta', 'texto', 'opcion')
    list_filter = ('pregunta',)

    admin.site.register(Cuestionario, CuestionarioAdmin)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(Opcion)
admin.site.register(Intento, IntentoAdmin)
admin.site.register(Respuesta, RespuestaAdmin)