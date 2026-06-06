from django.contrib.auth.decorators import login_required

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from django.contrib import messages

from usuarios.decorators import rol_requerido

from aprobaciones.models import ResultadoCurso

from .models import RegistroSacramental

from .forms import RegistroSacramentalForm, RegistroSacramentalAdminForm
from django.db.models import Q
from .models import Sacramento
from django.http import HttpResponse
from django.template.loader import render_to_string


@login_required
@rol_requerido('ADMIN')
def registrar_sacramento(request, id):

    resultado = get_object_or_404(
        ResultadoCurso,
        id=id
    )

    # ===================================
    # VALIDAR APROBADO
    # ===================================

    if resultado.estado_final != 'APROBADO':

        messages.error(
            request,
            'El participante no aprobó el curso'
        )

        return redirect('detalle_curso_finalizado', id=id)

    # ===================================
    # VALIDAR DUPLICADOS
    # ===================================

    existe = RegistroSacramental.objects.filter(

        participante=resultado.participante,

        sacramento=resultado.sacramento

    ).exists()

    if existe:

        messages.warning(
            request,
            'Este participante ya tiene registrado este sacramento'
        )

        return redirect('detalle_curso_finalizado', id=id)

    # ===================================
    # FORMULARIO
    # ===================================

    if request.method == 'POST':

        form = RegistroSacramentalForm(
            request.POST
        )

        if form.is_valid():

            registro = form.save(commit=False)

            registro.participante = (
                resultado.participante
            )

            registro.sacramento = (
                resultado.sacramento
            )

            registro.save()

            messages.success(
                request,
                'Sacramento registrado correctamente'
            )

            return redirect(
                'detalle_curso_finalizado', id=id
            )

    else:

        form = RegistroSacramentalForm()

    return render(

        request,

        'sacramentos/registrar_sacramento.html',

        {
            'form': form,
            'resultado': resultado
        }
    )

#_________________________________________________________________
@login_required
@rol_requerido('ADMIN')
def lista_registros_sacramentales(request):

    busqueda = request.GET.get(
        'busqueda'
    )

    sacramento_id = request.GET.get(
        'sacramento'
    )

    registros = RegistroSacramental.objects.select_related(
        'participante',
        'sacramento'
    ).order_by(
        '-fecha_registro'
    )

    # BUSCADOR
    if busqueda:

        registros = registros.filter(

            Q(
                participante__user__first_name__icontains=busqueda
            ) |

            Q(
                participante__user__last_name__icontains=busqueda
            ) |

            Q(
                nombre_manual__icontains=busqueda
            ) |

            Q(
                apellido_manual__icontains=busqueda
            )
        )

    # FILTRO SACRAMENTO
    if sacramento_id:

        registros = registros.filter(
            sacramento_id=sacramento_id
        )

    sacramentos = Sacramento.objects.all()

    context = {

        'registros': registros,

        'sacramentos': sacramentos

    }

    return render(

        request,

        'sacramentos/admin/lista.html',

        context
    )

@login_required
@rol_requerido('ADMIN')
def crear_registro_sacramental(request):

    if request.method == 'POST':

        form = RegistroSacramentalAdminForm(
            request.POST
        )

        if form.is_valid():

            registro = form.save()

            messages.success(

                request,

                'Registro sacramental creado correctamente'
            )

            return redirect(
                'lista_registros_sacramentales'
            )

    else:

        form = RegistroSacramentalAdminForm()

    return render(

        request,

        'sacramentos/admin/crear.html',

        {
            'form': form
        }
    )

@login_required
@rol_requerido('ADMIN')
def editar_registro_sacramental(
    request,
    id
):

    registro = get_object_or_404(
        RegistroSacramental,
        id=id
    )

    if request.method == 'POST':

        form = RegistroSacramentalForm(

            request.POST,

            instance=registro
        )

        if form.is_valid():

            form.save()

            messages.success(

                request,

                'Registro sacramental actualizado correctamente'
            )

            return redirect(
                'lista_registros_sacramentales'
            )

    else:

        form = RegistroSacramentalForm(
            instance=registro
        )

    return render(

        request,

        'sacramentos/admin/editar.html',

        {

            'form': form,

            'registro': registro
        }
    )

@login_required
@rol_requerido('ADMIN')
def detalle_registro_sacramental(
    request,
    id
):

    registro = get_object_or_404(
        RegistroSacramental,
        id=id
    )

    return render(

        request,

        'sacramentos/admin/detalle.html',

        {
            'registro': registro
        }
    )

@login_required
@rol_requerido('ADMIN')
def pdf_registro_sacramental(
    request,
    id
):
    from weasyprint import HTML

    registro = get_object_or_404(
        RegistroSacramental,
        id=id
    )

    html_string = render_to_string(

        'sacramentos/admin/pdf_registro.html',

        {
            'registro': registro
        }
    )

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
    ] = (
        'filename="registro_sacramental.pdf"'
    )

    return response

@login_required
@rol_requerido('ADMIN')
def libros_historicos(request):

    registros = RegistroSacramental.objects.filter(

        participante__isnull=True

    ).order_by(
        '-fecha_sacramento'
    )

    return render(

        request,

        'sacramentos/admin/libros_historicos.html',

        {
            'registros': registros
        }
    )

@login_required
@rol_requerido('ADMIN')
def certificado_sacramental_pdf(
    request,
    id
):
    from weasyprint import HTML
    registro = get_object_or_404(
        RegistroSacramental,
        id=id
    )

    nombre_completo = ''

    if registro.participante:

        nombre_completo = (

            f"{registro.participante.user.first_name} "
            f"{registro.participante.user.last_name}"
        )

    else:

        nombre_completo = (

            f"{registro.nombre_manual} "
            f"{registro.apellido_manual}"
        )

    html_string = render_to_string(

        'sacramentos/admin/certificado_pdf.html',

        {

            'registro': registro,

            'nombre_completo': nombre_completo

        }
    )

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
    ] = (
        'filename="certificado_sacramental.pdf"'
    )

    return response

@login_required
@rol_requerido('ADMIN')
def lista_sacramentos_admin(request):

    sacramentos = Sacramento.objects.all().order_by(
        'nombre'
    )

    return render(

        request,

        'sacramentos/admin/tipos/lista.html',

        {
            'sacramentos': sacramentos
        }
    )

@login_required
@rol_requerido('ADMIN')
def crear_sacramento_admin(request):

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre'
        )

        descripcion = request.POST.get(
            'descripcion'
        )

        Sacramento.objects.create(

            nombre=nombre,

            descripcion=descripcion
        )

        messages.success(

            request,

            'Sacramento creado correctamente'
        )

        return redirect(
            'lista_sacramentos_admin'
        )

    return render(

        request,

        'sacramentos/admin/tipos/crear.html'
    )

@login_required
@rol_requerido('ADMIN')
def editar_sacramento_admin(
    request,
    id
):

    sacramento = get_object_or_404(
        Sacramento,
        id=id
    )

    if request.method == 'POST':

        sacramento.nombre = request.POST.get(
            'nombre'
        )

        sacramento.descripcion = request.POST.get(
            'descripcion'
        )

        sacramento.save()

        messages.success(

            request,

            'Sacramento actualizado correctamente'
        )

        return redirect(
            'lista_sacramentos_admin'
        )

    return render(

        request,

        'sacramentos/admin/tipos/editar.html',

        {
            'sacramento': sacramento
        }
    )

@login_required
@rol_requerido('ADMIN')
def eliminar_sacramento_admin(
    request,
    id
):

    sacramento = get_object_or_404(
        Sacramento,
        id=id
    )

    sacramento.delete()

    messages.success(

        request,

        'Sacramento eliminado correctamente'
    )

    return redirect(
        'lista_sacramentos_admin'
    )

from cursos.models import Curso
from usuarios.models import Perfil
from aprobaciones.models import ResultadoCurso
@login_required
@rol_requerido('ADMIN')
def cursos_finalizados_admin(request):

    cursos = Curso.objects.filter(

        lista_enviada=True

    ).order_by(

        '-fecha_envio_lista'
    )

    data = []

    for curso in cursos:

        total_aprobados = ResultadoCurso.objects.filter(

            curso=curso,

            estado_final='APROBADO'

        ).count()

        total_reprobados = ResultadoCurso.objects.filter(

            curso=curso,

            estado_final='REPROBADO'

        ).count()

        total_registrados = RegistroSacramental.objects.filter(

            sacramento__nombre=curso.sacramento,

            participante__in=Perfil.objects.filter(

                id__in=ResultadoCurso.objects.filter(

                    curso=curso,

                    estado_final='APROBADO'

                ).values_list(

                    'participante_id',
                    flat=True
                )
            )

        ).count()

        data.append({

            'curso': curso,

            'aprobados': total_aprobados,

            'reprobados': total_reprobados,

            'registrados': total_registrados
        })

    return render(

        request,

        'sacramentos/admin/cursos/lista.html',

        {
            'data': data
        }
    )

@login_required
@rol_requerido('ADMIN')
def detalle_curso_finalizado(
    request,
    id
):

    curso = get_object_or_404(
        Curso,
        id=id
    )

    resultados = ResultadoCurso.objects.filter(

        curso=curso

    ).select_related(

        'participante',

        'sacramento'
    )

    # ===================================
    # VALIDAR SI YA TIENE REGISTRO
    # DEL MISMO SACRAMENTO
    # ===================================

    for r in resultados:

        r.ya_registrado = RegistroSacramental.objects.filter(

            participante=r.participante,

            sacramento=r.sacramento

        ).exists()

    return render(

        request,

        'sacramentos/admin/cursos/detalle.html',

        {

            'curso': curso,

            'resultados': resultados
        }
    )