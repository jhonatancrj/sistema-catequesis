from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto/enviar/', views.enviar_contacto, name='enviar_contacto'),
    path('eventos/', views.eventos, name='eventos'),
    path('calendario/', views.calendario, name='calendario'),
    path('api/calendario/', views.calendario_api, name='calendario_api'),
    path('admin/calendario/', views.calendario_admin, name='calendario_admin'),
    path('api/admin/calendario/', views.calendario_admin_api, name='calendario_admin_api'),
]
