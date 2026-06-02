# 🔔 Sistema de Notificaciones

## Descripción

Sistema completo de notificaciones integrado en el Centro de Catequesis Parroquial que permite:

- 📢 **Notificaciones en tiempo real** dentro de la aplicación
- 📧 **Email automático** para eventos importantes
- 💬 **WhatsApp/SMS** para notificaciones urgentes (requiere Twilio)
- ⚙️ **Preferencias personalizables** por usuario
- 📋 **Historial de notificaciones** completo
- 👥 **Notificaciones masivas** para administradores

---

## 🎯 Tipos de Notificaciones

| Tipo | Descripción | Destinatarios |
|------|-------------|---|
| **Nuevo Curso** | Se crea un nuevo curso en el sistema | Catequistas, Admins |
| **Cambio de Calificación** | Actualización en calificaciones o estado de aprobación | Participantes |
| **Recordatorio de Tarea** | Nueva tarea creada o tarea entregada | Participantes, Catequistas |
| **Cuestionario Disponible** | Nuevo cuestionario o cierre de cuestionario | Participantes |
| **Clase Programada** | Nueva clase programada o cambios | Participantes |
| **Mensaje Recibido** | Nuevo mensaje de usuario a usuario | Destinatarios |

---

## 📊 Modelo de Datos

### Notificacion
- **usuario**: Usuario que recibe la notificación
- **tipo**: TipoNotificacion (curso_creado, calificacion_cambio, etc.)
- **canal**: CanalNotificacion (en_app, email, whatsapp, sms)
- **titulo**: Título de la notificación
- **mensaje**: Contenido de la notificación
- **leida**: Boolean (si ha sido leída)
- **enviada**: Boolean (si se envió por canal externo)
- **contenido_type**: Tipo de objeto relacionado (opcional)
- **contenido_id**: ID del objeto relacionado (opcional)
- **icono**: Ícono de Bootstrap a mostrar
- **color**: Clase de color Bootstrap

### PreferenciaNotificacion
- **usuario**: OneToOne relationship
- **cursos_nuevos**: bool (default: True)
- **calificaciones_cambios**: bool (default: True)
- **tareas_recordatorios**: bool (default: True)
- **cuestionarios_eventos**: bool (default: True)
- **clases_programadas**: bool (default: True)
- **mensajes_recibidos**: bool (default: True)
- **email_habilitado**: bool (default: True)
- **whatsapp_habilitado**: bool (default: False)
- **sms_habilitado**: bool (default: False)
- **resumen_diario**: bool (default: False)
- **hora_resumen**: TimeField (default: 09:00)
- **numero_whatsapp**: CharField (para SMS via Twilio)
- **numero_sms**: CharField (para SMS via Twilio)

---

## 🛠️ Uso del Servicio

### Crear Notificación Simple

```python
from notificaciones.models import TipoNotificacion, CanalNotificacion
from notificaciones.services import NotificacionService

# Notificar a un usuario
NotificacionService.crear_notificacion(
    usuarios=usuario,
    tipo=TipoNotificacion.CURSO_CREADO,
    titulo="Nuevo Curso: Python Avanzado",
    mensaje="Se ha creado un nuevo curso disponible para inscripción",
    canales=[CanalNotificacion.EN_APP, CanalNotificacion.EMAIL],
    contenido_type='curso',
    contenido_id=curso.id,
    icono='bi-book',
    color='info'
)
```

### Notificar a Múltiples Usuarios

```python
usuarios = User.objects.filter(perfil__rol='ADMIN')

NotificacionService.crear_notificacion(
    usuarios=list(usuarios),
    tipo=TipoNotificacion.CALIFICACION_CAMBIO,
    titulo="Nueva Aprobación Registrada",
    mensaje="Se ha registrado una nueva aprobación de curso",
    canales=[CanalNotificacion.EN_APP, CanalNotificacion.EMAIL],
)
```

### Métodos Disponibles

```python
# Obtener notificaciones del usuario
notificaciones = NotificacionService.obtener_notificaciones_usuario(
    usuario=request.user,
    solo_no_leidas=False,
    limite=20
)

# Contar no leídas
count = NotificacionService.obtener_count_no_leidas(request.user)

# Marcar todas como leídas
NotificacionService.marcar_todas_como_leidas(request.user)

# Limpiar notificaciones antiguas (>30 días y leídas)
NotificacionService.eliminar_notificaciones_antiguas(dias=30)
```

---

## 🌐 Endpoints (URLs)

### Para Usuarios
- `GET  /notificaciones/` - Lista de notificaciones
- `GET  /notificaciones/preferencias/` - Panel de preferencias
- `POST /notificaciones/marcar-como-leida/<id>/` - Marcar como leída
- `POST /notificaciones/marcar-todas-como-leidas/` - Marcar todas
- `POST /notificaciones/eliminar/<id>/` - Eliminar notificación

### APIs
- `GET  /notificaciones/api/recientes/?limit=5` - Últimas notificaciones (JSON)
- `GET  /notificaciones/api/campana/` - HTML para dropdown

### Admin
- `GET  /notificaciones/masivas/` - Centro de notificaciones masivas

---

## ⚙️ Configuración

### 1. Agregar App a INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    ...
    'notificaciones',
]
```

✅ **Ya está configurado**

### 2. Email Configuration

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña-app'
DEFAULT_FROM_EMAIL = 'noreply@sistema-catequesis.com'

# Opcional: URL base del sitio para links en emails
SITE_URL = 'http://localhost:8000'
```

### 3. Twilio Configuration (Opcional - para WhatsApp/SMS)

```python
# settings.py
TWILIO_ACCOUNT_SID = 'tu-account-sid'
TWILIO_AUTH_TOKEN = 'tu-auth-token'
TWILIO_PHONE_NUMBER = '+1234567890'
TWILIO_WHATSAPP_NUMBER = '+1234567890'
```

Instalar Twilio:
```bash
pip install twilio
```

### 4. Ejecutar Migraciones

```bash
python manage.py migrate notificaciones
```

---

## 🔗 Signals (Notificaciones Automáticas)

El sistema genera notificaciones automáticamente cuando ocurren eventos:

### Cursos
- `Curso` - Se crea (notifica a admins/catequistas)
- `Clase` - Se crea (notifica a participantes inscritos)

### Tareas
- `Tarea` - Se crea (notifica a participantes)
- `EntregaTarea` - Se crea (notifica al catequista)

### Cuestionarios
- `Cuestionario` - Se crea (notifica a participantes)

### Calificaciones
- `ResultadoCurso` - Se actualiza (notifica al participante)

### Asistencia
- `Asistencia` - Se registra (notifica al participante)

---

## 🎨 Interfaz de Usuario

### Campana de Notificaciones
- Ubicada en la barra superior del panel
- Muestra número de notificaciones no leídas
- Dropdown con últimas 5 notificaciones
- Enlaces para marcar como leída y ver todas

### Página de Notificaciones
- `/notificaciones/` - Lista completa de notificaciones
- Filtros por tipo
- Paginación
- Búsqueda y ordenamiento

### Panel de Preferencias
- `/notificaciones/preferencias/` - Gestionar preferencias
- Habilitar/deshabilitar por tipo
- Elegir canales
- Configurar horarios

---

## 🔒 Seguridad

- ✅ Login requerido para acceder a notificaciones
- ✅ Usuarios solo ven sus propias notificaciones
- ✅ Signals respetan preferencias del usuario
- ✅ CSRF protection en formularios
- ✅ Validación de números de teléfono

---

## 📚 Ejemplos de Uso

### En Signals/Receivers

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from cursos.models import Curso
from notificaciones.models import TipoNotificacion, CanalNotificacion
from notificaciones.services import NotificacionService

@receiver(post_save, sender=Curso)
def notificar_nuevo_curso(sender, instance, created, **kwargs):
    if created:
        usuarios = User.objects.filter(perfil__rol__in=['ADMIN', 'CATEQUISTA'])
        NotificacionService.crear_notificacion(
            usuarios=list(usuarios),
            tipo=TipoNotificacion.CURSO_CREADO,
            titulo=f"Nuevo Curso: {instance.nombre}",
            mensaje=f"Se ha creado un nuevo curso: {instance.nombre}",
            canales=[CanalNotificacion.EN_APP, CanalNotificacion.EMAIL],
        )
```

### En Views

```python
from notificaciones.models import TipoNotificacion, CanalNotificacion
from notificaciones.services import NotificacionService

def guardar_calificacion(request, resultado_id):
    resultado = ResultadoCurso.objects.get(id=resultado_id)
    
    # Actualizar calificación...
    resultado.calificacion = 85
    resultado.save()
    
    # Notificar al participante
    NotificacionService.crear_notificacion(
        usuarios=[resultado.usuario],
        tipo=TipoNotificacion.CALIFICACION_CAMBIO,
        titulo="Tu Calificación ha Sido Actualizada",
        mensaje=f"Tu calificación en {resultado.curso.nombre} es: {resultado.calificacion}",
        canales=[CanalNotificacion.EN_APP, CanalNotificacion.EMAIL],
    )
```

---

## 🧪 Pruebas

Ejecutar tests:

```bash
python manage.py test notificaciones
```

Tests disponibles:
- ✅ Crear notificación simple
- ✅ Crear para múltiples usuarios
- ✅ Marcar como leída
- ✅ Contar no leídas
- ✅ Verificación de preferencias

---

## 📝 Notas

- **Cleanup automático**: Notificaciones leídas con >30 días se eliminan
- **Performance**: Usa índices en usuario/leida/fecha_creacion
- **Escalabilidad**: Diseñado para manejar miles de notificaciones
- **Extensible**: Fácil agregar nuevos tipos o canales

---

## 🐛 Troubleshooting

### Las notificaciones por email no se envían

1. Verificar configuración EMAIL en settings.py
2. Revisar logs: `tail -f logs/django.log`
3. Probar: `python manage.py shell`
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Mensaje', 'from@example.com', ['to@example.com'])
   ```

### Badge no actualiza en tiempo real

- El sistema actualiza cada 30 segundos automáticamente
- Puedes reducir el intervalo en base_admin.html (línea: `setInterval(cargarNotificaciones, 30000)`)

### WhatsApp/SMS no funciona

- Requiere configuración de Twilio
- Verificar: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, números de teléfono
- Números deben estar en formato internacional: +506XXXXXXXX

---

## 📞 Soporte

Para reportar issues o sugerencias, contactar al administrador del sistema.
