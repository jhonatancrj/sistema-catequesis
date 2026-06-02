import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from .models import Notificacion, PreferenciaNotificacion, CanalNotificacion
from .services import NotificacionService
from usuarios.decorators import rol_requerido


@login_required
def notificaciones_list(request):
    """Página de notificaciones del usuario - redirecciona según rol"""
    # Detectar rol y redirigir a la vista específica
    usuario = request.user
    if hasattr(usuario, 'rol') and usuario.rol:
        if usuario.rol == 'PARTICIPANTE':
            return redirect('notificaciones:participante')
        elif usuario.rol == 'CATEQUISTA':
            return redirect('notificaciones:catequista')
    
    # Por defecto (ADMIN) muestra todas las notificaciones
    filtro = request.GET.get('filtro', 'todas')
    pagina = int(request.GET.get('pagina', 1))
    por_pagina = 15

    query = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')

    # Filtrar por tipo
    if filtro != 'todas':
        query = query.filter(tipo=filtro)

    # Filtrar solo en-app
    query = query.filter(canal=CanalNotificacion.EN_APP)

    # Contar total no leídas
    total_no_leidas = query.filter(leida=False).count()

    # Paginación
    start = (pagina - 1) * por_pagina
    end = start + por_pagina
    notificaciones = query[start:end]

    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina

    context = {
        'notificaciones': notificaciones,
        'filtro': filtro,
        'pagina': pagina,
        'total_paginas': total_paginas,
        'total': total,
        'total_no_leidas': total_no_leidas,
        'tipos_disponibles': [
            ('curso_creado', 'Cursos'),
            ('calificacion_cambio', 'Calificaciones'),
            ('tarea_recordatorio', 'Tareas'),
            ('tarea_entregada', 'Tareas Entregadas'),
            ('cuestionario_disponible', 'Cuestionarios'),
            ('cuestionario_entregado', 'Cuestionarios Entregados'),
            ('clase_programada', 'Clases'),
        ]
    }
    return render(request, 'notificaciones/notificaciones_list.html', context)


@login_required
def notificaciones_participante(request):
    """Página de notificaciones para participantes"""
    filtro = request.GET.get('filtro', 'todas')
    pagina = int(request.GET.get('pagina', 1))
    por_pagina = 15

    query = Notificacion.objects.filter(
        usuario=request.user,
        canal=CanalNotificacion.EN_APP
    ).order_by('-fecha_creacion')

    if filtro != 'todas':
        query = query.filter(tipo=filtro)

    total_no_leidas = query.filter(leida=False).count()

    start = (pagina - 1) * por_pagina
    notificaciones = query[start:start + por_pagina]
    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina

    context = {
        'notificaciones': notificaciones,
        'filtro': filtro,
        'pagina': pagina,
        'total_paginas': total_paginas,
        'total': total,
        'total_no_leidas': total_no_leidas,
        'rol': 'Participante'
    }
    return render(request, 'notificaciones/notificaciones_participante.html', context)


@login_required
@rol_requerido('CATEQUISTA')
def notificaciones_catequista(request):
    """Página de notificaciones para catequistas"""
    filtro = request.GET.get('filtro', 'todas')
    pagina = int(request.GET.get('pagina', 1))
    por_pagina = 15

    query = Notificacion.objects.filter(
        usuario=request.user,
        canal=CanalNotificacion.EN_APP
    ).order_by('-fecha_creacion')

    if filtro != 'todas':
        query = query.filter(tipo=filtro)

    total_no_leidas = query.filter(leida=False).count()

    start = (pagina - 1) * por_pagina
    notificaciones = query[start:start + por_pagina]
    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina

    context = {
        'notificaciones': notificaciones,
        'filtro': filtro,
        'pagina': pagina,
        'total_paginas': total_paginas,
        'total': total,
        'total_no_leidas': total_no_leidas,
        'rol': 'Catequista'
    }
    return render(request, 'notificaciones/notificaciones_catequista.html', context)


@login_required
@require_http_methods(["POST"])
def marcar_como_leida(request, notificacion_id):
    """Marca una notificación como leída"""
    try:
        notif = Notificacion.objects.get(
            id=notificacion_id,
            usuario=request.user
        )
        notif.marcar_como_leida()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No encontrada'}, status=404)


@login_required
@require_http_methods(["POST"])
def marcar_todas_como_leidas(request):
    """Marca todas las notificaciones como leídas"""
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True, fecha_lectura=timezone.now())
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def eliminar_notificacion(request, notificacion_id):
    """Elimina una notificación"""
    try:
        notif = Notificacion.objects.get(
            id=notificacion_id,
            usuario=request.user
        )
        notif.delete()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


@login_required
def preferencias_notificaciones(request):
    """Panel de preferencias de notificaciones"""
    try:
        preferencias = request.user.preferencias_notificaciones
    except PreferenciaNotificacion.DoesNotExist:
        preferencias = PreferenciaNotificacion.objects.create(usuario=request.user)

    if request.method == 'POST':
        preferencias.cursos_nuevos = request.POST.get('cursos_nuevos') == 'on'
        preferencias.calificaciones_cambios = request.POST.get('calificaciones_cambios') == 'on'
        preferencias.tareas_recordatorios = request.POST.get('tareas_recordatorios') == 'on'
        preferencias.cuestionarios_eventos = request.POST.get('cuestionarios_eventos') == 'on'
        preferencias.clases_programadas = request.POST.get('clases_programadas') == 'on'
        preferencias.mensajes_recibidos = request.POST.get('mensajes_recibidos') == 'on'

        preferencias.email_habilitado = request.POST.get('email_habilitado') == 'on'
        preferencias.resumen_diario = request.POST.get('resumen_diario') == 'on'

        if request.POST.get('hora_resumen'):
            preferencias.hora_resumen = request.POST.get('hora_resumen')

        preferencias.save()

        return JsonResponse({'success': True, 'mensaje': 'Preferencias actualizadas'})

    context = {'preferencias': preferencias}
    return render(request, 'notificaciones/preferencias.html', context)


@login_required
def obtener_notificaciones_recientes(request):
    """API AJAX para obtener notificaciones recientes (para campana)"""
    try:
        limit = int(request.GET.get('limit', 5))
    except:
        limit = 5

    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        canal=CanalNotificacion.EN_APP
    ).order_by('-fecha_creacion')[:limit]

    data = {
        'notificaciones': [
            {
                'id': n.id,
                'titulo': n.titulo,
                'mensaje': n.mensaje[:60] + '...' if len(n.mensaje) > 60 else n.mensaje,
                'tipo': n.get_tipo_display(),
                'leida': n.leida,
                'icono': n.icono,
                'color': n.color,
                'fecha': n.fecha_creacion.strftime('%d/%m %H:%M'),
            }
            for n in notificaciones
        ],
        'total_no_leidas': Notificacion.objects.filter(
            usuario=request.user,
            leida=False,
            canal=CanalNotificacion.EN_APP
        ).count()
    }
    return JsonResponse(data)


@rol_requerido('ADMIN')
def notificaciones_masivas(request):
    """Panel de administración de notificaciones masivas"""
    from .models import NotificacionMasiva

    notificaciones = NotificacionMasiva.objects.all().order_by('-fecha_creacion')

    context = {'notificaciones': notificaciones}
    return render(request, 'notificaciones/notificaciones_masivas.html', context)
