from django.urls import path
from . import views

urlpatterns = [
    #path('crear/<int:clase_id>/', views.crear_cuestionario, name='crear_cuestionario'),
    #path('pregunta/<int:cuestionario_id>/', views.crear_pregunta, name='crear_pregunta'),
    #path('resolver/<int:cuestionario_id>/', views.resolver_cuestionario, name='resolver_cuestionario'),
    
    
    path('crear/<int:clase_id>/', views.crear_cuestionario, name='crear_cuestionario'),
    path('guardar/', views.guardar_cuestionario, name='guardar_cuestionario'),
    path('editar/<int:id>/', views.editar_cuestionario, name='editar_cuestionario'),
    path('actualizar/<int:id>/', views.actualizar_cuestionario, name='actualizar_cuestionario'),
    #resultados
    path('resultados/<int:id>/', views.ver_resultados, name='ver_resultados_cuestionario'),
    path('resolver/<int:id>/', views.resolver_cuestionario, name='resolver_cuestionario'),
    path('detalle/<int:id>/', views.detalle_intento, name='detalle_intento'),

    path('estadisticas/<int:id>/', views.estadisticas_pregunta, name='estadisticas_pregunta'),
    path('ranking/<int:id>/', views.ranking, name='ranking'),
    path('pdf/<int:id>/', views.exportar_pdf, name='exportar_pdf'),
    path('reporte/', views.reporte_general, name='reporte_general'),
    #reporte PDF
    path('reporte/pdf/', views.exportar_reporte_pdf, name='exportar_reporte_pdf'),
    #admin
    path('',views.lista_cuestionarios,name='lista_cuestionarios'),
    path('admin/crear/',views.crear_cuestionario_admin,name='crear_cuestionario_admin'),
    path('admin/guardar/',views.guardar_cuestionario_admin,name='guardar_cuestionario_admin'),
    path('admin/editar/<int:cuestionario_id>/',views.editar_cuestionario_admin,name='editar_cuestionario_admin'),
    path('admin/actualizar/<int:cuestionario_id>/',views.actualizar_cuestionario_admin,name='actualizar_cuestionario_admin'),
    path('admin/resultados/<int:cuestionario_id>/',views.resultados_cuestionario_admin,name='resultados_cuestionario_admin'),
    path('admin/intento/<int:intento_id>/',views.detalle_intento_admin,name='detalle_intento_admin'),
    path('admin/estadisticas/<int:cuestionario_id>/',views.estadisticas_cuestionario_admin,name='estadisticas_cuestionario_admin'),
    path('admin/pdf/<int:cuestionario_id>/',views.exportar_resultados_pdf,name='exportar_resultados_pdf'),

    
]