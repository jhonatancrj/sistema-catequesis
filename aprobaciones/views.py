from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import now



from usuarios.decorators import rol_requerido

from cursos.models import (
    Asistencia,
    Clase,
    Curso,
    Inscripcion,
)

from tareas.models import (
    EntregaTarea,
    Tarea,
)

from cuestionario.models import (
    Cuestionario,
    Intento,
)

from aprobaciones.models import ResultadoCurso
from django.db.models import Q
from .services import *
from .utils import verificar_aprobacion

from django.core.mail import EmailMessage

from django.template.loader import render_to_string


from django.http import HttpResponse

import tempfile
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count
from .forms import AprobadoManualForm

@login_required
@rol_requerido('CATEQUISTA')
def enviar_aprobados(request, id):

    curso = get_object_or_404(
        Curso,
        id=id
    )

    # ===================================
    # VALIDAR FECHA FINALIZACIÓN
    # ===================================

    hoy = timezone.now().date()

    fecha_fin = curso.fecha_fin

    if hoy < fecha_fin:

        messages.error(
            request,
            'El envío se habilitará cuando finalice el curso'
        )

        return redirect(
            'reporte_curso',
            id=curso.id
        )

    # ===================================
    # VALIDAR PLAZO DE 3 DÍAS
    # ===================================

    dias_pasados = (
        hoy - fecha_fin
    ).days

    # si pasaron más de 3 días
    if dias_pasados > 3:

        messages.error(
            request,
            'El plazo para enviar la lista ya finalizó'
        )

        return redirect(
            'reporte_curso',
            id=curso.id
        )

    # ===================================
    # INSCRIPCIONES
    # ===================================

    inscripciones = Inscripcion.objects.filter(
        curso=curso,
        estado='INSCRITO'
    )

    # ===================================
    # TAREAS Y CUESTIONARIOS
    # ===================================

    tareas = Tarea.objects.filter(
        clase__curso=curso
    )

    cuestionarios = Cuestionario.objects.filter(
        clase__curso=curso
    )

    # ===================================
    # RECORRER PARTICIPANTES
    # ===================================

    for inscripcion in inscripciones:

        participante = inscripcion.participante

        usuario = participante.user

        # ===================================
        # FALTAS
        # ===================================

        faltas = Asistencia.objects.filter(
            participante=participante,
            clase__curso=curso,
            estado='AUSENTE'
        ).count()

        # ===================================
        # PROMEDIO TAREAS
        # ===================================

        notas_tareas = []

        for tarea in tareas:

            entrega = EntregaTarea.objects.filter(
                estudiante=usuario,
                tarea=tarea
            ).first()

            if (
                entrega and
                entrega.calificacion is not None
            ):

                notas_tareas.append(
                    entrega.calificacion
                )

            else:

                notas_tareas.append(0)

        if notas_tareas:

            promedio_tareas = (
                sum(notas_tareas)
                / len(notas_tareas)
            )

        else:

            promedio_tareas = 0

        # ===================================
        # PROMEDIO CUESTIONARIOS
        # ===================================

        notas_cuestionarios = []

        for cuestionario in cuestionarios:

            mejor_intento = Intento.objects.filter(
                usuario=usuario,
                cuestionario=cuestionario
            ).order_by('-puntaje').first()

            if mejor_intento:

                notas_cuestionarios.append(
                    mejor_intento.puntaje
                )

            else:

                notas_cuestionarios.append(0)

        if notas_cuestionarios:

            promedio_cuestionarios = (
                sum(notas_cuestionarios)
                / len(notas_cuestionarios)
            )

        else:

            promedio_cuestionarios = 0

        # ===================================
        # VERIFICAR APROBACIÓN
        # ===================================

        aprobado = (

            faltas < 3 and

            promedio_tareas >= 51 and

            promedio_cuestionarios >= 51
        )

        # ===================================
        # ESTADO FINAL
        # ===================================

        if aprobado:

            estado = 'APROBADO'

        else:

            estado = 'REPROBADO'

        # ===================================
        # ACTUALIZAR O CREAR RESULTADO
        # ===================================

        resultado = ResultadoCurso.objects.filter(
            participante=participante,
            curso=curso
        ).first()

        # ===================================
        # SI YA EXISTE
        # ===================================

        if resultado:

            resultado.promedio_tareas = round(
                promedio_tareas,
                1
            )

            resultado.promedio_cuestionarios = round(
                promedio_cuestionarios,
                1
            )

            resultado.faltas = faltas

            resultado.estado_final = estado

            resultado.sacramento = curso.sacramento

            resultado.gestion = curso.fecha_fin.year

            resultado.save()

        # ===================================
        # SI NO EXISTE
        # ===================================

        else:

            ResultadoCurso.objects.create(

                participante=participante,

                curso=curso,

                gestion=curso.fecha_fin.year,

                sacramento=curso.sacramento,

                promedio_tareas=round(
                    promedio_tareas,
                    1
                ),

                promedio_cuestionarios=round(
                    promedio_cuestionarios,
                    1
                ),

                faltas=faltas,

                estado_final=estado
            )

    # ===================================
    # MARCAR LISTA ENVIADA
    # ===================================

    curso.lista_enviada = True

    curso.fecha_envio_lista = timezone.now()

    curso.save()

    # ===================================
    # MENSAJE
    # ===================================

    messages.success(
        request,
        'Lista final enviada correctamente'
    )

    return redirect(
        'reporte_curso',
        id=curso.id
    )

@login_required
@rol_requerido('CATEQUISTA')
def lista_aprobados(request):

    aprobados = ResultadoCurso.objects.all()

    # ===================================
    # BUSCADOR
    # ===================================

    buscar = request.GET.get('buscar')

    if buscar:

        aprobados = aprobados.filter(

            Q(
                participante__user__first_name__icontains=buscar
            ) |

            Q(
                participante__user__last_name__icontains=buscar
            ) |

            Q(
                participante__user__username__icontains=buscar
            ) |

            Q(
                curso__nombre__icontains=buscar
            )
        )

    # ===================================
    # FILTRO GESTIÓN
    # ===================================

    gestion = request.GET.get('gestion')

    if gestion:

        aprobados = aprobados.filter(
            gestion=gestion
        )

    # ===================================
    # FILTRO SACRAMENTO
    # ===================================

    sacramento = request.GET.get('sacramento')

    if sacramento:

        aprobados = aprobados.filter(
            sacramento__nombre=sacramento
        )

    # ===================================
    # SOLO CURSOS DEL CATEQUISTA
    # ===================================

    perfil = request.user.perfil

    aprobados = aprobados.filter(
        curso__catequistas=perfil
    )

    # ===================================
    # DATOS FILTROS
    # ===================================

    gestiones = ResultadoCurso.objects.values_list(
        'gestion',
        flat=True
    ).distinct()

    sacramentos = ResultadoCurso.objects.select_related(
        'sacramento'
    ).values_list(
        'sacramento__nombre',
        flat=True
    ).distinct()

    return render(

        request,

        'aprobaciones/catequista/lista_aprobados.html',

        {
            'aprobados': aprobados,

            'gestiones': gestiones,

            'sacramentos': sacramentos
        }
    )

@login_required
@rol_requerido('CATEQUISTA')
def enviar_certificado(request, id):
    from weasyprint import HTML
    aprobado = get_object_or_404(
        ResultadoCurso,
        id=id
    )
    if aprobado.estado_final != 'APROBADO':

        messages.error(
            request,
            'No se puede enviar certificado a un reprobado'
        )

        return redirect('lista_aprobados')

    # ===================================
    # GENERAR HTML
    # ===================================

    html_string = render_to_string(

        'aprobaciones/pdf/certificado.html',

        {
            'aprobado': aprobado,
            'fecha': timezone.now()
        }
    )

    # ===================================
    # GENERAR PDF
    # ===================================

    html = HTML(
        string=html_string
    )

    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.pdf'
    )

    html.write_pdf(
        target=pdf_file.name
    )

    # ===================================
    # ENVIAR CORREO
    # ===================================

    correo = aprobado.participante.user.email

    email = EmailMessage(

        subject='Certificado de Participación',

        body=(
            'Adjuntamos su certificado '
            'de reconocimiento.'
        ),

        to=[correo]
    )

    email.attach_file(
        pdf_file.name
    )

    email.send()

    messages.success(
        request,
        '✅ Certificado enviado correctamente'
    )

    return redirect('lista_aprobados')

@login_required
@rol_requerido('CATEQUISTA')
def reporte_curso(request, id):

    curso = get_object_or_404(Curso, id=id)

    inscripciones = Inscripcion.objects.filter(
        curso=curso,
        estado='INSCRITO'
    )

    # ===================================
    # TOTAL DE CLASES
    # ===================================

    total_clases = Clase.objects.filter(
        curso=curso
    ).count()

    # ===================================
    # TOTAL TAREAS Y CUESTIONARIOS
    # ===================================

    tareas = Tarea.objects.filter(
        clase__curso=curso
    )

    cuestionarios = Cuestionario.objects.filter(
        clase__curso=curso
    )

    datos_participantes = []

    # ===================================
    # RECORRER PARTICIPANTES
    # ===================================

    for inscripcion in inscripciones:

        usuario = inscripcion.participante.user

        # ===================================
        # ASISTENCIAS
        # ===================================

        asistencias = Asistencia.objects.filter(
            participante=inscripcion.participante,
            clase__curso=curso,
            estado='PRESENTE'
        ).count()

        faltas = Asistencia.objects.filter(
            participante=inscripcion.participante,
            clase__curso=curso,
            estado='AUSENTE'
        ).count()

        porcentaje_asistencia = 0

        if total_clases > 0:

            porcentaje_asistencia = (
                asistencias / total_clases
            ) * 100

        # ===================================
        # TAREAS
        # ===================================

        notas_tareas = []

        for tarea in tareas:

            entrega = EntregaTarea.objects.filter(
                estudiante=usuario,
                tarea=tarea
            ).first()

            if (
                entrega and
                entrega.calificacion is not None
            ):

                notas_tareas.append(
                    entrega.calificacion
                )

            else:

                notas_tareas.append(0)

        if notas_tareas:

            promedio_tareas = (
                sum(notas_tareas)
                / len(notas_tareas)
            )

        else:

            promedio_tareas = 0

        porcentaje_tareas = promedio_tareas

        # ===================================
        # CUESTIONARIOS
        # ===================================

        notas_cuestionarios = []

        for cuestionario in cuestionarios:

            mejor_intento = Intento.objects.filter(
                usuario=usuario,
                cuestionario=cuestionario
            ).order_by('-puntaje').first()

            if mejor_intento:

                notas_cuestionarios.append(
                    mejor_intento.puntaje
                )

            else:

                notas_cuestionarios.append(0)

        if notas_cuestionarios:

            promedio_cuestionarios = (
                sum(notas_cuestionarios)
                / len(notas_cuestionarios)
            )

        else:

            promedio_cuestionarios = 0

        porcentaje_cuestionarios = (
            promedio_cuestionarios
        )

        # ===================================
        # ESTADO ACADÉMICO
        # ===================================

        if (
            faltas < 3 and
            promedio_tareas >= 60 and
            promedio_cuestionarios >= 60
        ):

            estado = "APROBANDO"

        elif (

            faltas == 2 or

            (
                promedio_tareas >= 51 and
                promedio_tareas < 70
            ) or

            (
                promedio_cuestionarios >= 51 and
                promedio_cuestionarios < 70
            )

        ):

            estado = "EN RIESGO"

        else:

            estado = "REPROBANDO"

        # ===================================
        # GUARDAR DATOS
        # ===================================

        datos_participantes.append({

            'usuario': usuario,

            'asistencias': asistencias,

            'faltas': faltas,

            'total_clases': total_clases,

            'porcentaje_asistencia': round(
                porcentaje_asistencia,
                1
            ),

            'promedio_tareas': round(
                promedio_tareas,
                1
            ),

            'porcentaje_tareas': round(
                porcentaje_tareas,
                1
            ),

            'promedio_cuestionarios': round(
                promedio_cuestionarios,
                1
            ),

            'porcentaje_cuestionarios': round(
                porcentaje_cuestionarios,
                1
            ),

            'estado': estado
        })

    return render(
        request,
        'aprobaciones/reporte_curso.html',
        {
            'curso': curso,
            'datos_participantes': datos_participantes
        }
    )


@login_required
@rol_requerido('CATEQUISTA')
def exportar_reporte_curso_pdf(request, id):
    from weasyprint import HTML
    curso = get_object_or_404(
        Curso,
        id=id
    )

    inscripciones = Inscripcion.objects.filter(
        curso=curso,
        estado='INSCRITO'
    )

    total_clases = Clase.objects.filter(
        curso=curso
    ).count()

    tareas = Tarea.objects.filter(
        clase__curso=curso
    )

    cuestionarios = Cuestionario.objects.filter(
        clase__curso=curso
    )

    datos_participantes = []

    # ===================================
    # RECORRER PARTICIPANTES
    # ===================================

    for inscripcion in inscripciones:

        usuario = inscripcion.participante.user

        asistencias = Asistencia.objects.filter(
            participante=inscripcion.participante,
            clase__curso=curso,
            estado='PRESENTE'
        ).count()

        faltas = Asistencia.objects.filter(
            participante=inscripcion.participante,
            clase__curso=curso,
            estado='AUSENTE'
        ).count()

        porcentaje_asistencia = 0

        if total_clases > 0:

            porcentaje_asistencia = (
                asistencias / total_clases
            ) * 100

        # ===================================
        # TAREAS
        # ===================================

        notas_tareas = []

        for tarea in tareas:

            entrega = EntregaTarea.objects.filter(
                estudiante=usuario,
                tarea=tarea
            ).first()

            if (
                entrega and
                entrega.calificacion is not None
            ):

                notas_tareas.append(
                    entrega.calificacion
                )

            else:

                notas_tareas.append(0)

        if notas_tareas:

            promedio_tareas = (
                sum(notas_tareas)
                / len(notas_tareas)
            )

        else:

            promedio_tareas = 0

        # ===================================
        # CUESTIONARIOS
        # ===================================

        notas_cuestionarios = []

        for cuestionario in cuestionarios:

            mejor_intento = Intento.objects.filter(
                usuario=usuario,
                cuestionario=cuestionario
            ).order_by('-puntaje').first()

            if mejor_intento:

                notas_cuestionarios.append(
                    mejor_intento.puntaje
                )

            else:

                notas_cuestionarios.append(0)

        if notas_cuestionarios:

            promedio_cuestionarios = (
                sum(notas_cuestionarios)
                / len(notas_cuestionarios)
            )

        else:

            promedio_cuestionarios = 0

        # ===================================
        # ESTADO
        # ===================================

        if (
            faltas < 3 and
            promedio_tareas >= 60 and
            promedio_cuestionarios >= 60
        ):

            estado = "APROBANDO"

        elif (

            faltas == 2 or

            (
                promedio_tareas >= 51 and
                promedio_tareas < 70
            ) or

            (
                promedio_cuestionarios >= 51 and
                promedio_cuestionarios < 70
            )

        ):

            estado = "EN RIESGO"

        else:

            estado = "REPROBANDO"

        datos_participantes.append({

            'usuario': usuario,

            'asistencias': asistencias,

            'total_clases': total_clases,

            'porcentaje_asistencia': round(
                porcentaje_asistencia,
                1
            ),

            'promedio_tareas': round(
                promedio_tareas,
                1
            ),

            'promedio_cuestionarios': round(
                promedio_cuestionarios,
                1
            ),

            'estado': estado
        })

    # ===================================
    # RENDER HTML
    # ===================================

    html_string = render_to_string(

        'aprobaciones/pdf/reporte_curso_pdf.html',

        {
            'curso': curso,
            'datos_participantes': datos_participantes,
            'fecha': now()
        }
    )

    # ===================================
    # GENERAR PDF
    # ===================================

    html = HTML(
        string=html_string
    )

    pdf = html.write_pdf()

    response = HttpResponse(
        pdf,
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'filename="reporte_curso_{curso.id}.pdf"'

    return response

##_______________________________________________________________________________
@login_required
def sacramentos_admin(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    sacramentos = (

        ResultadoCurso.objects
        .values('sacramento')

        .annotate(
            total=Count('id')
        )

        .order_by('sacramento')
    )

    return render(

        request,

        'aprobaciones/admin/sacramentos.html',

        {
            'sacramentos': sacramentos
        }
    )

@login_required
def detalle_sacramento_admin(
    request,
    sacramento
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    aprobados = ResultadoCurso.objects.filter(
        sacramento=sacramento
    ).select_related(
        'participante__user',
        'curso'
    )

    # =========================
    # BUSCADOR
    # =========================

    buscar = request.GET.get(
        'buscar'
    )

    if buscar:

        aprobados = aprobados.filter(

            Q(
                participante__user__first_name__icontains=buscar
            ) |

            Q(
                participante__user__last_name__icontains=buscar
            ) |

            Q(
                participante__user__username__icontains=buscar
            )
        )

    # =========================
    # FILTRO GESTIÓN
    # =========================

    gestion = request.GET.get(
        'gestion'
    )

    if gestion:

        aprobados = aprobados.filter(
            gestion=gestion
        )

    gestiones = (

        ResultadoCurso.objects
        .filter(
            sacramento=sacramento
        )

        .values_list(
            'gestion',
            flat=True
        )

        .distinct()
    )

    return render(

        request,

        'aprobaciones/admin/detalle_sacramento.html',

        {

            'aprobados': aprobados,

            'sacramento': sacramento,

            'gestiones': gestiones
        }
    )

@login_required
def agregar_sacramento_manual(
    request
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    if request.method == 'POST':

        form = AprobadoManualForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(

                request,

                'Sacramento registrado correctamente'
            )

            return redirect(
                'sacramentos_admin'
            )

    else:

        form = AprobadoManualForm()

    return render(

        request,

        'aprobaciones/admin/agregar_manual.html',

        {
            'form': form
        }
    )



