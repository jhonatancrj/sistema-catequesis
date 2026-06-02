# Guía de Uso del Sistema de Notificaciones - MEJORADO

## 🚀 Instalación y Configuración

### 1. Migraciones (YA REALIZADAS)
```bash
python manage.py makemigrations notificaciones
python manage.py migrate notificaciones
```

### 2. Rutas de Notificaciones

#### Para Usuarios
- **Notificaciones Generales**: `/notificaciones/`
- **Notificaciones (Participante)**: `/notificaciones/participante/`
- **Notificaciones (Catequista)**: `/notificaciones/catequista/`
- **Preferencias**: `/notificaciones/preferencias/`

#### APIs
- **Obtener Recientes**: `/notificaciones/api/recientes/?limit=5`

#### Admin
- **Notificaciones Masivas**: `/notificaciones/masivas/`

---

## 📢 Tipos de Notificaciones Implementadas

### Participantes Reciben
1. ✅ **Nueva Tarea Creada** - Cuando el catequista crea una tarea
2. ✅ **Tarea Próxima a Terminar** - 1 hora antes del vencimiento
3. ✅ **Nuevo Cuestionario** - Cuando hay cuestionario disponible
4. ✅ **Cuestionario Próximo a Terminar** - 1 hora antes del vencimiento
5. ✅ **Cambio de Calificación** - Cuando se actualiza la nota

### Catequistas Reciben
1. ✅ **Tarea Entregada** - Cuando un participante entrega una tarea
2. ✅ **Cuestionario Respondido** - Cuando un participante responde un cuestionario
3. ✅ **Nuevo Curso Creado** - Notificación administrativa

---

## 🔔 Funciones de Notificaciones

### Campana en Navbar
- Se actualiza cada **30 segundos**
- Muestra las **5 últimas notificaciones**
- Botón para marcar como leída
- Enlace a "Ver todas"

### Página de Notificaciones
- Filtrado por tipo
- Paginación
- Marcar individual o masivamente como leída
- Eliminar notificaciones

### Preferencias
- Habilitar/deshabilitar por tipo de notificación
- Canal: En-app o Email
- (WhatsApp/SMS requiere configuración Twilio)

---

## ⏰ Comando para Notificaciones Automáticas

### Notificar cuando faltan 60 minutos

```bash
python manage.py notificar_proximos_terminos
```

**Resultado**: Envía notificaciones a participantes que tienen:
- Tareas por vencer en menos de 1 hora
- Cuestionarios por vencer en menos de 1 hora

### Ejecutar Automáticamente (Cron Job)

**En Linux/Mac**:
```bash
# Ejecutar cada 15 minutos
*/15 * * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py notificar_proximos_terminos
```

**En Windows (Task Scheduler)**:
```
Programa: C:\ruta\venv\Scripts\python.exe
Argumentos: C:\ruta\manage.py notificar_proximos_terminos
Trabajar en: C:\ruta
```

---

## 📧 Configuración de Email

En `settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # o tu proveedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña-app'
DEFAULT_FROM_EMAIL = 'noreply@sistema-catequesis.com'

# URL base para links en emails
SITE_URL = 'https://tudominio.com'
```

**Para Gmail**: Usar [Contraseña de Aplicación](https://support.google.com/accounts/answer/185833)

---

## 🔄 Flujos de Notificación

### Cuando se Crea una Tarea
1. ✅ Crear notificación EN_APP a todos los participantes
2. ✅ Enviar EMAIL si está habilitado
3. 🕐 Agregar a cola de tareas próximas a terminar

### Cuando Falta 1 Hora para Terminar Tarea/Cuestionario
1. ✅ Ejecutar comando `notificar_proximos_terminos`
2. ✅ Enviar notificación EN_APP
3. ✅ Enviar EMAIL si está habilitado

### Cuando se Entrega Tarea
1. ✅ Crear notificación para catequista (EN_APP)
2. ✅ Enviar EMAIL al catequista

### Cuando se Responde Cuestionario
1. ✅ Crear notificación para catequista (EN_APP)
2. ✅ Enviar EMAIL al catequista

---

## 🎯 Vistas por Rol

### Vista Participante
- Filtros: Tareas | Cuestionarios | Calificaciones
- Muestra notificaciones personalizadas
- Acceso: `/notificaciones/participante/`

### Vista Catequista
- Filtros: Tareas Entregadas | Cuestionarios Respondidos
- Muestra notificaciones de actividad de alumnos
- Acceso: `/notificaciones/catequista/`

### Vista General
- Todas las notificaciones
- Acceso: `/notificaciones/`

---

## 🧪 Probar las Notificaciones

### Manual
1. Ir a `/admin/`
2. Crear una tarea en un curso
3. Verificar que los participantes reciban notificación
4. Ejecutar comando: `python manage.py notificar_proximos_terminos`

### Automático
1. Programar el comando con cron
2. Esperar 15 minutos (si es cada 15 min)
3. Verificar que se envíen notificaciones

---

## 📊 Modelos de Datos

### Notificacion
```
- usuario (FK User)
- tipo (TAREA_RECORDATORIO, CUESTIONARIO_DISPONIBLE, etc)
- canal (EN_APP, EMAIL, WHATSAPP, SMS)
- titulo
- mensaje
- leida (Boolean)
- enviada (Boolean)
- fecha_creacion
- fecha_lectura
- icono (Bootstrap icon)
- color (Bootstrap color class)
```

### PreferenciaNotificacion
```
- usuario (OneToOne User)
- email_habilitado (Boolean)
- cursos_nuevos, tareas_recordatorios, etc (Boolean)
```

---

## 🐛 Troubleshooting

### Las notificaciones no cargan en la campana
1. Abre la consola (F12 → Console)
2. Verifica que no haya errores de JavaScript
3. Intenta recargar la página
4. Verifica que la API `/notificaciones/api/recientes/` responda

### Los emails no se envían
1. Verifica configuración en `settings.py`
2. Intenta enviar email manualmente:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Mensaje', 'from@example.com', ['to@example.com'])
   ```

### El comando no se ejecuta
1. Verifica que el archivo existe: `notificaciones/management/commands/notificar_proximos_terminos.py`
2. Ejecuta con salida: `python manage.py notificar_proximos_terminos --verbosity 2`

---

## ✨ Resumen

✅ **Sistema completamente funcional** con:
- Campana de notificaciones en navbar
- Vistas separadas por rol
- Notificaciones automáticas
- Soporte para email
- Comando para verificar tareas próximas a terminar
- Preferencias personalizables

**Próximas mejoras opcionales:**
- Integrar Celery para tareas programadas
- Agregar WhatsApp/SMS con Twilio
- Dashboard de estadísticas
