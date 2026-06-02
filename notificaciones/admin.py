from django.contrib import admin
from django.utils.html import format_html
from .models import Notificacion, PreferenciaNotificacion, NotificacionMasiva


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo_badge', 'leida_badge', 'enviada_badge', 'fecha_creacion')
    list_filter = ('tipo', 'canal', 'leida', 'enviada', 'fecha_creacion')
    search_fields = ('titulo', 'usuario__username', 'usuario__email')
    readonly_fields = ('fecha_creacion', 'fecha_lectura', 'fecha_envio')
    
    fieldsets = (
        ('Información', {
            'fields': ('usuario', 'tipo', 'canal', 'titulo', 'mensaje')
        }),
        ('Relación', {
            'fields': ('contenido_type', 'contenido_id'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('leida', 'enviada')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_lectura', 'fecha_envio'),
            'classes': ('collapse',)
        }),
        ('Estilo', {
            'fields': ('icono', 'color'),
            'classes': ('collapse',)
        }),
    )

    def tipo_badge(self, obj):
        colores = {
            'curso_creado': '#0d6efd',
            'calificacion_cambio': '#198754',
            'tarea_recordatorio': '#ffc107',
            'cuestionario_disponible': '#0dcaf0',
            'cuestionario_cerrado': '#dc3545',
            'clase_programada': '#6c757d',
            'mensaje_recibido': '#0d6efd',
        }
        color = colores.get(obj.tipo, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'

    def leida_badge(self, obj):
        if obj.leida:
            return format_html('<span style="color: green;">✓ Leída</span>')
        return format_html('<span style="color: red;">✗ No leída</span>')
    leida_badge.short_description = 'Leída'

    def enviada_badge(self, obj):
        if obj.enviada:
            return format_html('<span style="color: green;">✓ Enviada</span>')
        return format_html('<span style="color: orange;">⟳ Pendiente</span>')
    enviada_badge.short_description = 'Enviada'


@admin.register(PreferenciaNotificacion)
class PreferenciaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'email_habilitado', 'whatsapp_habilitado', 'sms_habilitado')
    list_filter = ('email_habilitado', 'whatsapp_habilitado', 'sms_habilitado', 'resumen_diario')
    search_fields = ('usuario__username', 'usuario__email')

    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Tipos de Notificaciones', {
            'fields': (
                'cursos_nuevos',
                'calificaciones_cambios',
                'tareas_recordatorios',
                'cuestionarios_eventos',
                'clases_programadas',
                'mensajes_recibidos'
            )
        }),
        ('Canales', {
            'fields': (
                'email_habilitado',
                'whatsapp_habilitado',
                'sms_habilitado'
            )
        }),
        ('Resumen Diario', {
            'fields': ('resumen_diario', 'hora_resumen')
        }),
        ('Datos de Contacto', {
            'fields': ('numero_whatsapp', 'numero_sms'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificacionMasiva)
class NotificacionMasivaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'estado', 'destinatarios_tipo', 'enviadas', 'fallidas', 'fecha_creacion')
    list_filter = ('estado', 'tipo', 'destinatarios_tipo', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje')
    filter_horizontal = ('usuarios',)

    fieldsets = (
        ('Contenido', {
            'fields': ('titulo', 'mensaje', 'tipo')
        }),
        ('Destinatarios', {
            'fields': ('destinatarios_tipo', 'usuarios'),
            'description': 'Si se selecciona "Personalizado", especifique los usuarios. De lo contrario, se enviarán automáticamente.'
        }),
        ('Canales', {
            'fields': ('canales',),
            'description': 'JSON array: ["en_app", "email", "whatsapp", "sms"]'
        }),
        ('Envío', {
            'fields': ('estado', 'fecha_envio_programada')
        }),
        ('Resultados', {
            'fields': ('enviadas', 'fallidas', 'fecha_creacion', 'fecha_envio_real'),
            'classes': ('collapse',)
        }),
    )
