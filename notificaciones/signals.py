"""
Signals para generar notificaciones automáticamente cuando ocurren eventos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from cursos.models import Curso, Clase, Inscripcion
from tareas.models import Tarea, EntregaTarea
from cuestionario.models import Cuestionario, Intento
from aprobaciones.models import ResultadoCurso

from .models import TipoNotificacion, CanalNotificacion, Notificacion
from .services import NotificacionService


# ============================================================================
# Notificaciones de Cursos
# ============================================================================

@receiver(post_save, sender=Curso)
def notificar_curso_creado(sender, instance, created, **kwargs):
    """Notificar cuando se crea un nuevo curso"""
    if created:
        usuarios = User.objects.filter(
            perfil__rol__in=['ADMIN', 'CATEQUISTA']
        ).distinct()

        for usuario in usuarios:
            Notificacion.objects.create(
                usuario=usuario,
                tipo=TipoNotificacion.CURSO_CREADO,
                canal=CanalNotificacion.EN_APP,
                titulo=f"Nuevo Curso: {instance.nombre}",
                mensaje=f"Se ha creado un nuevo curso: {instance.nombre}",
                contenido_type='curso',
                contenido_id=instance.id,
                icono='bi-book',
                color='info'
            )


# ============================================================================
# Notificaciones de Tareas
# ============================================================================

@receiver(post_save, sender=Tarea)
def notificar_tarea_creada(sender, instance, created, **kwargs):
    """Notificar cuando se crea una nueva tarea"""
    if created:
        # Notificar a los participantes del curso
        participantes = Inscripcion.objects.filter(
            curso=instance.clase.curso,
            estado='ACTIVA'
        ).values_list('participante', flat=True)

        for usuario_id in participantes:
            usuario = User.objects.get(id=usuario_id)
            Notificacion.objects.create(
                usuario=usuario,
                tipo=TipoNotificacion.TAREA_RECORDATORIO,
                canal=CanalNotificacion.EN_APP,
                titulo=f"Nueva Tarea: {instance.titulo}",
                mensaje=f"Nueva tarea en {instance.curso.nombre}: {instance.titulo}. Fecha límite: {instance.fecha_limite.strftime('%d/%m/%Y %H:%M')}",
                contenido_type='tarea',
                contenido_id=instance.id,
                icono='bi-exclamation-circle',
                color='warning'
            )
            
            # También enviar por email si está habilitado
            try:
                if usuario.preferencias_notificaciones.email_habilitado:
                    NotificacionService._enviar_email(usuario, Notificacion.objects.get(
                        usuario=usuario,
                        contenido_id=instance.id,
                        contenido_type='tarea'
                    ))
            except:
                pass


@receiver(post_save, sender=EntregaTarea)
def notificar_tarea_entregada(sender, instance, created, **kwargs):
    """Notificar al catequista cuando se entrega una tarea"""
    if created:
        catequistas = instance.tarea.clase.curso.catequistas.all()
        
        for catequista in catequistas:
            if catequista.user:
                notif = Notificacion.objects.create(
                    usuario=catequista.user,
                    tipo=TipoNotificacion.TAREA_RECORDATORIO,  # Reutilizamos pero con otro nombre
                    canal=CanalNotificacion.EN_APP,
                    titulo=f"✓ Tarea Entregada: {instance.tarea.titulo}",
                    mensaje=f"{instance.estudiante.get_full_name() or instance.estudiante.username} entregó la tarea '{instance.tarea.titulo}' en {instance.tarea.clase.curso.nombre}",
                    contenido_type='entrega_tarea',
                    contenido_id=instance.id,
                    icono='bi-check-circle',
                    color='success'
                )
                
                # También enviar por email si está habilitado
                try:
                    if catequista.user.preferencias_notificaciones.email_habilitado:
                        NotificacionService._enviar_email(catequista.user, notif)
                except:
                    pass


# ============================================================================
# Notificaciones de Cuestionarios
# ============================================================================

@receiver(post_save, sender=Cuestionario)
def notificar_cuestionario_disponible(sender, instance, created, **kwargs):
    """Notificar cuando se crea un nuevo cuestionario"""
    if created:
        # Notificar a los participantes del curso
        participantes = Inscripcion.objects.filter(
            curso=instance.clase.curso,
            estado='ACTIVA'
        ).values_list('participante', flat=True)

        for usuario_id in participantes:
            usuario = User.objects.get(id=usuario_id)
            Notificacion.objects.create(
                usuario=usuario,
                tipo=TipoNotificacion.CUESTIONARIO_DISPONIBLE,
                canal=CanalNotificacion.EN_APP,
                titulo=f"Nuevo Cuestionario: {instance.titulo}",
                mensaje=f"Nuevo cuestionario en {instance.curso.nombre}: {instance.titulo}. Disponible hasta: {instance.fecha_limite.strftime('%d/%m/%Y %H:%M') if instance.fecha_limite else 'sin límite'}",
                contenido_type='cuestionario',
                contenido_id=instance.id,
                icono='bi-pencil-square',
                color='primary'
            )
            
            try:
                if usuario.preferencias_notificaciones.email_habilitado:
                    NotificacionService._enviar_email(usuario, Notificacion.objects.get(
                        usuario=usuario,
                        contenido_id=instance.id,
                        contenido_type='cuestionario'
                    ))
            except:
                pass


@receiver(post_save, sender=Intento)
def notificar_cuestionario_respondido(sender, instance, created, **kwargs):
    """Notificar al catequista cuando se responde un cuestionario"""
    if created:
        catequistas = instance.cuestionario.clase.curso.catequistas.all()
        
        for catequista in catequistas:
            if catequista.user:
                notif = Notificacion.objects.create(
                    usuario=catequista.user,
                    tipo=TipoNotificacion.CUESTIONARIO_DISPONIBLE,
                    canal=CanalNotificacion.EN_APP,
                    titulo=f"✓ Cuestionario Respondido: {instance.cuestionario.titulo}",
                    mensaje=f"{instance.usuario.get_full_name() or instance.usuario.username} respondió el cuestionario '{instance.cuestionario.titulo}' en {instance.cuestionario.clase.curso.nombre}",
                    contenido_type='intento_cuestionario',
                    contenido_id=instance.id,
                    icono='bi-check-circle',
                    color='success'
                )
                
                try:
                    if catequista.user.preferencias_notificaciones.email_habilitado:
                        NotificacionService._enviar_email(catequista.user, notif)
                except:
                    pass


# ============================================================================
# Notificaciones de Calificaciones
# ============================================================================

@receiver(post_save, sender=ResultadoCurso)
def notificar_resultado_curso(sender, instance, created, **kwargs):
    """Notificar al participante cuando hay cambios en su calificación"""
    if not created:  # Solo en actualizaciones
        # Notificar al participante
        notif = Notificacion.objects.create(
            usuario=instance.estudiante,
            tipo=TipoNotificacion.CALIFICACION_CAMBIO,
            canal=CanalNotificacion.EN_APP,
            titulo=f"Actualización en {instance.curso.nombre}",
            mensaje=f"Tu calificación en {instance.curso.nombre} ha sido actualizada. Estado: {instance.estado}",
            contenido_type='resultado_curso',
            contenido_id=instance.id,
            icono='bi-check-circle',
            color='success' if instance.estado == 'APROBADO' else 'danger'
        )
        
        try:
            if instance.estudiante.preferencias_notificaciones.email_habilitado:
                NotificacionService._enviar_email(instance.estudiante, notif)
        except:
            pass


# ============================================================================
# Limpieza de notificaciones antiguas
# ============================================================================

@receiver(post_save, sender=User)
def crear_preferencias_notificacion(sender, instance, created, **kwargs):
    """Crear preferencias de notificación para nuevos usuarios"""
    if created:
        from .models import PreferenciaNotificacion
        PreferenciaNotificacion.objects.get_or_create(usuario=instance)

