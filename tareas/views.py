import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponse

# Modelos
from .models import (
    Tarea, MaterialTarea, EntregaTarea, Notificacion, ArchivoEntrega
)
from cursos.models import Clase, Inscripcion, Curso
from cuestionario.models import Cuestionario

# Servicios
from .google_drive_oauth import subir_archivo_drive, get_flow
from .notifications_service import crear_notificacion_y_email
from usuarios.decorators import rol_requerido
from .forms import TareaForm

@login_required
def crear_tarea(request, clase_id):
    clase = Clase.objects.get(id=clase_id)
    if not request.session.get('credentials'):
        return redirect('google_login')
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descripcion = request.POST['descripcion']
        fecha_entrega = request.POST['fecha_entrega']

        permitir_tardia = request.POST.get('permitir_tardia') == 'on'
        fecha_limite_tardia = request.POST.get('fecha_limite_tardia')

        tarea = Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_entrega=fecha_entrega,
            permitir_tardia=permitir_tardia,
            fecha_limite_tardia=fecha_limite_tardia or None,
            clase=clase,
            catequista=request.user
        )

        # 📁 SUBIR MÚLTIPLES ARCHIVOS
        archivos = request.FILES.getlist('archivos')

        for archivo in archivos:
            link = subir_archivo_drive(request, archivo)

            # 🔥 IGUAL QUE EN entregar_tarea
            if not link:
                return redirect('google_login')

            MaterialTarea.objects.create(
                tarea=tarea,
                archivo_url=link,
                nombre=archivo.name
            )
        return redirect('panel_catequista', curso_id=clase.curso.id)

    return render(request, 'tareas/crear_tarea.html', {'clase': clase})


def ver_tareas(request, clase_id):
    tareas = Tarea.objects.filter(clase_id=clase_id)
    return render(request, 'tareas/lista_tareas.html', {'tareas': tareas})


# =========================
# 📤 ENTREGAR TAREA (OAUTH)
# =========================
@login_required
def entregar_tarea(request, tarea_id):
    tarea = Tarea.objects.get(id=tarea_id)
    if not request.session.get('credentials'):
        return redirect('google_login')
    # VALIDAR FECHA
    if not tarea.puede_entregar():
        return render(request, 'tareas/error.html', {
            'mensaje': 'La tarea está cerrada'
        })

    entrega_existente = EntregaTarea.objects.filter(
        tarea=tarea,
        estudiante=request.user
    ).first()

    if request.method == 'POST':
        archivos = request.FILES.getlist('archivos')

        # 🔹 crear entrega si no existe
        if not entrega_existente:
            entrega = EntregaTarea.objects.create(
                tarea=tarea,
                estudiante=request.user
            )
        else:
            entrega = entrega_existente

        # 🔥 subir múltiples archivos
        for archivo in archivos:
            link_drive = subir_archivo_drive(request, archivo)

            if not link_drive:
                return redirect('google_login')

            ArchivoEntrega.objects.create(
                entrega=entrega,
                archivo_url=link_drive,
                nombre=archivo.name
            )

        # 📩 correo
        if request.user.email:
            send_mail(
                'Tarea enviada',
                f'Has enviado la tarea: {tarea.titulo}',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=True,
            )
        return redirect('detalle_curso', id=tarea.clase.curso.id)

    return render(request, 'participante/entregar_tarea.html', {'tarea': tarea})

# =========================
# 📝 CALIFICAR TAREA
# =========================
@login_required
@rol_requerido('CATEQUISTA')
def calificar_tarea(request, entrega_id):
    entrega = EntregaTarea.objects.get(id=entrega_id)

    if request.method == 'POST':
        entrega.calificacion = request.POST['calificacion']
        entrega.observacion = request.POST['observacion']
        entrega.save()

        # 🔔 NOTIFICACIÓN CON EMAIL
        mensaje = f"Tu tarea '{entrega.tarea.titulo}' fue calificada con {entrega.calificacion}"
        crear_notificacion_y_email(
            usuario=entrega.estudiante,
            mensaje=mensaje,
            asunto="Tarea Calificada"
        )

        return redirect('ver_entregas', tarea_id=entrega.tarea.id)

    return render(request, 'tareas/calificar.html', {'entrega': entrega})


# =========================
# 👀 VER ENTREGAS
# =========================
@login_required
@rol_requerido('CATEQUISTA')
def ver_entregas(request, tarea_id):
    tarea = Tarea.objects.get(id=tarea_id)
    entregas = EntregaTarea.objects.filter(tarea=tarea)

    return render(request, 'tareas/ver_entregas.html', {
        'tarea': tarea,
        'entregas': entregas
    })


# =========================
# ❌ CANCELAR ENTREGA
# =========================
@login_required
def cancelar_entrega(request, tarea_id):
    entrega = EntregaTarea.objects.filter(
        tarea_id=tarea_id,
        estudiante=request.user
    ).first()

    if entrega:
        curso_id = entrega.tarea.clase.curso.id
        entrega.delete()
        return redirect('detalle_curso', id=curso_id)

    return redirect('detalle_curso', id=tarea_id)



##login con google
from django.shortcuts import redirect
from .google_drive_oauth import get_flow


def google_login(request):
    flow = get_flow()

    auth_url, state = flow.authorization_url(prompt='consent')

    # 🔥 guardar TODO
    request.session['state'] = state
    request.session['code_verifier'] = flow.code_verifier

    return redirect(auth_url)

def oauth2callback(request):
    state = request.session.get('state')
    code_verifier = request.session.get('code_verifier')

    flow = get_flow()
    flow.state = state
    flow.code_verifier = code_verifier  # 🔥 clave

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('/')

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


# =========================
# 📊 PANEL CATEQUISTA PRO
# =========================
@login_required
@rol_requerido('CATEQUISTA')
def panel_catequista(request, curso_id):

    # ✅ CURSO
    curso = get_object_or_404(Curso, id=curso_id)

    # ✅ TODAS LAS CLASES DEL CURSO
    clases = Clase.objects.filter(
        curso=curso
    ).order_by('fecha')

    # ✅ PRIMERA CLASE (para crear tareas/cuestionarios)
    clase = clases.first()

    # ✅ PARTICIPANTES
    participantes = Inscripcion.objects.filter(
        curso=curso,
        estado='INSCRITO',
        participante__isnull=False,
        participante__user__isnull=False
    ).select_related(
        'participante',
        'participante__user'
    ).distinct()

    # ✅ TAREAS
    tareas = Tarea.objects.filter(
        clase__curso=curso
    ).select_related('clase').distinct()

    # ✅ CUESTIONARIOS
    cuestionarios = Cuestionario.objects.filter(
        clase__curso=curso
    ).select_related('clase').distinct()

    # =========================
    # DASHBOARD
    # =========================

    total_tareas = tareas.count()

    total_entregas = EntregaTarea.objects.filter(
        tarea__clase__curso=curso
    ).count()

    estudiantes = EntregaTarea.objects.filter(
        tarea__clase__curso=curso
    ).values('estudiante').distinct().count()

    pendientes = 0

    for tarea in tareas:

        entregas_tarea = EntregaTarea.objects.filter(
            tarea=tarea
        ).count()

        if entregas_tarea < estudiantes:
            pendientes += 1

    # =========================
    # RENDER
    # =========================

    return render(request, 'catequista/panel_catequista.html', {

        'curso': curso,
        'clase': clase,  # 👈 SOLO para botones crear
        'clases': clases,  # 👈 LISTA COMPLETA
        'participantes': participantes,

        'tareas': tareas,
        'cuestionarios': cuestionarios,

        'total_tareas': total_tareas,
        'total_entregas': total_entregas,
        'pendientes': pendientes,
    })

from django.db.models import Avg, Count
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Avg
from cursos.models import Curso
from .models import Tarea, EntregaTarea

@login_required
@rol_requerido('CATEQUISTA')
def reporte_tareas(request, curso_id):

    curso = Curso.objects.get(id=curso_id)

    tareas = Tarea.objects.filter(clase__curso=curso)

    total_tareas = tareas.count()

    entregas = EntregaTarea.objects.filter(tarea__clase__curso=curso)
    total_entregas = entregas.count()

    promedio = entregas.aggregate(avg=Avg('calificacion'))

    # 📈 evolución
    ultimas = entregas.order_by('id')[:20]
    fechas = [str(i.id) for i in ultimas]
    notas = [i.calificacion or 0 for i in ultimas]

    # 📊 promedio por tarea
    nombres = []
    promedios = []

    for t in tareas:
        prom = EntregaTarea.objects.filter(tarea=t).aggregate(avg=Avg('calificacion'))['avg'] or 0
        nombres.append(t.titulo)
        promedios.append(prom)

    # 🏆 ranking (con clase incluida)
    ranking = entregas.order_by('-calificacion')[:10]

    return render(request, 'catequista/reporte_tareas.html', {
        'curso': curso,  # 🔥 IMPORTANTE (ya no clase)
        'total_tareas': total_tareas,
        'total_entregas': total_entregas,
        'promedio': promedio,

        'fechas': fechas,
        'notas': notas,

        'nombres': nombres,
        'promedios': promedios,

        'ranking': ranking
    })


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.db.models import Avg
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

from cursos.models import Curso
from .models import Tarea, EntregaTarea


def reporte_tareas_pdf(request, curso_id):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_tareas_curso.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    curso = Curso.objects.get(id=curso_id)

    # 🔥 SOLO DATOS DEL CURSO
    tareas = Tarea.objects.filter(clase__curso=curso)
    entregas = EntregaTarea.objects.filter(tarea__clase__curso=curso)

    elementos = []

    # =========================
    # 🏫 HEADER
    # =========================

    elementos.append(Paragraph("<b>SISTEMA EDUCATIVO</b>", styles['Title']))
    elementos.append(Paragraph("Reporte de Tareas del Curso", styles['Heading2']))

    fecha = datetime.now().strftime("%d/%m/%Y")
    elementos.append(Paragraph(f"Fecha: {fecha}", styles['Normal']))
    elementos.append(Paragraph(f"Curso: {curso}", styles['Normal']))

    elementos.append(Spacer(1, 20))

    # =========================
    # 📊 RESUMEN
    # =========================

    total_tareas = tareas.count()
    total_entregas = entregas.count()
    promedio = entregas.aggregate(avg=Avg('calificacion'))['avg'] or 0

    resumen = [
        ["Indicador", "Valor"],
        ["Total Tareas", total_tareas],
        ["Total Entregas", total_entregas],
        ["Promedio General", round(promedio, 2)],
    ]

    tabla_resumen = Table(resumen)

    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ]))

    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 20))

    # =========================
    # 🏆 RANKING (CON CLASE)
    # =========================

    ranking = entregas.select_related('tarea__clase', 'estudiante')\
                      .order_by('-calificacion')[:15]

    data = [["#", "Estudiante", "Clase", "Tarea", "Nota"]]

    for i, e in enumerate(ranking, start=1):
        data.append([
            i,
            e.estudiante.username,
            e.tarea.clase.titulo,  # 🔥 igual que tu HTML
            e.tarea.titulo,
            e.calificacion or 0
        ])

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ]))

    elementos.append(Paragraph("<b>Ranking de Estudiantes</b>", styles['Heading2']))
    elementos.append(Spacer(1, 10))
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    # =========================
    # 📊 GRAFICA 1: PROMEDIO POR TAREA
    # =========================

    nombres = []
    promedios = []

    for t in tareas:
        prom = EntregaTarea.objects.filter(tarea=t).aggregate(avg=Avg('calificacion'))['avg'] or 0
        nombres.append(t.titulo)
        promedios.append(prom)

    buffer = BytesIO()
    plt.figure()
    plt.bar(nombres, promedios)
    plt.title("Promedio por Tarea")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)

    elementos.append(Paragraph("<b>Promedio por Tarea</b>", styles['Heading2']))
    elementos.append(Image(buffer, width=400, height=200))
    elementos.append(Spacer(1, 20))

    # =========================
    # 📈 GRAFICA 2: EVOLUCIÓN
    # =========================

    ultimas = entregas.order_by('id')[:20]

    x = [str(i.id) for i in ultimas]
    y = [i.calificacion or 0 for i in ultimas]

    buffer2 = BytesIO()
    plt.figure()
    plt.plot(x, y)
    plt.title("Evolución de Notas")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(buffer2, format='png')
    plt.close()

    buffer2.seek(0)

    elementos.append(Paragraph("<b>Evolución de Notas</b>", styles['Heading2']))
    elementos.append(Image(buffer2, width=400, height=200))

    elementos.append(Spacer(1, 30))

    # =========================
    # ✍️ PIE
    # =========================

    elementos.append(Paragraph(
        "Documento generado automáticamente por el sistema académico",
        styles['Italic']
    ))

    doc.build(elementos)

    return response

#_____________________________________________________________________________________________
@login_required
def lista_tareas(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    tareas = Tarea.objects.select_related(
        'clase',
        'clase__curso',
        'catequista'
    ).order_by('-fecha_publicacion')

    context = {
        'tareas': tareas
    }

    return render(
        request,
        'tareas/lista.html',
        context
    )

@login_required
def crear_tarea_admin(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        form = TareaForm(request.POST)

        if form.is_valid():

            tarea = form.save(commit=False)

            tarea.catequista = request.user

            tarea.save()

            messages.success(
                request,
                'Tarea creada correctamente.'
            )

            return redirect(
                'lista_tareas'
            )

    else:

        form = TareaForm()

    context = {
        'form': form
    }

    return render(
        request,
        'tareas/crear.html',
        context
    )

@login_required
def editar_tarea(request, tarea_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    tarea = get_object_or_404(
        Tarea,
        id=tarea_id
    )

    if request.method == 'POST':

        form = TareaForm(
            request.POST,
            instance=tarea
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Tarea actualizada correctamente.'
            )

            return redirect(
                'lista_tareas'
            )

    else:

        form = TareaForm(
            instance=tarea
        )

    context = {
        'form': form,
        'tarea': tarea
    }

    return render(
        request,
        'tareas/editar.html',
        context
    )

@login_required
def ver_entregas_admin(request, tarea_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    tarea = get_object_or_404(
        Tarea,
        id=tarea_id
    )

    entregas = EntregaTarea.objects.filter(
        tarea=tarea
    ).select_related(
        'estudiante'
    ).order_by('-fecha_entrega')

    context = {

        'tarea': tarea,
        'entregas': entregas

    }

    return render(
        request,
        'admin/ver_entregas.html',
        context
    )

@login_required
def calificar_entrega(request, entrega_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    entrega = get_object_or_404(
        EntregaTarea,
        id=entrega_id
    )

    if request.method == 'POST':

        calificacion = request.POST.get(
            'calificacion'
        )

        observacion = request.POST.get(
            'observacion'
        )

        entrega.calificacion = calificacion
        entrega.observacion = observacion

        entrega.save()

        messages.success(
            request,
            'Entrega calificada correctamente.'
        )

        return redirect(
            'ver_entregas_admin',
            entrega.tarea.id
        )

    context = {
        'entrega': entrega
    }

    return render(
        request,
        'admin/calificar.html',
        context
    )

