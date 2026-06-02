from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from cursos.models import Clase
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.utils import timezone
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .forms import CuestionarioForm
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from datetime import datetime

@login_required
def crear_cuestionario(request, clase_id):

    if request.user.perfil.rol != 'CATEQUISTA':
        return redirect('/')

    return render(request, 'cuestionario/crear_cuestionario.html', {
        'clase_id': clase_id
    })

def guardar_cuestionario(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        # Convertir fecha si existe
        fecha_limite = None
        if data.get('fecha_limite'):
            from datetime import datetime
            fecha_limite = datetime.fromisoformat(data.get('fecha_limite'))

        cuestionario = Cuestionario.objects.create(
            titulo=data['titulo'],
            descripcion=data['descripcion'],
            clase_id=data['clase_id'],
            catequista=request.user,
            tiempo_limite=data.get('tiempo'),
            es_unico=data.get('unico'),
            fecha_limite=fecha_limite
        )

        for p in data['preguntas']:
            pregunta = Pregunta.objects.create(
                cuestionario=cuestionario,
                enunciado=p['texto'],
                tipo=p['tipo'],
                puntaje=p['puntaje'],
                retroalimentacion=p.get('retroalimentacion', '')
                
            )

            for op in p.get('opciones', []):
                Opcion.objects.create(
                    pregunta=pregunta,
                    texto=op['texto'],
                    es_correcta=op['correcta']
                )

        return JsonResponse({'ok': True})
    

def ver_resultados(request, id):

    cuestionario = get_object_or_404(Cuestionario, id=id)

    intentos = Intento.objects.filter(cuestionario=cuestionario)

    mejores = {}

    for i in intentos:
        user = i.usuario
        if user not in mejores or i.puntaje > mejores[user].puntaje:
            mejores[user] = i

    return render(request, 'cuestionario/panel_resultados.html', {
        'cuestionario': cuestionario,
        'mejores': mejores.values(),
        'intentos': intentos
    })


@login_required
def resolver_cuestionario(request, id):

    if request.user.perfil.rol != 'PARTICIPANTE':
        return redirect('/')

    cuestionario = get_object_or_404(Cuestionario, id=id)
    
    # ⛔ VALIDAR FECHA LÍMITE
    fecha_pasada = cuestionario.fecha_limite and timezone.now() > cuestionario.fecha_limite
    
    if fecha_pasada:
        # Si pasó la fecha, mostrar página de expirado
        return render(request, 'cuestionario/expirado.html', {
            'cuestionario': cuestionario
        })
    
    preguntas = Pregunta.objects.filter(cuestionario=cuestionario)

    # 🔒 Verificar intento único
    intentos = Intento.objects.filter(usuario=request.user, cuestionario=cuestionario)

    if cuestionario.es_unico and intentos.exists():
        mejor = intentos.order_by('-puntaje').first()
        return render(request, 'participante/bloqueado.html', {
            'mejor': mejor,
            'intentos': intentos.count(),
            'cuestionario': cuestionario,
            'es_unico': True
        })

    if request.method == 'POST':

        total = 0
        maximo = 0
        retro = []

        intento = Intento.objects.create(
            usuario=request.user,
            cuestionario=cuestionario,
            puntaje=0
        )

        for pregunta in preguntas:

            maximo += pregunta.puntaje

            if pregunta.tipo == 'texto':
                texto = request.POST.get(f"p_{pregunta.id}")

                Respuesta.objects.create(
                    intento=intento,
                    pregunta=pregunta,
                    texto=texto
                )

            elif pregunta.tipo == 'multiple':
                opcion_id = request.POST.get(f"p_{pregunta.id}")

                if opcion_id:
                    opcion = Opcion.objects.get(id=opcion_id)

                    Respuesta.objects.create(
                        intento=intento,
                        pregunta=pregunta,
                        opcion=opcion
                    )

                    if opcion.es_correcta:
                        total += pregunta.puntaje

            elif pregunta.tipo == 'checkbox':
                opciones_ids = request.POST.getlist(f"p_{pregunta.id}")

                correctas = Opcion.objects.filter(pregunta=pregunta, es_correcta=True)
                seleccionadas = Opcion.objects.filter(id__in=opciones_ids)

                for op in seleccionadas:
                    Respuesta.objects.create(
                        intento=intento,
                        pregunta=pregunta,
                        opcion=op
                    )

                if set(correctas) == set(seleccionadas):
                    total += pregunta.puntaje

            # 🧠 RETROALIMENTACIÓN (AQUÍ CORRECTO)
            if pregunta.retroalimentacion:
                retro.append({
                    'pregunta': pregunta.enunciado,
                    'mensaje': pregunta.retroalimentacion
                })

        respuestas = Respuesta.objects.filter(intento=intento).select_related('pregunta', 'opcion')

        preguntas_con_respuestas = {}

        for r in respuestas:
            pid = r.pregunta.id

            if pid not in preguntas_con_respuestas:
                preguntas_con_respuestas[pid] = {
                    'pregunta': r.pregunta,
                    'respuestas': []
                }

            preguntas_con_respuestas[pid]['respuestas'].append(r)
            
        intento.puntaje = total
        intento.save()
        
        # 🏆 mejor intento
        mejores = Intento.objects.filter(usuario=request.user, cuestionario=cuestionario).order_by('-puntaje')
        mejor = mejores.first()

        return render(request, 'participante/resultado_participante.html', {
            'puntaje': total,
            'maximo': maximo,
            'retro': retro,
            'mejor': mejor,
            'intentos': mejores.count(),
            'respuestas': respuestas,
            'cuestionario': cuestionario
        })

    return render(request, 'participante/resolver.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas
    })

def detalle_intento(request, id):

    intento = get_object_or_404(Intento, id=id)
    respuestas = Respuesta.objects.filter(intento=intento)

    return render(request, 'participante/detalle.html', {
        'intento': intento,
        'respuestas': respuestas
    })

@login_required
def editar_cuestionario(request, id):

    if request.user.perfil.rol != 'CATEQUISTA':
        return redirect('/')

    cuestionario = get_object_or_404(Cuestionario, id=id)
    preguntas = Pregunta.objects.filter(cuestionario=cuestionario)

    data = []

    for p in preguntas:
        opciones = Opcion.objects.filter(pregunta=p)

        data.append({
            'id': p.id,
            'texto': p.enunciado,
            'tipo': p.tipo,
            'puntaje': p.puntaje,
            'opciones': [
                {
                    'id': op.id,
                    'texto': op.texto,
                    'correcta': op.es_correcta
                } for op in opciones
            ]
        })

    return render(request, 'cuestionario/editar_cuestionario.html', {
        'cuestionario': cuestionario,
        'preguntas_json': json.dumps(data)
    })

@login_required
def actualizar_cuestionario(request, id):

    if request.method == 'POST':

        data = json.loads(request.body)

        cuestionario = Cuestionario.objects.get(id=id)

        cuestionario.titulo = data['titulo']
        cuestionario.descripcion = data['descripcion']
        cuestionario.tiempo_limite = data['tiempo']
        cuestionario.es_unico = data['unico']
        cuestionario.save()

        # ❗ BORRAR TODO PARA RECREAR
        Pregunta.objects.filter(cuestionario=cuestionario).delete()

        for p in data['preguntas']:
            pregunta = Pregunta.objects.create(
                cuestionario=cuestionario,
                enunciado=p['texto'],
                tipo=p['tipo'],
                puntaje=p['puntaje']
            )

            for op in p.get('opciones', []):
                Opcion.objects.create(
                    pregunta=pregunta,
                    texto=op['texto'],
                    es_correcta=op['correcta']
                )

        return JsonResponse({'ok': True})
    

##cosas extras

def estadisticas_pregunta(request, id):

    cuestionario = get_object_or_404(Cuestionario, id=id)
    preguntas = Pregunta.objects.filter(cuestionario=cuestionario)

    data = []

    for p in preguntas:
        opciones = Opcion.objects.filter(pregunta=p)

        stats = []
        for op in opciones:
            count = Respuesta.objects.filter(opcion=op).count()
            stats.append({
                'texto': op.texto,
                'cantidad': count
            })

        data.append({
            'pregunta': p.enunciado,
            'stats': stats
        })

    return render(request, 'cuestionario/estadisticas.html', {
        'data': data
    })

def ranking(request, id):

    cuestionario = get_object_or_404(Cuestionario, id=id)

    ranking = Intento.objects.filter(
        cuestionario=cuestionario
    ).order_by('-puntaje')

    return render(request, 'cuestionario/ranking.html', {
        'ranking': ranking
    })



def exportar_pdf(request, id):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resultados.pdf"'

    p = canvas.Canvas(response)

    intentos = Intento.objects.filter(cuestionario_id=id)

    y = 800

    for i in intentos:
        p.drawString(100, y, f"{i.usuario.username} - {i.puntaje}")
        y -= 20

    p.save()
    return response

from django.db.models import Avg
from datetime import datetime

def reporte_general(request):

    total_cuestionarios = Cuestionario.objects.count()
    total_intentos = Intento.objects.count()
    promedio = Intento.objects.aggregate(avg=Avg('puntaje'))

    # 📈 evolución (últimos intentos)
    intentos = Intento.objects.order_by('fecha')[:20]

    fechas = [i.fecha.strftime("%d/%m") for i in intentos]
    puntajes = [i.puntaje for i in intentos]

    # 📊 promedio por cuestionario
    cuestionarios = Cuestionario.objects.all()

    nombres = []
    promedios = []

    for c in cuestionarios:
        prom = Intento.objects.filter(cuestionario=c).aggregate(avg=Avg('puntaje'))['avg'] or 0

        nombres.append(c.titulo)
        promedios.append(prom)

    # 🏆 ranking global
    ranking = Intento.objects.order_by('-puntaje')[:10]

    return render(request, 'catequista/reporte.html', {
        'total_cuestionarios': total_cuestionarios,
        'total_intentos': total_intentos,
        'promedio': promedio,

        'fechas': fechas,
        'puntajes': puntajes,

        'nombres_cuestionarios': nombres,
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

from .models import *

def exportar_reporte_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_institucional.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    elementos = []

    # =========================
    # 🏫 HEADER INSTITUCIONAL
    # =========================

    try:
        logo = Image("static/img/logo.png", width=70, height=70)
        elementos.append(logo)
    except:
        pass

    elementos.append(Paragraph("<b>SISTEMA EDUCATIVO</b>", styles['Title']))
    elementos.append(Paragraph("Reporte General Académico", styles['Heading2']))

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    elementos.append(Paragraph(f"Fecha: {fecha_actual}", styles['Normal']))

    elementos.append(Spacer(1, 20))

    # =========================
    # 📊 RESUMEN
    # =========================

    total_cuestionarios = Cuestionario.objects.count()
    total_intentos = Intento.objects.count()
    promedio = Intento.objects.aggregate(avg=Avg('puntaje'))['avg'] or 0

    resumen_data = [
        ["Indicador", "Valor"],
        ["Total Cuestionarios", total_cuestionarios],
        ["Total Intentos", total_intentos],
        ["Promedio General", round(promedio, 2)],
    ]

    tabla_resumen = Table(resumen_data)
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 20))

    # =========================
    # 📈 GRAFICA 1: EVOLUCIÓN
    # =========================

    intentos = Intento.objects.order_by('fecha')[:20]

    fechas = [i.fecha.strftime("%d/%m") for i in intentos]
    puntajes = [i.puntaje for i in intentos]

    buffer = BytesIO()
    plt.figure()
    plt.plot(fechas, puntajes)
    plt.title("Evolución de Puntajes")
    plt.xlabel("Fecha")
    plt.ylabel("Puntaje")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    elementos.append(Paragraph("<b>Evolución de Puntajes</b>", styles['Heading2']))
    elementos.append(Image(buffer, width=400, height=200))
    elementos.append(Spacer(1, 20))

    # =========================
    # 📊 GRAFICA 2: PROMEDIO POR CUESTIONARIO
    # =========================

    cuestionarios = Cuestionario.objects.all()

    nombres = []
    promedios = []

    for c in cuestionarios:
        prom = Intento.objects.filter(cuestionario=c).aggregate(avg=Avg('puntaje'))['avg'] or 0
        nombres.append(c.titulo)
        promedios.append(prom)

    buffer2 = BytesIO()
    plt.figure()
    plt.bar(nombres, promedios)
    plt.title("Promedio por Cuestionario")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(buffer2, format='png')
    plt.close()

    buffer2.seek(0)
    elementos.append(Paragraph("<b>Promedio por Cuestionario</b>", styles['Heading2']))
    elementos.append(Image(buffer2, width=400, height=200))
    elementos.append(Spacer(1, 20))

    # =========================
    # 🏆 RANKING
    # =========================

    elementos.append(Paragraph("<b>Ranking Global</b>", styles['Heading2']))
    elementos.append(Spacer(1, 10))

    ranking = Intento.objects.order_by('-puntaje')[:15]

    data = [["#", "Usuario", "Cuestionario", "Puntaje"]]

    for i, r in enumerate(ranking, start=1):
        data.append([
            i,
            r.usuario.username,
            r.cuestionario.titulo,
            r.puntaje
        ])

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elementos.append(tabla)

    elementos.append(Spacer(1, 30))

    # =========================
    # ✍️ PIE
    # =========================

    elementos.append(Paragraph("Documento generado automáticamente por el sistema académico", styles['Italic']))

    doc.build(elementos)

    return response


##________________________________________________________________________________________________

@login_required
def lista_cuestionarios(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    cuestionarios = Cuestionario.objects.select_related(
        'clase',
        'clase__curso',
        'catequista'
    ).order_by('-fecha_creacion')

    context = {
        'cuestionarios': cuestionarios
    }

    return render(
        request,
        'cuestionario/lista.html',
        context
    )

@login_required
def crear_cuestionario_admin(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    clases = Clase.objects.select_related(
        'curso'
    )

    return render(
        request,
        'cuestionario/admin/crear.html',
        {
            'clases': clases
        }
    )

@login_required
def guardar_cuestionario_admin(request):

    if request.user.perfil.rol != 'ADMIN':
        return JsonResponse({
            'ok': False
        })

    if request.method == 'POST':

        data = json.loads(request.body)

        # Convertir fecha si existe
        fecha_limite = None
        if data.get('fecha_limite'):
            from datetime import datetime
            fecha_limite = datetime.fromisoformat(data.get('fecha_limite'))

        cuestionario = Cuestionario.objects.create(

            titulo=data['titulo'],

            descripcion=data['descripcion'],

            clase_id=data['clase_id'],

            catequista=request.user,

            tiempo_limite=data.get('tiempo'),

            es_unico=data.get('unico'),

            fecha_limite=fecha_limite

        )

        for p in data['preguntas']:

            pregunta = Pregunta.objects.create(

                cuestionario=cuestionario,

                enunciado=p['texto'],

                tipo=p['tipo'],

                puntaje=p['puntaje'],

                retroalimentacion=p.get(
                    'retroalimentacion',
                    ''
                )

            )

            for op in p.get('opciones', []):

                Opcion.objects.create(

                    pregunta=pregunta,

                    texto=op['texto'],

                    es_correcta=op['correcta']

                )

        return JsonResponse({
            'ok': True
        })
    

@login_required
def editar_cuestionario_admin(
    request,
    cuestionario_id
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    cuestionario = get_object_or_404(
        Cuestionario,
        id=cuestionario_id
    )

    preguntas = Pregunta.objects.filter(
        cuestionario=cuestionario
    ).prefetch_related('opcion_set')

    clases = Clase.objects.select_related(
        'curso'
    )

    context = {

        'cuestionario': cuestionario,
        'preguntas': preguntas,
        'clases': clases

    }

    return render(
        request,
        'cuestionario/admin/editar.html',
        context
    )

@login_required
def actualizar_cuestionario_admin(
    request,
    cuestionario_id
):

    if request.user.perfil.rol != 'ADMIN':
        return JsonResponse({
            'ok': False
        })

    cuestionario = get_object_or_404(
        Cuestionario,
        id=cuestionario_id
    )

    if request.method == 'POST':

        data = json.loads(request.body)

        cuestionario.titulo = data['titulo']

        cuestionario.descripcion = data['descripcion']

        cuestionario.clase_id = data['clase_id']

        cuestionario.tiempo_limite = data.get(
            'tiempo'
        )

        cuestionario.es_unico = data.get(
            'unico'
        )

        cuestionario.fecha_limite = data.get(
            'fecha_limite'
        )

        cuestionario.save()

        # ELIMINAR ANTERIORES
        Pregunta.objects.filter(
            cuestionario=cuestionario
        ).delete()

        # CREAR NUEVAS
        for p in data['preguntas']:

            pregunta = Pregunta.objects.create(

                cuestionario=cuestionario,

                enunciado=p['texto'],

                tipo=p['tipo'],

                puntaje=p['puntaje'],

                retroalimentacion=p.get(
                    'retroalimentacion',
                    ''
                )

            )

            for op in p.get('opciones', []):

                Opcion.objects.create(

                    pregunta=pregunta,

                    texto=op['texto'],

                    es_correcta=op['correcta']

                )

        return JsonResponse({
            'ok': True
        })
    
@login_required
def resultados_cuestionario_admin(
    request,
    cuestionario_id
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    cuestionario = get_object_or_404(
        Cuestionario,
        id=cuestionario_id
    )

    intentos = Intento.objects.filter(
        cuestionario=cuestionario
    ).select_related(
        'usuario'
    ).order_by('-puntaje')

    promedio = intentos.aggregate(
        Avg('puntaje')
    )['puntaje__avg']

    maxima = intentos.aggregate(
        Max('puntaje')
    )['puntaje__max']

    minima = intentos.aggregate(
        Min('puntaje')
    )['puntaje__min']

    total = intentos.count()

    context = {

        'cuestionario': cuestionario,

        'intentos': intentos,

        'promedio': promedio,
        'maxima': maxima,
        'minima': minima,
        'total': total

    }

    return render(
        request,
        'cuestionario/admin/resultados.html',
        context
    )

@login_required
def detalle_intento_admin(
    request,
    intento_id
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    intento = get_object_or_404(
        Intento,
        id=intento_id
    )

    respuestas = Respuesta.objects.filter(
        intento=intento
    ).select_related(
        'pregunta',
        'opcion'
    )

    context = {

        'intento': intento,
        'respuestas': respuestas

    }

    return render(
        request,
        'cuestionario/admin/detalle_intento.html',
        context
    )

@login_required
def estadisticas_cuestionario_admin(
    request,
    cuestionario_id
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    cuestionario = get_object_or_404(
        Cuestionario,
        id=cuestionario_id
    )

    preguntas = Pregunta.objects.filter(
        cuestionario=cuestionario
    )

    estadisticas = []

    for pregunta in preguntas:

        total_respuestas = Respuesta.objects.filter(
            pregunta=pregunta
        ).count()

        correctas = Respuesta.objects.filter(
            pregunta=pregunta,
            opcion__es_correcta=True
        ).count()

        incorrectas = total_respuestas - correctas

        porcentaje = 0

        if total_respuestas > 0:

            porcentaje = (
                correctas / total_respuestas
            ) * 100

        estadisticas.append({

            'pregunta': pregunta,

            'total': total_respuestas,

            'correctas': correctas,

            'incorrectas': incorrectas,

            'porcentaje': round(
                porcentaje,
                2
            )

        })

    labels = []

    correctas_data = []
    incorrectas_data = []

    for e in estadisticas:

        labels.append(
            e['pregunta'].enunciado[:20]
        )

        correctas_data.append(
            e['correctas']
        )

        incorrectas_data.append(
            e['incorrectas']
        )
    context = {

        'cuestionario': cuestionario,
        'estadisticas': estadisticas,
        'labels': labels,
        'correctas_data': correctas_data,
        'incorrectas_data': incorrectas_data

    }

    return render(
        request,
        'cuestionario/admin/estadisticas.html',
        context
    )

@login_required
def exportar_resultados_pdf(
    request,
    cuestionario_id
):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('/')

    cuestionario = get_object_or_404(
        Cuestionario,
        id=cuestionario_id
    )

    intentos = Intento.objects.filter(
        cuestionario=cuestionario
    ).select_related(
        'usuario'
    ).order_by('-puntaje')

    promedio = intentos.aggregate(
        Avg('puntaje')
    )['puntaje__avg']

    html_string = render_to_string(

        'cuestionario/admin/pdf_resultados.html',

        {

            'cuestionario': cuestionario,

            'intentos': intentos,

            'promedio': promedio,

            'fecha': datetime.now()

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
        'filename="reporte_cuestionario.pdf"'
    )

    return response