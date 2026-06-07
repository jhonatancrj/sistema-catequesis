"""
URL configuration for sistema_catequesis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from tareas.views import oauth2callback, google_login
urlpatterns = [
    
    ## aqui comienza el proyecto
    path('', include('centro.urls')),
    path('usuarios/', include('usuarios.urls')),
    ## cursos
    path('cursos/', include('cursos.urls')),
    #path('', include('usuarios.urls')),
    ## tarea
    path('tareas/', include('tareas.urls')),
    ## drive con outh
    path('tareas/', include('tareas.urls')),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('google-login/', google_login, name='google_login'),
    ## cuestionario
    path('cuestionario/', include('cuestionario.urls')),

    ## Aprobados
    path('aprobaciones/', include('aprobaciones.urls')),
    ## Sacramentos
    path('sacramentos/', include('sacramentos.urls')),
    ## Reportes
    path('reportes/', include('reportes.urls')),
    ## Notificaciones
    path('notificaciones/', include('notificaciones.urls')),
    ## Admin
    path('admin/', admin.site.urls),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

