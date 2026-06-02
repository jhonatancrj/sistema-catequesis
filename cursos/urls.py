from django.urls import path
from . import views

urlpatterns = [
    ##crear cursos
    path('', views.lista_cursos, name='lista_cursos'),
    path('crear/', views.crear_curso, name='crear_curso'),
    path('editar/<int:curso_id>/',views.editar_curso,name='editar_curso'),
    path('eliminar/<int:id>/', views.eliminar_curso, name='eliminar_curso'),
    ##inscripciones
    path('disponibles/', views.cursos_disponibles, name='cursos_disponibles'),
    path('inscribirse/<int:id>/', views.inscribirse_curso, name='inscribirse_curso'),
    path('mis-cursos/', views.mis_cursos, name='mis_cursos'),
    ##vista catequistas##
    path('catequista/',views.cursos_catequista,name='cursos_catequista'),

    ##clases##
    path(
        'curso/<int:curso_id>/clases/',
        views.clases_curso,
        name='clases_curso'
    ),    
    ##asistencia
    path(
    'clase/<int:clase_id>/asistencia/',
    views.tomar_asistencia,
    name='tomar_asistencia'
    ),
    path(
        'asistencia-qr/<int:clase_id>/',
        views.registrar_asistencia_qr,
        name='asistencia_qr'
    ),
    path('mi-qr/', views.mi_qr, name='mi_qr'),
    path('historial-asistencias/', views.historial_asistencias, name='historial_asistencias'),
    path('detalle/<int:id>/', views.detalle_curso, name='detalle_curso'),
    ## PDF
    path('curso/<int:id>/exportar-pdf/', views.exportar_participantes_pdf, name='exportar_participantes_pdf'),
    path('exportar-asistencia/<int:curso_id>/', views.exportar_asistencia_curso_pdf, name='exportar_asistencia_curso_pdf'),
    ##admin
    path('inscripciones/',views.lista_inscripciones,name='lista_inscripciones'),
    path('inscripciones/crear/',views.crear_inscripcion,name='crear_inscripcion'),
    path('clases/',views.lista_clases,name='lista_clases'),
    path('clases/crear/',views.crear_clase,name='crear_clase'),
    path('clases/editar/<int:clase_id>/',views.editar_clase,name='editar_clase'),
    path('asistencia/',views.lista_asistencia,name='lista_asistencia'),
    path('asistencia/tomar/<int:clase_id>/',views.tomar_asistencia_admin,name='tomar_asistencia_admin'),

]
