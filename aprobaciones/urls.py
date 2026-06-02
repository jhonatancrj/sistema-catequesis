from django.urls import path
from .views import enviar_aprobados, reporte_curso, exportar_reporte_curso_pdf, lista_aprobados, enviar_certificado
from . import views

urlpatterns = [
    path(
        'enviar-aprobados/<int:id>/',
        enviar_aprobados,
        name='enviar_aprobados'
    ),
    path(
        'reporte/<int:id>/',
        reporte_curso,
        name='reporte_curso'
    ),
    path(
        'pdf/reporte/<int:id>/',
        exportar_reporte_curso_pdf,
        name='exportar_reporte_curso_pdf'
    ),
    path(
        'lista-aprobados/',
        lista_aprobados,
        name='lista_aprobados'
    ),
    path(
        'enviar-certificado/<int:id>/',
        enviar_certificado,
        name='enviar_certificado'
    ),
    path(
        'admin/sacramentos/',
        views.sacramentos_admin,
        name='sacramentos_admin'
    ),
    path(
        'admin/sacramentos/agregar/',
        views.agregar_sacramento_manual,
        name='agregar_sacramento_manual'
    ),
    path(
        'admin/sacramentos/<str:sacramento>/',
        views.detalle_sacramento_admin,
        name='detalle_sacramento_admin'
    ),


]