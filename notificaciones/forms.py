from django import forms
from .models import PreferenciaNotificacion


class PreferenciaNotificacionForm(forms.ModelForm):
    class Meta:
        model = PreferenciaNotificacion
        fields = [
            'cursos_nuevos',
            'calificaciones_cambios',
            'tareas_recordatorios',
            'cuestionarios_eventos',
            'clases_programadas',
            'mensajes_recibidos',
            'email_habilitado',
            'whatsapp_habilitado',
            'sms_habilitado',
            'resumen_diario',
            'hora_resumen',
            'numero_whatsapp',
            'numero_sms',
        ]

        widgets = {
            'hora_resumen': forms.TimeInput(attrs={'type': 'time'}),
            'numero_whatsapp': forms.TextInput(attrs={
                'placeholder': '+506 XXXX XXXX',
                'pattern': '[0-9+\\s]+',
            }),
            'numero_sms': forms.TextInput(attrs={
                'placeholder': '+506 XXXX XXXX',
                'pattern': '[0-9+\\s]+',
            }),
        }

        labels = {
            'cursos_nuevos': 'Notificar sobre nuevos cursos',
            'calificaciones_cambios': 'Notificar sobre cambios en calificaciones',
            'tareas_recordatorios': 'Notificar sobre tareas',
            'cuestionarios_eventos': 'Notificar sobre cuestionarios',
            'clases_programadas': 'Notificar sobre clases programadas',
            'mensajes_recibidos': 'Notificar sobre nuevos mensajes',
            'email_habilitado': 'Habilitar notificaciones por Email',
            'whatsapp_habilitado': 'Habilitar notificaciones por WhatsApp',
            'sms_habilitado': 'Habilitar notificaciones por SMS',
            'resumen_diario': 'Recibir resumen diario en lugar de notificaciones individuales',
            'hora_resumen': 'Hora para recibir el resumen diario',
            'numero_whatsapp': 'Número de WhatsApp',
            'numero_sms': 'Número de Teléfono (SMS)',
        }
