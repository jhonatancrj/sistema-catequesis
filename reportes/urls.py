from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.reportes_dashboard, name='reportes_dashboard'),
    
    # Reportes principales
    path('cursos/', views.reportes_cursos, name='reportes_cursos'),
    path('cursos/<int:curso_id>/', views.reporte_curso_detallado, name='reporte_curso_detallado'),
    path('participantes/', views.reportes_participantes, name='reportes_participantes'),
    path('catequistas/', views.reportes_catequistas, name='reportes_catequistas'),
    path('tareas/', views.reportes_tareas, name='reportes_tareas'),
    path('cuestionarios/', views.reportes_cuestionarios, name='reportes_cuestionarios'),
    path('aprobaciones/', views.reportes_aprobaciones, name='reportes_aprobaciones'),
    
    # APIs para gráficas
    path('api/graficas/dashboard/', views.datos_graficas_dashboard, name='api_graficas_dashboard'),
    path('api/graficas/cursos/', views.datos_graficas_cursos, name='api_graficas_cursos'),
    
    # Exportar a PDF
    path('pdf/dashboard/', views.generar_pdf_dashboard, name='pdf_dashboard'),
    path('pdf/cursos/', views.generar_pdf_cursos, name='pdf_cursos'),
    path('pdf/participantes/', views.generar_pdf_participantes, name='pdf_participantes'),
]
