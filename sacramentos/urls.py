from django.urls import path

from .views import registrar_sacramento
from . import views

urlpatterns = [

    path('registrar/<int:id>/',registrar_sacramento,name='registrar_sacramento'),

    path('admin/lista/',views.lista_registros_sacramentales,name='lista_registros_sacramentales'),
    path('admin/crear/',views.crear_registro_sacramental,name='crear_registro_sacramental'),
    path('admin/editar/<int:id>/',views.editar_registro_sacramental,name='editar_registro_sacramental'),
    path('admin/detalle/<int:id>/',views.detalle_registro_sacramental,name='detalle_registro_sacramental'),
    #path('admin/pdf/<int:id>/',views.pdf_registro_sacramental,name='pdf_registro_sacramental'),
    path('admin/libros-historicos/',views.libros_historicos,name='libros_historicos'),
    path('admin/certificado/<int:id>/',views.certificado_sacramental_pdf,name='certificado_sacramental_pdf'),

    path('admin/tipos/',views.lista_sacramentos_admin,name='lista_sacramentos_admin'),
    path('admin/tipos/crear/',views.crear_sacramento_admin,name='crear_sacramento_admin'),
    path('admin/tipos/editar/<int:id>/',views.editar_sacramento_admin,name='editar_sacramento_admin'),
    path('admin/tipos/eliminar/<int:id>/',views.eliminar_sacramento_admin,name='eliminar_sacramento_admin'),

    path(
        'admin/cursos-finalizados/',
        views.cursos_finalizados_admin,
        name='cursos_finalizados_admin'
    ),

    path(
        'admin/cursos-finalizados/<int:id>/',
        views.detalle_curso_finalizado,
        name='detalle_curso_finalizado'
    ),
]