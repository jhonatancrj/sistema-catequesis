# Sistema de Notificaciones con Vistas Separadas por Rol

## 📋 Descripción General

El sistema cuenta con **vistas y templates completamente separadas** para cada rol:
- ✅ Admin tiene su propio panel (usa `base_admin.html`)
- ✅ Catequistas y Participantes tienen su propio panel (usa `base.html`)
- 📧 Ambos reciben notificaciones y emails automáticamente
- 🌐 Compatible con modelo simple y avanzado de notificaciones

## 🎯 Vistas Separadas

### 1. Vista de Admin
**URL**: `/tareas/notificaciones/admin/`
**Vista**: `ver_notificaciones_admin()`
**Template**: `notificaciones_admin.html`
**Base Template**: `base_admin.html`

```python
@login_required
@rol_requerido('ADMIN')
def ver_notificaciones_admin(request):
    """Panel de notificaciones para administradores"""
```

**Características**:
- Panel profesional con estadísticas
- Muestra total de notificaciones
- Diseño con gradiente azul-púrpura
- Animaciones suaves
- Datos formateados para administradores

### 2. Vista de Usuarios (Catequistas/Participantes)
**URL**: `/tareas/notificaciones/`
**Vista**: `ver_notificaciones()`
**Template**: `notificaciones.html`
**Base Template**: `base.html`

```python
@login_required
def ver_notificaciones(request):
    """Panel de notificaciones para catequistas y participantes"""
```

**Características**:
- Panel limpio y responsivo
- Diseño simple pero elegante
- Mismos estilos consistentes
- Redirige a admin si el usuario es ADMIN

## 🚀 Cómo Usar

### Acceder a Notificaciones

#### Como Admin
```
http://tudominio.com/tareas/notificaciones/admin/
```

#### Como Catequista o Participante
```
http://tudominio.com/tareas/notificaciones/
```

### Crear Notificación con Email

```python
from tareas.notifications_service import crear_notificacion_y_email

# En cualquier vista
crear_notificacion_y_email(
    usuario=estudiante,
    mensaje="Tu tarea ha sido calificada",
    asunto="Tarea Calificada"
)
```

## 📁 Estructura de Archivos

### Vistas
- `tareas/views.py`:
  - `ver_notificaciones_admin()` - Panel para admin
  - `ver_notificaciones()` - Panel para usuarios

### Templates
- `tareas/templates/tareas/notificaciones_admin.html`
  - Usa `base_admin.html`
  - Más información y estadísticas
  - Diseño profesional

- `tareas/templates/tareas/notificaciones.html`
  - Usa `base.html`
  - Interfaz limpia
  - Para catequistas y participantes

### Servicio
- `tareas/notifications_service.py`
  - `crear_notificacion_y_email()` - Crea notificación y envía email

### URLs
- `tareas/urls.py`:
  - `notificaciones/` → `ver_notificaciones()` (usuarios normales)
  - `notificaciones/admin/` → `ver_notificaciones_admin()` (admin)

## 🔧 Flujo de Control

```
Usuario accede a /tareas/notificaciones/
    ↓
ver_notificaciones() verifica rol
    ↓
¿Es ADMIN?
    ├─ SÍ → Redirige a /tareas/notificaciones/admin/
    │        ↓
    │        ver_notificaciones_admin()
    │        ↓
    │        notificaciones_admin.html (base_admin.html)
    │
    └─ NO → Muestra notificaciones.html (base.html)
```

## 📧 Configuración de Email

Ya está configurada en `settings.py`:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'parroquiarosariopnsr@gmail.com'
EMAIL_HOST_PASSWORD = 'gemoolewvxjxrtxd'
```

El servicio automaticamente:
1. Crea la notificación en BD
2. Envía email si usuario tiene correo
3. Maneja errores silenciosamente

## 🎨 Diferencias de Diseño

### Panel Admin
- Gradiente azul-púrpura
- Card con estadísticas
- Tarjetas con animación deslizante
- Información detallada de fecha

### Panel Usuarios
- Mismo gradiente elegante
- Interfaz más simple
- Tarjetas limpias
- Diseño responsivo
- Mensaje cuando no hay notificaciones

## ✅ Pasos para Implementación

1. ✅ Crear servicio de notificaciones
2. ✅ Crear vistas separadas por rol
3. ✅ Crear templates con `base.html` y `base_admin.html`
4. ✅ Actualizar URLs
5. ✅ Importar en vistas que necesiten crear notificaciones

## 🧪 Prueba de Funcionamiento

1. Inicia sesión como **ADMIN**
   - Accede a `/tareas/notificaciones/admin/`
   - Debes ver el panel del admin con base_admin.html

2. Inicia sesión como **CATEQUISTA**
   - Accede a `/tareas/notificaciones/`
   - Debes ver el panel de usuarios con base.html

3. Prueba de Email
   - Califica una entrega
   - El estudiante debe recibir email

## 📞 Troubleshooting

### Las notificaciones no aparecen
- Verifica que el usuario tenga un `Perfil` asociado
- Comprueba la BD: `SELECT * FROM tareas_notificacion WHERE usuario_id = X`

### Email no se envía
- Verifica `settings.py` tiene credenciales correctas
- Revisa `fail_silently=False` en exceptions
- Comprueba que el usuario tiene `email` configurado

### Rol no se detecta
- Asegúrate que `request.user.perfil.rol` existe
- Fallback: rol = 'PARTICIPANTE' por defecto

## 🔐 Seguridad

- ✅ `@login_required` en ambas vistas
- ✅ `@rol_requerido('ADMIN')` en vista de admin
- ✅ Redirige a admin si usuario intenta forzar ruta
- ✅ Filtra notificaciones por usuario

