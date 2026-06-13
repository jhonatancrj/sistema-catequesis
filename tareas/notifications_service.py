"""
Servicio centralizado para crear notificaciones y enviar emails
"""
from django.core.mail import send_mail
from django.conf import settings

# Intentar importar del modelo avanzado de notificaciones, sino usar el simple
try:
    from notificaciones.models import Notificacion, TipoNotificacion, CanalNotificacion
    USAR_MODELO_AVANZADO = True
except ImportError:
    from .models import Notificacion
    USAR_MODELO_AVANZADO = False


def crear_notificacion_y_email(usuario, mensaje, asunto=None, tipo=None, canal=None):
    """
    Crea una notificación en la BD y envía un email al usuario.
    
    Args:
        usuario: Usuario que recibe la notificación
        mensaje: Texto del mensaje
        asunto: Asunto del email (por defecto: "Notificación del Sistema")
        tipo: Tipo de notificación (si usar modelo avanzado)
        canal: Canal de notificación (si usar modelo avanzado)
    """
    if not asunto:
        asunto = "Notificación del Sistema"
    
    # ✅ Crear notificación en la base de datos
    if USAR_MODELO_AVANZADO:
        # Usar modelo avanzado con tipo y canal
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            titulo=asunto,
            mensaje=mensaje,
            tipo=tipo or TipoNotificacion.CURSO_CREADO,
            canal=CanalNotificacion.EN_APP,  # Primera se guarda en app
        )
    else:
        # Usar modelo simple de tareas
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            mensaje=mensaje
        )
    
    # 📧 Enviar email si el usuario tiene email
    if usuario.email:
        try:
            send_mail(
                asunto,
                mensaje,
                settings.EMAIL_HOST_USER,
                [usuario.email],
                fail_silently=False,
            )
            # Si usa modelo avanzado, marcar como enviada
            if USAR_MODELO_AVANZADO:
                notificacion.enviada = True
                notificacion.save()
        except Exception as e:
            print(f"Error enviando email a {usuario.email}: {e}")
    
    return notificacion
