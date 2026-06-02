from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar'),
    # recuperacion de cuenta
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path(
        'reset/<uidb64>/<token>/',
        views.password_reset_confirm,
        name='password_reset_confirm'
    ),
    # Editar perfil propio
    path('mi-perfil/',views.editar_mi_perfil,name='editar_mi_perfil'),
    # redireccion por roles
    path('panel/admin/', views.panel_admin, name='panel_admin'),
    path('catequista/', views.panel_catequista, name='panel_catequista'),
    path('participante/', views.panel_participante, name='panel_participante'),
    ##admin
    path('administradores/',views.lista_administradores,name='lista_administradores'),
    path('administradores/crear/',views.crear_administrador,name='crear_administrador'),
    path('administradores/editar/<int:perfil_id>/',views.editar_administrador,name='editar_administrador'),
    path('administradores/eliminar/<int:perfil_id>/', views.eliminar_administrador,name='eliminar_administrador'),
    path('catequistas/',views.lista_catequistas,name='lista_catequistas'),
    path('catequistas/crear/',views.crear_catequista,name='crear_catequista'),
    path('catequistas/editar/<int:perfil_id>/',views.editar_catequista,name='editar_catequista'),
    path('catequistas/eliminar/<int:perfil_id>/',views.eliminar_catequista,name='eliminar_catequista'),
    path('participantes/',views.lista_participantes,name='lista_participantes'),
    path('participantes/editar/<int:perfil_id>/',views.editar_participante,name='editar_participante'),
    path('participantes/estado/<int:perfil_id>/',views.toggle_estado_participante,name='toggle_estado_participante'),
    path('participantes/crear/',views.crear_participante,name='crear_participante'),

]
