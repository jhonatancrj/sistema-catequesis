from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from cursos.models import Clase, Inscripcion, Asistencia
import calendar

def home(request):
    return render(request, 'core/home.html')

def nosotros(request):
    """Vista para la página Nosotros"""
    return render(request, 'core/nosotros.html')

def contacto(request):
    """Vista para la página de Contacto"""
    return render(request, 'core/contacto.html')

def enviar_contacto(request):
    """Procesa el envío del formulario de contacto"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        if nombre and email and asunto and mensaje:
            try:
                # Enviar email a la parroquia
                send_mail(
                    f'Contacto: {asunto}',
                    f'De: {nombre} ({email})\n\n{mensaje}',
                    'noreply@parroquiarosario.com',
                    ['parroquiarosariopnsr@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, '✓ Mensaje enviado correctamente. Nos contactaremos pronto.')
                return redirect('contacto')
            except Exception as e:
                messages.error(request, f'✗ Error al enviar: {str(e)}')
        else:
            messages.error(request, '✗ Por favor completa todos los campos.')
    
    return redirect('contacto')

def eventos(request):
    """Vista para mostrar eventos de la parroquia"""
    return render(request, 'core/eventos.html')

def calendario(request):
    """Vista del calendario con clases del participante o catequista (si está logeado)"""
    clases = []
    
    # Si el usuario está logeado como participante o catequista, obtener sus clases
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            if perfil.rol == 'PARTICIPANTE':
                inscripciones = Inscripcion.objects.filter(
                    participante=perfil,
                    estado='INSCRITO'
                ).select_related('curso')
                
                clases_ids = []
                for inscripcion in inscripciones:
                    clases_ids.extend(
                        Clase.objects.filter(
                            curso=inscripcion.curso
                        ).values_list('id', flat=True)
                    )
                
                clases = Clase.objects.filter(id__in=clases_ids).order_by('fecha')
            
            elif perfil.rol == 'CATEQUISTA':
                # Catequista ve todas las clases de sus cursos
                clases = Clase.objects.filter(
                    curso__catequistas=perfil
                ).order_by('fecha')
        except:
            pass
    
    context = {
        'clases': clases,
    }
    
    return render(request, 'core/calendario.html', context)

def calendario_api(request):
    """API para obtener datos del calendario (participantes y catequistas)"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        perfil = request.user.perfil
        
        # Solo participantes y catequistas pueden ver el calendario
        if perfil.rol not in ['PARTICIPANTE', 'CATEQUISTA']:
            return JsonResponse({'error': 'Acceso denegado'}, status=403)
        
        mes = int(request.GET.get('mes', datetime.now().month))
        ano = int(request.GET.get('ano', datetime.now().year))
        
        # Obtener clases según el rol
        if perfil.rol == 'PARTICIPANTE':
            inscripciones = Inscripcion.objects.filter(
                participante=perfil,
                estado='INSCRITO'
            )
            
            clases = Clase.objects.filter(
                curso__inscripcion__in=inscripciones,
                fecha__month=mes,
                fecha__year=ano
            ).distinct().select_related('curso')
        
        elif perfil.rol == 'CATEQUISTA':
            # Catequista ve todas sus clases
            clases = Clase.objects.filter(
                curso__catequistas=perfil,
                fecha__month=mes,
                fecha__year=ano
            ).select_related('curso')
        
        # Agrupar clases por fecha
        clases_por_fecha = {}
        for clase in clases:
            fecha_str = clase.fecha.strftime('%Y-%m-%d')
            if fecha_str not in clases_por_fecha:
                clases_por_fecha[fecha_str] = []
            clases_por_fecha[fecha_str].append({
                'titulo': clase.titulo,
                'curso': clase.curso.nombre,
                'hora': f"{clase.hora_inicio.strftime('%H:%M')} - {clase.hora_fin.strftime('%H:%M')}"
            })
        
        return JsonResponse(clases_por_fecha)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def calendario_admin(request):
    """Vista del calendario para administrador - ve todas las clases de todos los cursos"""
    # Verificar que es admin
    try:
        perfil = request.user.perfil
        if perfil.rol != 'ADMIN':
            return redirect('home')
    except:
        return redirect('home')
    
    # Obtener todas las clases
    clases = Clase.objects.all().order_by('fecha')
    
    context = {
        'clases': clases,
    }
    
    return render(request, 'core/calendario_admin.html', context)


@login_required
def calendario_admin_api(request):
    """API para obtener datos del calendario del admin - todas las clases"""
    try:
        perfil = request.user.perfil
        
        # Solo admin puede ver este calendario
        if perfil.rol != 'ADMIN':
            return JsonResponse({'error': 'Acceso denegado'}, status=403)
        
        mes = int(request.GET.get('mes', datetime.now().month))
        ano = int(request.GET.get('ano', datetime.now().year))
        
        # Obtener todas las clases del mes/año
        clases = Clase.objects.filter(
            fecha__month=mes,
            fecha__year=ano
        ).select_related('curso').prefetch_related('curso__catequistas__usuario')
        
        # Agrupar clases por fecha
        clases_por_fecha = {}
        for clase in clases:
            fecha_str = clase.fecha.strftime('%Y-%m-%d')
            if fecha_str not in clases_por_fecha:
                clases_por_fecha[fecha_str] = []
            
            # Obtener catequistas del curso
            catequistas_names = []
            for cat in clase.curso.catequistas.all():
                nombre = cat.usuario.get_full_name() or cat.usuario.username
                catequistas_names.append(nombre)
            
            catequista_str = ', '.join(catequistas_names) if catequistas_names else 'Sin asignar'
            
            clases_por_fecha[fecha_str].append({
                'titulo': clase.titulo,
                'curso': clase.curso.nombre,
                'catequista': catequista_str,
                'hora': f"{clase.hora_inicio.strftime('%H:%M')} - {clase.hora_fin.strftime('%H:%M')}"
            })
        
        return JsonResponse(clases_por_fecha)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
