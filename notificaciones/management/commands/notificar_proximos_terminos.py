from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from tareas.models import Tarea, EntregaTarea
from cuestionario.models import Cuestionario, Intento
from cursos.models import Inscripcion
from notificaciones.models import Notificacion, TipoNotificacion, CanalNotificacion
from notificaciones.services import NotificacionService


class Command(BaseCommand):
    help = 'Envía notificaciones de tareas y cuestionarios próximos a terminar (falta menos de 1 hora)'

    def handle(self, *args, **options):
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)

        # ===== Tareas próximas a terminar =====
        tareas = Tarea.objects.filter(
            fecha_limite__gte=now,
            fecha_limite__lte=one_hour_later
        )

        for tarea in tareas:
            # Notificar a los participantes que aún no han entregado
            participantes_sin_entregar = Inscripcion.objects.filter(
                curso=tarea.curso,
                estado='ACTIVA'
            ).exclude(
                usuario__entregatareas__tarea=tarea
            ).values_list('usuario_id', flat=True)

            for usuario_id in participantes_sin_entregar:
                usuario = User.objects.get(id=usuario_id)
                
                # Verificar si ya existe notificación para esta tarea
                if not Notificacion.objects.filter(
                    usuario=usuario,
                    tipo=TipoNotificacion.TAREA_RECORDATORIO,
                    contenido_type='tarea',
                    contenido_id=tarea.id
                ).exists():
                    
                    notif = Notificacion.objects.create(
                        usuario=usuario,
                        tipo=TipoNotificacion.TAREA_RECORDATORIO,
                        canal=CanalNotificacion.EN_APP,
                        titulo=f"⏰ Faltan {self._minutos_restantes(tarea.fecha_limite)} para entregar: {tarea.titulo}",
                        mensaje=f"La tarea '{tarea.titulo}' vence en aproximadamente 1 hora. Asegúrate de entregarla a tiempo.",
                        contenido_type='tarea',
                        contenido_id=tarea.id,
                        icono='bi-hourglass-split',
                        color='danger'
                    )

                    # Enviar por email
                    try:
                        if usuario.preferencias_notificaciones.email_habilitado:
                            NotificacionService._enviar_email(usuario, notif)
                    except:
                        pass

        # ===== Cuestionarios próximos a terminar =====
        cuestionarios = Cuestionario.objects.filter(
            fecha_limite__gte=now,
            fecha_limite__lte=one_hour_later
        )

        for cuestionario in cuestionarios:
            # Notificar a los participantes que aún no han respondido
            participantes_sin_responder = Inscripcion.objects.filter(
                curso=cuestionario.curso,
                estado='ACTIVA'
            ).exclude(
                usuario__intento__cuestionario=cuestionario
            ).values_list('usuario_id', flat=True)

            for usuario_id in participantes_sin_responder:
                usuario = User.objects.get(id=usuario_id)
                
                # Verificar si ya existe notificación para este cuestionario
                if not Notificacion.objects.filter(
                    usuario=usuario,
                    tipo=TipoNotificacion.CUESTIONARIO_DISPONIBLE,
                    contenido_type='cuestionario',
                    contenido_id=cuestionario.id
                ).exists():
                    
                    notif = Notificacion.objects.create(
                        usuario=usuario,
                        tipo=TipoNotificacion.CUESTIONARIO_DISPONIBLE,
                        canal=CanalNotificacion.EN_APP,
                        titulo=f"⏰ Faltan {self._minutos_restantes(cuestionario.fecha_limite)} para responder: {cuestionario.titulo}",
                        mensaje=f"El cuestionario '{cuestionario.titulo}' vence en aproximadamente 1 hora. Apresúrate a responderlo.",
                        contenido_type='cuestionario',
                        contenido_id=cuestionario.id,
                        icono='bi-hourglass-split',
                        color='danger'
                    )

                    # Enviar por email
                    try:
                        if usuario.preferencias_notificaciones.email_habilitado:
                            NotificacionService._enviar_email(usuario, notif)
                    except:
                        pass

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Notificaciones de último minuto enviadas. '
                f'Tareas próximas: {tareas.count()}, '
                f'Cuestionarios próximos: {cuestionarios.count()}'
            )
        )

    def _minutos_restantes(self, fecha):
        """Calcula minutos restantes"""
        diff = fecha - timezone.now()
        minutos = int(diff.total_seconds() / 60)
        return f"{minutos} minutos"
