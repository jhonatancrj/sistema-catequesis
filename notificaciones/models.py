from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TipoNotificacion(models.TextChoices):
    """Tipos de notificaciones en el sistema"""
    CURSO_CREADO = 'curso_creado', 'Nuevo curso creado'
    CALIFICACION_CAMBIO = 'calificacion_cambio', 'Cambio en calificación/aprobación'
    TAREA_RECORDATORIO = 'tarea_recordatorio', 'Recordatorio de tarea sin entregar'
    CUESTIONARIO_DISPONIBLE = 'cuestionario_disponible', 'Cuestionario disponible'
    CUESTIONARIO_CERRADO = 'cuestionario_cerrado', 'Cuestionario cerrado'
    CLASE_PROGRAMADA = 'clase_programada', 'Clase programada'
    MENSAJE_RECIBIDO = 'mensaje_recibido', 'Nuevo mensaje'


class CanalNotificacion(models.TextChoices):
    """Canales por los que se envían notificaciones"""
    EN_APP = 'en_app', 'En la aplicación'
    EMAIL = 'email', 'Email'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    SMS = 'sms', 'SMS'


class Notificacion(models.Model):
    """Modelo principal de notificaciones"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TipoNotificacion.choices, default=TipoNotificacion.CURSO_CREADO)
    canal = models.CharField(max_length=20, choices=CanalNotificacion.choices, default=CanalNotificacion.EN_APP)
    
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    
    # Relación opcional con objetos del sistema
    contenido_type = models.CharField(max_length=50, blank=True, null=True)  # 'curso', 'tarea', etc.
    contenido_id = models.IntegerField(blank=True, null=True)
    
    leida = models.BooleanField(default=False)
    enviada = models.BooleanField(default=False)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    
    icono = models.CharField(max_length=50, default='bi-bell')  # Bootstrap icon
    color = models.CharField(max_length=20, default='primary')  # Clase Bootstrap

    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['usuario', '-fecha_creacion']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.username}"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()

    def marcar_como_enviada(self):
        """Marca la notificación como enviada por canal externo"""
        self.enviada = True
        self.fecha_envio = timezone.now()
        self.save()


class PreferenciaNotificacion(models.Model):
    """Preferencias de notificaciones por usuario"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferencias_notificaciones')
    
    # Habilitar/deshabilitar por tipo
    cursos_nuevos = models.BooleanField(default=True)
    calificaciones_cambios = models.BooleanField(default=True)
    tareas_recordatorios = models.BooleanField(default=True)
    cuestionarios_eventos = models.BooleanField(default=True)
    clases_programadas = models.BooleanField(default=True)
    mensajes_recibidos = models.BooleanField(default=True)
    
    # Canales preferidos
    email_habilitado = models.BooleanField(default=True)
    whatsapp_habilitado = models.BooleanField(default=False)
    sms_habilitado = models.BooleanField(default=False)
    
    # Horarios
    resumen_diario = models.BooleanField(default=False, help_text="Recibir resumen diario en lugar de notificaciones individuales")
    hora_resumen = models.TimeField(default='09:00', help_text="Hora para recibir el resumen diario")
    
    # Contacto para canales externos
    numero_whatsapp = models.CharField(max_length=20, blank=True, help_text="+506 XXXX XXXX")
    numero_sms = models.CharField(max_length=20, blank=True, help_text="+506 XXXX XXXX")
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Preferencias de notificaciones"

    def __str__(self):
        return f"Preferencias - {self.usuario.username}"


class NotificacionMasiva(models.Model):
    """Para enviar notificaciones a múltiples usuarios"""
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('programada', 'Programada'),
        ('enviando', 'Enviando'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=30, choices=TipoNotificacion.choices)
    canales = models.CharField(max_length=100)  # JSON: ["en_app", "email", "whatsapp"]
    
    usuarios = models.ManyToManyField(User, blank=True, related_name='notificaciones_masivas')
    destinatarios_tipo = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Administradores'),
            ('catequista', 'Catequistas'),
            ('participante', 'Participantes'),
            ('todos', 'Todos'),
            ('custom', 'Personalizado'),
        ],
        default='todos'
    )
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio_programada = models.DateTimeField(blank=True, null=True)
    fecha_envio_real = models.DateTimeField(blank=True, null=True)
    
    enviadas = models.IntegerField(default=0)
    fallidas = models.IntegerField(default=0)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"
