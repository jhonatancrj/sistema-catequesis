from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:clase_id>/', views.crear_tarea, name='crear_tarea'),
    path('ver/<int:clase_id>/', views.ver_tareas, name='ver_tareas'),
    path('catequista/entregar/<int:tarea_id>/', views.entregar_tarea, name='entregar_tarea'),
    path('calificar/<int:entrega_id>/', views.calificar_tarea, name='calificar_tarea'),
    path('entregas/<int:tarea_id>/', views.ver_entregas, name='ver_entregas'),

    path('notificaciones/', views.ver_notificaciones, name='notificaciones'),
    path('cancelar/<int:tarea_id>/', views.cancelar_entrega, name='cancelar_entrega'),

    ##coneccion de drive con outh
    path('google-login/', views.google_login, name='google_login'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),

    path('panel/<int:curso_id>/', views.panel_catequista, name='panel_catequista'),
    ##reporte PDF
    path('reporte/<int:curso_id>/', views.reporte_tareas, name='reporte_tareas'),
    path('reporte/<int:curso_id>/pdf/', views.reporte_tareas_pdf, name='reporte_tareas_pdf'),
    ##admin
    path('',views.lista_tareas,name='lista_tareas'),
    path('crear/',views.crear_tarea_admin,name='crear_tarea_admin'),
    path('editar/<int:tarea_id>/',views.editar_tarea,name='editar_tarea'),
    path('admin/entregas/<int:tarea_id>/',views.ver_entregas_admin,name='ver_entregas_admin'),
    path('admin/calificar/<int:entrega_id>/',views.calificar_entrega,name='calificar_entrega'),

]