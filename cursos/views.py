from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from django.core.files import File
# PYTHON
from datetime import datetime, timedelta
from io import BytesIO
# LIBRERÍAS EXTERNAS
import qrcode
# REPORTLAB
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from usuarios.decorators import rol_requerido
# MODELOS
from .models import Curso, Clase, Inscripcion, Asistencia
from usuarios.models import Perfil
from tareas.models import Tarea, EntregaTarea
from cuestionario.models import Cuestionario, Intento
# FORMULARIOS
from .forms import CursoForm, InscripcionForm, ClaseForm

@login_required
def lista_cursos(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    cursos = Curso.objects.prefetch_related(
        'catequistas'
    )

    context = {
        'cursos': cursos
    }

    return render(
        request,
        'admin/lista.html',
        context
    )

@login_required
@rol_requerido('ADMIN')
def crear_curso(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        form = CursoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # 🔹 GUARDAR CURSO
            curso = form.save()

            # 🔹 DATOS DE CLASES
            dias_clase = form.cleaned_data['dias_clase']

            hora_inicio = form.cleaned_data['hora_inicio_clase']

            hora_fin = form.cleaned_data['hora_fin_clase']

            descripcion_clase = form.cleaned_data['descripcion_clase']

            fecha_inicio = curso.fecha_inicio
            fecha_fin = curso.fecha_fin

            fecha_actual = fecha_inicio

            numero_clase = 1

            # 🔹 RECORRER FECHAS
            while fecha_actual <= fecha_fin:

                # weekday():
                # lunes=0 domingo=6
                if str(fecha_actual.weekday()) in dias_clase:

                    Clase.objects.create(

                        curso=curso,

                        titulo=f'Clase {numero_clase}',

                        descripcion=descripcion_clase,

                        fecha=fecha_actual,

                        hora_inicio=hora_inicio,

                        hora_fin=hora_fin
                    )

                    numero_clase += 1

                fecha_actual += timedelta(days=1)

            messages.success(
                request,
                'Curso y clases creados correctamente.'
            )

            return redirect(
                'lista_cursos'
            )

    else:

        form = CursoForm()

    context = {
        'form': form
    }

    return render(
        request,
        'admin/crear.html',
        context
    )

@login_required
@rol_requerido('ADMIN')
def editar_curso(request, curso_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    curso = get_object_or_404(
        Curso,
        id=curso_id
    )

    if request.method == 'POST':

        form = CursoForm(
            request.POST,
            request.FILES,
            instance=curso
        )

        if form.is_valid():

            # 🔹 GUARDAR CURSO
            curso = form.save()

            # 🔹 ELIMINAR CLASES ANTERIORES
            curso.clases.all().delete()

            # 🔹 OBTENER DATOS
            dias_clase = form.cleaned_data['dias_clase']

            hora_inicio = form.cleaned_data['hora_inicio_clase']

            hora_fin = form.cleaned_data['hora_fin_clase']

            descripcion_clase = form.cleaned_data['descripcion_clase']

            fecha_inicio = curso.fecha_inicio

            fecha_fin = curso.fecha_fin

            fecha_actual = fecha_inicio

            numero_clase = 1

            # 🔹 CREAR NUEVAS CLASES
            while fecha_actual <= fecha_fin:

                if str(fecha_actual.weekday()) in dias_clase:

                    Clase.objects.create(

                        curso=curso,

                        titulo=f'Clase {numero_clase}',

                        descripcion=descripcion_clase,

                        fecha=fecha_actual,

                        hora_inicio=hora_inicio,

                        hora_fin=hora_fin

                    )

                    numero_clase += 1

                fecha_actual += timedelta(days=1)

            messages.success(
                request,
                'Curso y clases actualizados correctamente.'
            )

            return redirect(
                'lista_cursos'
            )

    else:

        form = CursoForm(
            instance=curso
        )

    context = {
        'form': form,
        'curso': curso
    }

    return render(
        request,
        'admin/editar.html',
        context
    )

@login_required
@rol_requerido('ADMIN')
def eliminar_curso(request, id):
    curso = get_object_or_404(Curso, id=id)

    if request.method == 'POST':
        curso.delete()
        return redirect('lista_cursos')

    return render(request, 'cursos/eliminar_curso.html', {'curso': curso})

@login_required
@rol_requerido('PARTICIPANTE')
def cursos_disponibles(request):
    hoy = now().date()
    cursos = Curso.objects.filter(
        estado='ACTIVO',
        fecha_limite_inscripcion__gte=hoy
    )
    return render(request, 'participante/cursos_disponibles.html', {
        'cursos': cursos
    })

@login_required
@rol_requerido('PARTICIPANTE')
def inscribirse_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    perfil = request.user.perfil

    # ❌ fuera de fecha
    if curso.fecha_limite_inscripcion < now().date():
        return render(request, 'cursos/inscripcion_cerrada.html')

    # ❌ ya inscrito
    if Inscripcion.objects.filter(
        participante=perfil,
        curso=curso
    ).exists():
        return render(request, 'cursos/ya_inscrito.html')

    Inscripcion.objects.create(
        participante=perfil,
        curso=curso
    )

    return redirect('mis_cursos')

@login_required
@rol_requerido('PARTICIPANTE')
def mis_cursos(request):
    perfil = request.user.perfil
    inscripciones = Inscripcion.objects.filter(
        participante=perfil,
        estado='INSCRITO'
    )

    return render(request, 'participante/mis_cursos.html', {
        'inscripciones': inscripciones
    })


## funcionalidades de los catequistas##


@login_required
@rol_requerido('CATEQUISTA')
def cursos_catequista(request):
    perfil = request.user.perfil

    cursos = Curso.objects.filter(
        catequistas=perfil,
        estado='ACTIVO'
    )

    return render(request, 'catequista/cursos_catequista.html', {
        'cursos': cursos
    })

@login_required
@rol_requerido('CATEQUISTA')
def clases_curso(request, curso_id):

    curso = get_object_or_404(Curso, id=curso_id)

    clases = Clase.objects.filter(curso=curso).order_by('fecha')
    
    # 🔹 DATOS PARA RESUMEN DE ASISTENCIAS
    inscripciones = Inscripcion.objects.filter(
        curso=curso, 
        estado='INSCRITO'
    ).select_related('participante', 'participante__user')
    
    # 📊 CONSTRUIR DATOS DE ASISTENCIAS
    asistencias_resumen = []
    
    for inscripcion in inscripciones:
        participante = inscripcion.participante
        asistencias_presentes = 0
        total_clases = clases.count()
        
        fila_asistencia = {
            'nombre': f"{participante.user.first_name} {participante.user.last_name}",
            'detalles': []
        }
        
        for clase in clases:
            asistencia = Asistencia.objects.filter(
                clase=clase,
                participante=participante
            ).first()
            
            estado = asistencia.estado if asistencia else "AUSENTE"
            
            if estado == "PRESENTE":
                asistencias_presentes += 1
            
            fila_asistencia['detalles'].append({
                'estado': estado,
                'fecha': clase.fecha
            })
        
        porcentaje = int((asistencias_presentes / total_clases) * 100) if total_clases > 0 else 0
        fila_asistencia['porcentaje'] = porcentaje
        fila_asistencia['presentes'] = asistencias_presentes
        fila_asistencia['total'] = total_clases
        
        asistencias_resumen.append(fila_asistencia)

    return render(request, 'catequista/clases_curso.html', {
        'curso': curso,
        'clases': clases,
        'asistencias_resumen': asistencias_resumen,
        'inscripciones': inscripciones
    })

## asistencia##
@login_required
@rol_requerido('CATEQUISTA')
def tomar_asistencia(request, clase_id):

    clase = get_object_or_404(Clase, id=clase_id)

    inscripciones = Inscripcion.objects.filter(
        curso=clase.curso,
        estado='INSCRITO'
    )

    # cargar asistencias existentes
    asistencias = Asistencia.objects.filter(clase=clase)

    asistencia_dict = {
        a.participante.id: a
        for a in asistencias
    }

    if request.method == "POST":

        for inscripcion in inscripciones:

            participante = inscripcion.participante

            estado = request.POST.get(f"estado_{participante.id}")
            observacion = request.POST.get(f"obs_{participante.id}")

            Asistencia.objects.update_or_create(
                clase=clase,
                participante=participante,
                defaults={
                    'estado': estado,
                    'observacion': observacion
                }
            )

        return redirect('clases_curso', curso_id=clase.curso.id)

    return render(request, 'catequista/tomar_asistencia.html', {
        'clase': clase,
        'inscripciones': inscripciones,
        'asistencia_dict': asistencia_dict
    })

#asistencia por qr

def registrar_asistencia_qr(request, clase_id):

    clase = get_object_or_404(Clase, id=clase_id)

    if request.method == "POST":
        try:
            qr_data = request.POST.get("qr_data")

            perfil_id = qr_data.split(":")[1]
            perfil = Perfil.objects.get(id=perfil_id)

            Asistencia.objects.update_or_create(
                clase=clase,
                participante=perfil,
                defaults={'estado': 'PRESENTE'}
            )

            total_presentes = Asistencia.objects.filter(
                clase=clase,
                estado='PRESENTE'
            ).count()

            total_inscritos = Inscripcion.objects.filter(
                curso=clase.curso,
                estado='INSCRITO'
            ).count()

            return JsonResponse({
                'status': 'ok',
                'nombre': f"{perfil.user.first_name} {perfil.user.last_name}",
                'total': total_presentes,
                'inscritos': total_inscritos
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})

    total_presentes = Asistencia.objects.filter(
        clase=clase,
        estado='PRESENTE'
    ).count()

    total_inscritos = Inscripcion.objects.filter(
        curso=clase.curso,
        estado='INSCRITO'
    ).count()

    return render(request, "catequista/asistencia_qr.html", {
        "clase": clase,
        "total_presentes": total_presentes,
        "total_inscritos": total_inscritos
    })
#mi qr

@login_required
def mi_qr(request):

    perfil = request.user.perfil

    if not perfil.qr:

        data = f"USER:{perfil.id}"

        qr = qrcode.make(data)

        buffer = BytesIO()
        qr.save(buffer)

        perfil.qr.save(
            f'qr_{perfil.id}.png',
            File(buffer),
            save=True
        )

    return render(request, 'usuarios/mi_qr.html', {
        'perfil': perfil
    })

##detalles del curso

def detalle_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    clases = Clase.objects.filter(curso=curso)
    # 👇 NUEVO
    cuestionarios = Cuestionario.objects.filter(clase__curso=curso)
    tareas = Tarea.objects.filter(clase__curso=curso)

    tareas_con_estado = []

    for tarea in tareas:
        entrega = EntregaTarea.objects.filter(
            tarea=tarea,
            estudiante=request.user
        ).first()

        estado = "Pendiente"
        nota = None

        if entrega:
            estado = "Entregado"
            nota = entrega.calificacion

        tareas_con_estado.append({
            'tarea': tarea,
            'estado': estado,
            'nota': nota
        })

    # 🧠 CUESTIONARIOS CON ESTADO
    cuestionarios_con_estado = []
    for c in cuestionarios:
        intentos = Intento.objects.filter(usuario=request.user, cuestionario=c)
        mejor = intentos.order_by('-puntaje').first() if intentos.exists() else None
        
        fecha_pasada = c.fecha_limite and timezone.now() > c.fecha_limite
        
        estado = "Pendiente"
        if intentos.exists():
            if c.es_unico:
                estado = "Resuelto"
            else:
                estado = "Resuelto (Múltiples)"
        
        cuestionarios_con_estado.append({
            'cuestionario': c,
            'intentos': intentos.count(),
            'mejor': mejor,
            'estado': estado,
            'fecha_pasada': fecha_pasada,
            'es_unico': c.es_unico
        })

    # 📊 PROGRESO
    total_tareas = tareas.count()
    entregadas = EntregaTarea.objects.filter(
        tarea__clase__curso=curso,
        estudiante=request.user
    ).count()

    progreso = 0
    if total_tareas > 0:
        progreso = int((entregadas / total_tareas) * 100)

    return render(request, 'participante/detalle_curso.html', {
        'curso': curso,
        'clases': clases,
        'tareas': tareas_con_estado,
        'progreso': progreso,
        'cuestionarios': cuestionarios_con_estado
    })

## exportar a pdf participantes
def exportar_participantes_pdf(request, id):

    curso = get_object_or_404(Curso, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="participantes_{curso.nombre}.pdf"'

    p = canvas.Canvas(response)

    inscripciones = Inscripcion.objects.filter(
        curso=curso,
        estado='INSCRITO'
    )

    y = 800

    p.drawString(100, y, f"Participantes - {curso.nombre}")
    y -= 30

    for i in inscripciones:
        user = i.participante.user
        texto = f"{user.username} | {user.first_name} {user.last_name} | {user.email}"
        p.drawString(50, y, texto)
        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    return response



def exportar_asistencia_curso_pdf(request, curso_id):

    curso = get_object_or_404(Curso, id=curso_id)

    clases = Clase.objects.filter(curso=curso).order_by('fecha')
    inscripciones = Inscripcion.objects.filter(curso=curso, estado='INSCRITO')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_asistencia_{curso.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    elementos = []

    # 🏫 ENCABEZADO INSTITUCIONAL
    elementos.append(Paragraph("REPORTE INSTITUCIONAL DE ASISTENCIA", styles['Title']))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"<b>Curso:</b> {curso.nombre}", styles['Normal']))
    elementos.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elementos.append(Spacer(1, 20))

    # 📊 TABLA
    headers = ["Participante"]

    for clase in clases:
        headers.append(clase.fecha.strftime("%d/%m"))

    headers.append("% Asistencia")

    data = [headers]

    resumen_presentes = 0
    resumen_total = 0

    for ins in inscripciones:

        nombre = f"{ins.participante.user.first_name} {ins.participante.user.last_name}"

        fila = [nombre]

        asistencias_presentes = 0

        for clase in clases:

            asistencia = Asistencia.objects.filter(
                clase=clase,
                participante=ins.participante
            ).first()

            if asistencia:
                estado = asistencia.estado
            else:
                estado = "AUSENTE"

            if estado == "PRESENTE":
                asistencias_presentes += 1

            fila.append(estado)

        total_clases = len(clases)
        porcentaje = int((asistencias_presentes / total_clases) * 100) if total_clases > 0 else 0

        fila.append(f"{porcentaje}%")

        resumen_presentes += asistencias_presentes
        resumen_total += total_clases

        data.append(fila)

    tabla = Table(data, repeatRows=1)

    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ])

    # 🎨 COLORES
    for fila_idx in range(1, len(data)):
        for col_idx in range(1, len(headers)-1):

            estado = data[fila_idx][col_idx]

            if estado == "PRESENTE":
                color = colors.green
            elif estado == "PERMISO":
                color = colors.orange
            else:
                color = colors.red

            estilo.add('BACKGROUND', (col_idx, fila_idx), (col_idx, fila_idx), color)
            estilo.add('TEXTCOLOR', (col_idx, fila_idx), (col_idx, fila_idx), colors.white)

    # 🎯 COLOR POR PORCENTAJE
    for fila_idx in range(1, len(data)):
        porcentaje_texto = data[fila_idx][-1].replace('%','')
        porcentaje = int(porcentaje_texto)

        if porcentaje >= 80:
            color = colors.green
        elif porcentaje >= 50:
            color = colors.orange
        else:
            color = colors.red

        estilo.add('BACKGROUND', (-1, fila_idx), (-1, fila_idx), color)
        estilo.add('TEXTCOLOR', (-1, fila_idx), (-1, fila_idx), colors.white)

    tabla.setStyle(estilo)

    elementos.append(tabla)
    elementos.append(Spacer(1, 25))

    # 📊 RESUMEN GENERAL
    promedio = int((resumen_presentes / resumen_total) * 100) if resumen_total > 0 else 0

    elementos.append(Paragraph("<b>Resumen General</b>", styles['Heading2']))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"Asistencia promedio del curso: <b>{promedio}%</b>", styles['Normal']))
    elementos.append(Spacer(1, 5))

    elementos.append(Paragraph(
        "Leyenda: Verde = Presente | Naranja = Permiso | Rojo = Ausente",
        styles['Italic']
    ))

    doc.build(elementos)

    return response


# 📋 HISTORIAL DE ASISTENCIAS DEL PARTICIPANTE
@login_required
@rol_requerido('PARTICIPANTE')
def historial_asistencias(request):
    """
    Muestra el historial completo de asistencias del participante en todos sus cursos.
    """
    perfil = request.user.perfil
    
    # Obtener todos los cursos en los que está inscrito
    inscripciones = Inscripcion.objects.filter(
        participante=perfil,
        estado='INSCRITO'
    ).select_related('curso')
    
    # Agrupar asistencias por curso
    historial = {}
    
    for inscripcion in inscripciones:
        curso = inscripcion.curso
        
        # Obtener asistencias de este participante en este curso
        asistencias = Asistencia.objects.filter(
            participante=perfil,
            clase__curso=curso
        ).select_related('clase').order_by('clase__fecha')
        
        if asistencias.exists():
            # Calcular estadísticas
            total_clases = Clase.objects.filter(curso=curso).count()
            presentes = asistencias.filter(estado='PRESENTE').count()
            ausentes = asistencias.filter(estado='AUSENTE').count()
            permisos = asistencias.filter(estado='PERMISO').count()
            
            porcentaje = int((presentes / total_clases) * 100) if total_clases > 0 else 0
            
            historial[curso] = {
                'asistencias': asistencias,
                'total_clases': total_clases,
                'presentes': presentes,
                'ausentes': ausentes,
                'permisos': permisos,
                'porcentaje': porcentaje
            }
    
    context = {
        'historial': historial,
        'perfil': perfil
    }
    
    return render(request, 'participante/historial_asistencias.html', context)

    doc.build(elementos)

    return response
##____________________________________________________________________________________________
@login_required
def lista_inscripciones(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    inscripciones = Inscripcion.objects.select_related(
        'participante__user',
        'curso'
    )

    context = {
        'inscripciones': inscripciones
    }

    return render(
        request,
        'cursos/inscripciones/lista.html',
        context
    )

@login_required
def crear_inscripcion(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        form = InscripcionForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Participante inscrito correctamente.'
            )

            return redirect(
                'lista_inscripciones'
            )

    else:

        form = InscripcionForm()

    context = {
        'form': form
    }

    return render(
        request,
        'cursos/inscripciones/crear.html',
        context
    )

@login_required
def lista_clases(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    clases = Clase.objects.select_related(
        'curso'
    ).order_by('-fecha')

    context = {
        'clases': clases
    }

    return render(
        request,
        'cursos/clases/lista.html',
        context
    )

@login_required
def crear_clase(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        form = ClaseForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Clase creada correctamente.'
            )

            return redirect(
                'lista_clases'
            )

    else:

        form = ClaseForm()

    context = {
        'form': form
    }

    return render(
        request,
        'cursos/clases/crear.html',
        context
    )

@login_required
def editar_clase(request, clase_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    clase = get_object_or_404(
        Clase,
        id=clase_id
    )

    if request.method == 'POST':

        form = ClaseForm(
            request.POST,
            instance=clase
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Clase actualizada correctamente.'
            )

            return redirect(
                'lista_clases'
            )

    else:

        form = ClaseForm(
            instance=clase
        )

    context = {
        'form': form,
        'clase': clase
    }

    return render(
        request,
        'cursos/clases/editar.html',
        context
    )

@login_required
def lista_asistencia(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    clases = Clase.objects.select_related(
        'curso'
    ).order_by('-fecha')

    context = {
        'clases': clases
    }

    return render(
        request,
        'cursos/asistencia/lista.html',
        context
    )

@login_required
def tomar_asistencia_admin(request, clase_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    clase = get_object_or_404(
        Clase,
        id=clase_id
    )

    # INSCRITOS DEL CURSO
    inscripciones = Inscripcion.objects.filter(
        curso=clase.curso,
        estado='INSCRITO'
    ).select_related(
        'participante__user'
    )

    # CREAR ASISTENCIAS SI NO EXISTEN
    for inscripcion in inscripciones:

        Asistencia.objects.get_or_create(

            clase=clase,
            participante=inscripcion.participante,

            defaults={
                'estado': 'AUSENTE'
            }
        )

    asistencias = Asistencia.objects.filter(
        clase=clase
    ).select_related(
        'participante__user'
    )

    # GUARDAR
    if request.method == 'POST':

        for asistencia in asistencias:

            estado = request.POST.get(
                f'estado_{asistencia.id}'
            )

            observacion = request.POST.get(
                f'observacion_{asistencia.id}'
            )

            asistencia.estado = estado
            asistencia.observacion = observacion
            asistencia.save()

        messages.success(
            request,
            'Asistencia guardada correctamente.'
        )

        return redirect(
            'tomar_asistencia_admin',
            clase.id
        )

    context = {

        'clase': clase,
        'asistencias': asistencias

    }

    return render(
        request,
        'cursos/asistencia/tomar.html',
        context
    )

