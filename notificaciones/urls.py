from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    # Notificaciones generales (redirecciona según rol)
    path('', views.notificaciones_list, name='lista'),
    
    # Notificaciones por rol
    path('admin/', views.notificaciones_admin, name='admin'),
    path('participante/', views.notificaciones_participante, name='participante'),
    path('catequista/', views.notificaciones_catequista, name='catequista'),
    
    # Acciones
    path('marcar-como-leida/<int:notificacion_id>/', views.marcar_como_leida, name='marcar_como_leida'),
    path('marcar-todas-como-leidas/', views.marcar_todas_como_leidas, name='marcar_todas_como_leidas'),
    path('eliminar/<int:notificacion_id>/', views.eliminar_notificacion, name='eliminar'),
    path('preferencias/', views.preferencias_notificaciones, name='preferencias'),
    
    # APIs
    path('api/recientes/', views.obtener_notificaciones_recientes, name='api_recientes'),
    
    # Admin
    path('masivas/', views.notificaciones_masivas, name='masivas'),
]
