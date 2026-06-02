import json
import logging
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notificacion, PreferenciaNotificacion, CanalNotificacion, TipoNotificacion

logger = logging.getLogger(__name__)


class NotificacionService:
    """Servicio centralizado para crear y gestionar notificaciones"""

    # Configuración de iconos y colores por tipo
    CONFIG_NOTIFICACIONES = {
        TipoNotificacion.CURSO_CREADO: {
            'icono': 'bi-book',
            'color': 'info',
            'titulo_default': 'Nuevo Curso'
        },
        TipoNotificacion.CALIFICACION_CAMBIO: {
            'icono': 'bi-check-circle',
            'color': 'success',
            'titulo_default': 'Actualización de Calificación'
        },
        TipoNotificacion.TAREA_RECORDATORIO: {
            'icono': 'bi-exclamation-circle',
            'color': 'warning',
            'titulo_default': 'Recordatorio de Tarea'
        },
        TipoNotificacion.CUESTIONARIO_DISPONIBLE: {
            'icono': 'bi-pencil-square',
            'color': 'primary',
            'titulo_default': 'Cuestionario Disponible'
        },
        TipoNotificacion.CUESTIONARIO_CERRADO: {
            'icono': 'bi-lock',
            'color': 'danger',
            'titulo_default': 'Cuestionario Cerrado'
        },
        TipoNotificacion.CLASE_PROGRAMADA: {
            'icono': 'bi-calendar-event',
            'color': 'secondary',
            'titulo_default': 'Clase Programada'
        },
        TipoNotificacion.MENSAJE_RECIBIDO: {
            'icono': 'bi-chat-dots',
            'color': 'primary',
            'titulo_default': 'Nuevo Mensaje'
        },
    }

    @staticmethod
    def crear_notificacion(
        usuarios,
        tipo,
        titulo,
        mensaje,
        canales=None,
        contenido_type=None,
        contenido_id=None,
        icono=None,
        color=None
    ):
        """
        Crear notificación para uno o varios usuarios
        
        Args:
            usuarios: User o lista de User
            tipo: TipoNotificacion
            titulo: str
            mensaje: str
            canales: lista de CanalNotificacion (default: ['en_app', 'email'])
            contenido_type: str (opcional)
            contenido_id: int (opcional)
            icono: str (opcional, default según tipo)
            color: str (opcional, default según tipo)
        """
        if canales is None:
            canales = [CanalNotificacion.EN_APP, CanalNotificacion.EMAIL]

        if not isinstance(usuarios, list):
            usuarios = [usuarios]

        # Obtener configuración por tipo
        config = NotificacionService.CONFIG_NOTIFICACIONES.get(tipo, {})
        if icono is None:
            icono = config.get('icono', 'bi-bell')
        if color is None:
            color = config.get('color', 'primary')

        notificaciones_creadas = []

        for usuario in usuarios:
            # Verificar preferencias del usuario
            try:
                preferencias = usuario.preferencias_notificaciones
            except PreferenciaNotificacion.DoesNotExist:
                # Crear preferencias por defecto
                preferencias = PreferenciaNotificacion.objects.create(usuario=usuario)

            # Verificar si el usuario quiere recibir este tipo de notificación
            if not NotificacionService._verificar_preferencias(tipo, preferencias):
                continue

            for canal in canales:
                # Crear notificación en BD
                notif = Notificacion.objects.create(
                    usuario=usuario,
                    tipo=tipo,
                    canal=canal,
                    titulo=titulo,
                    mensaje=mensaje,
                    contenido_type=contenido_type,
                    contenido_id=contenido_id,
                    icono=icono,
                    color=color
                )
                notificaciones_creadas.append(notif)

                # Enviar por canal externo si no es en_app
                if canal != CanalNotificacion.EN_APP:
                    NotificacionService._enviar_por_canal(usuario, notif, canal, preferencias)

        return notificaciones_creadas

    @staticmethod
    def _verificar_preferencias(tipo, preferencias):
        """Verifica si el usuario quiere recibir este tipo de notificación"""
        if tipo == TipoNotificacion.CURSO_CREADO:
            return preferencias.cursos_nuevos
        elif tipo == TipoNotificacion.CALIFICACION_CAMBIO:
            return preferencias.calificaciones_cambios
        elif tipo == TipoNotificacion.TAREA_RECORDATORIO:
            return preferencias.tareas_recordatorios
        elif tipo in [TipoNotificacion.CUESTIONARIO_DISPONIBLE, TipoNotificacion.CUESTIONARIO_CERRADO]:
            return preferencias.cuestionarios_eventos
        elif tipo == TipoNotificacion.CLASE_PROGRAMADA:
            return preferencias.clases_programadas
        elif tipo == TipoNotificacion.MENSAJE_RECIBIDO:
            return preferencias.mensajes_recibidos
        return True

    @staticmethod
    def _enviar_por_canal(usuario, notificacion, canal, preferencias):
        """Envía notificación por canal específico"""
        if canal == CanalNotificacion.EMAIL and preferencias.email_habilitado:
            NotificacionService._enviar_email(usuario, notificacion)
        elif canal == CanalNotificacion.WHATSAPP and preferencias.whatsapp_habilitado:
            NotificacionService._enviar_whatsapp(usuario, notificacion, preferencias)
        elif canal == CanalNotificacion.SMS and preferencias.sms_habilitado:
            NotificacionService._enviar_sms(usuario, notificacion, preferencias)

    @staticmethod
    def _enviar_email(usuario, notificacion):
        """Envía notificación por email"""
        try:
            subject = notificacion.titulo
            html_message = render_to_string('notificaciones/email.html', {
                'usuario': usuario,
                'notificacion': notificacion,
                'nombre_sistema': 'Sistema de Catequesis',
                'url_base': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            })

            send_mail(
                subject=subject,
                message=notificacion.mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                html_message=html_message,
                fail_silently=False,
            )
            notificacion.marcar_como_enviada()
            logger.info(f"Email enviado a {usuario.email} - {notificacion.id}")
        except Exception as e:
            logger.error(f"Error enviando email a {usuario.email}: {str(e)}")

    @staticmethod
    def _enviar_whatsapp(usuario, notificacion, preferencias):
        """Envía notificación por WhatsApp (requiere Twilio)"""
        try:
            # Necesita configuración de Twilio
            if not hasattr(settings, 'TWILIO_ACCOUNT_SID'):
                logger.warning("Twilio no configurado para WhatsApp")
                return

            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                body=f"{notificacion.titulo}\n\n{notificacion.mensaje}",
                to=f"whatsapp:{preferencias.numero_whatsapp}"
            )
            notificacion.marcar_como_enviada()
            logger.info(f"WhatsApp enviado a {preferencias.numero_whatsapp} - {message.sid}")
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {str(e)}")

    @staticmethod
    def _enviar_sms(usuario, notificacion, preferencias):
        """Envía notificación por SMS (requiere Twilio)"""
        try:
            if not hasattr(settings, 'TWILIO_ACCOUNT_SID'):
                logger.warning("Twilio no configurado para SMS")
                return

            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=settings.TWILIO_PHONE_NUMBER,
                body=f"{notificacion.titulo}: {notificacion.mensaje[:80]}",
                to=preferencias.numero_sms
            )
            notificacion.marcar_como_enviada()
            logger.info(f"SMS enviado a {preferencias.numero_sms} - {message.sid}")
        except Exception as e:
            logger.error(f"Error enviando SMS: {str(e)}")

    @staticmethod
    def obtener_notificaciones_usuario(usuario, solo_no_leidas=False, limite=20):
        """Obtiene notificaciones del usuario"""
        query = Notificacion.objects.filter(usuario=usuario, canal=CanalNotificacion.EN_APP)

        if solo_no_leidas:
            query = query.filter(leida=False)

        return query[:limite]

    @staticmethod
    def obtener_count_no_leidas(usuario):
        """Obtiene cantidad de notificaciones no leídas"""
        return Notificacion.objects.filter(
            usuario=usuario,
            leida=False,
            canal=CanalNotificacion.EN_APP
        ).count()

    @staticmethod
    def marcar_todas_como_leidas(usuario):
        """Marca todas las notificaciones del usuario como leídas"""
        Notificacion.objects.filter(
            usuario=usuario,
            leida=False,
            canal=CanalNotificacion.EN_APP
        ).update(leida=True)

    @staticmethod
    def eliminar_notificaciones_antiguas(dias=30):
        """Limpia notificaciones antiguas"""
        from django.utils import timezone
        from datetime import timedelta

        fecha_limite = timezone.now() - timedelta(days=dias)
        eliminar = Notificacion.objects.filter(
            fecha_creacion__lt=fecha_limite,
            leida=True
        )
        count, _ = eliminar.delete()
        logger.info(f"Eliminadas {count} notificaciones antiguas")
        return count
