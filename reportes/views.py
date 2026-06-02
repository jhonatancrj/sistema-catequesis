from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
import json

from .services import ReportesService
from cursos.models import Curso
from usuarios.models import Perfil
from usuarios.decorators import rol_requerido

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io


@login_required
@rol_requerido('ADMIN')
def reportes_dashboard(request):
    """Dashboard principal de reportes"""
    datos = ReportesService.obtener_datos_dashboard()
    
    context = {
        'datos': datos,
        'titulo': 'Dashboard de Reportes',
        'subtitulo': 'Resumen general del sistema'
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_cursos(request):
    """Reporte de todos los cursos"""
    datos = ReportesService.obtener_reportes_cursos()
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        datos = [d for d in datos if d['estado'] == estado_filtro]
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Cursos',
        'subtitulo': 'Análisis detallado de todos los cursos',
        'estados': ['ACTIVO', 'INACTIVO', 'FINALIZADO']
    }
    
    return render(request, 'reportes/cursos.html', context)


@login_required
@rol_requerido('ADMIN')
def reporte_curso_detallado(request, curso_id):
    """Reporte detallado de un curso específico"""
    datos = ReportesService.obtener_reporte_curso_detallado(curso_id)
    
    if not datos:
        messages.error(request, 'Curso no encontrado')
        return redirect('reportes_cursos')
    
    context = {
        'datos': datos,
        'titulo': f"Reporte: {datos['curso']['nombre']}",
        'subtitulo': 'Análisis detallado del curso'
    }
    
    return render(request, 'reportes/curso_detallado.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_participantes(request):
    """Reporte de participantes"""
    datos = ReportesService.obtener_reportes_participantes()
    
    # Filtros
    filtro_nombre = request.GET.get('nombre', '')
    if filtro_nombre:
        datos = [d for d in datos if filtro_nombre.lower() in d['nombre'].lower()]
    
    # Ordenamiento
    ordenar_por = request.GET.get('ordenar', 'nombre')
    if ordenar_por == 'asistencia':
        datos.sort(key=lambda x: x['asistencia']['porcentaje'], reverse=True)
    elif ordenar_por == 'aprobacion':
        datos.sort(key=lambda x: x['resultados']['aprobados'], reverse=True)
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Participantes',
        'subtitulo': 'Desempeño de todos los participantes'
    }
    
    return render(request, 'reportes/participantes.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_catequistas(request):
    """Reporte de catequistas"""
    datos = ReportesService.obtener_reportes_catequistas()
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Catequistas',
        'subtitulo': 'Desempeño y carga de trabajo de catequistas'
    }
    
    return render(request, 'reportes/catequistas.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_tareas(request):
    """Reporte de tareas"""
    datos = ReportesService.obtener_reportes_tareas()
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Tareas',
        'subtitulo': 'Análisis de entregas de tareas'
    }
    
    return render(request, 'reportes/tareas.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_cuestionarios(request):
    """Reporte de cuestionarios"""
    datos = ReportesService.obtener_reportes_cuestionarios()
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Cuestionarios',
        'subtitulo': 'Desempeño en evaluaciones'
    }
    
    return render(request, 'reportes/cuestionarios.html', context)


@login_required
@rol_requerido('ADMIN')
def reportes_aprobaciones(request):
    """Reporte de aprobaciones"""
    datos = ReportesService.obtener_reportes_aprobaciones()
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        datos = [d for d in datos if d['estado_final'] == estado_filtro]
    
    context = {
        'datos': datos,
        'titulo': 'Reporte de Aprobaciones',
        'subtitulo': 'Estado final de participantes por curso',
        'estados': ['APROBADO', 'REPROBADO']
    }
    
    return render(request, 'reportes/aprobaciones.html', context)


@login_required
@rol_requerido('ADMIN')
def datos_graficas_dashboard(request):
    """API para obtener datos de gráficas del dashboard"""
    datos = ReportesService.obtener_datos_dashboard()
    
    # Asistencia
    asistencia_labels = ['Presente', 'Ausente', 'Permiso']
    asistencia_data = [
        datos['asistencia']['presente'],
        datos['asistencia']['ausente'],
        datos['asistencia']['permiso']
    ]
    
    # Resultados finales
    resultados_labels = ['Aprobados', 'Reprobados']
    resultados_data = [
        datos['resultados']['aprobados'],
        datos['resultados']['reprobados']
    ]
    
    # Entregas de tareas
    tareas_labels = ['Entregadas', 'Pendientes']
    tareas_data = [
        datos['tareas']['entregadas'],
        datos['tareas']['pendientes']
    ]
    
    return JsonResponse({
        'asistencia': {
            'labels': asistencia_labels,
            'data': asistencia_data,
        },
        'resultados': {
            'labels': resultados_labels,
            'data': resultados_data,
        },
        'tareas': {
            'labels': tareas_labels,
            'data': tareas_data,
        },
        'cuestionarios': {
            'promedio': datos['cuestionarios']['promedio_puntaje'],
            'total': datos['cuestionarios']['total_intentos'],
        }
    })


@login_required
@rol_requerido('ADMIN')
def datos_graficas_cursos(request):
    """API para obtener datos de gráficas de cursos"""
    datos = ReportesService.obtener_reportes_cursos()
    
    labels = [d['nombre'] for d in datos]
    inscripciones = [d['inscripciones'] for d in datos]
    asistencia = [d['asistencia']['porcentaje'] for d in datos]
    aprobacion = [
        (d['resultados']['aprobados'] / d['resultados']['total'] * 100) 
        if d['resultados']['total'] > 0 else 0 
        for d in datos
    ]
    
    return JsonResponse({
        'labels': labels,
        'datasets': [
            {
                'label': 'Inscripciones',
                'data': inscripciones,
            },
            {
                'label': 'Asistencia %',
                'data': asistencia,
            },
            {
                'label': 'Aprobación %',
                'data': aprobacion,
            }
        ]
    })


# =============================================================================
# EXPORTACIÓN A PDF
# =============================================================================

def generar_pdf_dashboard(request):
    """Genera PDF del dashboard general"""
    datos = ReportesService.obtener_datos_dashboard()
    presentes = datos['asistencia']['presente']
    ausentes = datos['asistencia']['ausente']

    total = presentes + ausentes

    porcentaje = 0

    if total > 0:
        porcentaje = round((presentes / total) * 100, 2)

    datos['asistencia']['porcentaje'] = porcentaje
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Título
    story.append(Paragraph("📊 REPORTE GENERAL DEL SISTEMA", titulo_style))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Estadísticas Generales
    story.append(Paragraph("ESTADÍSTICAS GENERALES", heading_style))
    
    stats_data = [
        ['Métrica', 'Valor'],
        ['Total de Cursos', str(datos['total_cursos'])],
        ['Cursos Activos', str(datos['total_cursos_activos'])],
        ['Total de Participantes', str(datos['total_participantes'])],
        ['Total de Catequistas', str(datos['total_catequistas'])],
        ['Total de Inscripciones', str(datos['total_inscripciones'])],
        ['Total de Clases', str(datos['total_clases'])],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Asistencia
    story.append(Paragraph("ASISTENCIA", heading_style))
    
    asistencia_data = [
        ['Estado', 'Cantidad', 'Porcentaje'],
        ['Presente', str(datos['asistencia']['presente']), f"{datos['asistencia']['porcentaje']}%"],
        ['Ausente', str(datos['asistencia']['ausente']), ''],
        ['Permiso', str(datos['asistencia']['permiso']), ''],
        ['Total', str(datos['asistencia']['total']), ''],
    ]
    
    asistencia_table = Table(asistencia_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    asistencia_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
    ]))
    
    story.append(asistencia_table)
    story.append(PageBreak())
    
    # Tareas
    story.append(Paragraph("ENTREGAS DE TAREAS", heading_style))
    
    tareas_data = [
        ['Métrica', 'Valor'],
        ['Total de Tareas', str(datos['tareas']['total'])],
        ['Entregadas', str(datos['tareas']['entregadas'])],
        ['Pendientes', str(datos['tareas']['pendientes'])],
        ['% Entrega', f"{datos['tareas']['porcentaje_entrega']}%"],
    ]
    
    tareas_table = Table(tareas_data, colWidths=[3*inch, 2*inch])
    tareas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
    ]))
    
    story.append(tareas_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Resultados Finales
    story.append(Paragraph("RESULTADOS FINALES", heading_style))
    
    resultados_data = [
        ['Estado', 'Cantidad', 'Porcentaje'],
        ['Aprobados', str(datos['resultados']['aprobados']), f"{datos['resultados']['porcentaje_aprobacion']}%"],
        ['Reprobados', str(datos['resultados']['reprobados']), ''],
    ]
    
    resultados_table = Table(resultados_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    resultados_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
    ]))
    
    story.append(resultados_table)
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"<i>Reporte generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</i>",
        styles['Normal']
    ))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_general_{datetime.now().strftime("%d_%m_%Y_%H%M%S")}.pdf"'
    
    return response


@login_required
@rol_requerido('ADMIN')
def generar_pdf_cursos(request):
    """Genera PDF del reporte de cursos"""
    datos = ReportesService.obtener_reportes_cursos()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("📚 REPORTE DE CURSOS", titulo_style))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de cursos
    cursos_data = [
        ['Curso', 'Estado', 'Participantes', 'Asistencia %', 'Aprobación %']
    ]
    
    for curso in datos:
        aprobacion_pct = (curso['resultados']['aprobados'] / curso['resultados']['total'] * 100) if curso['resultados']['total'] > 0 else 0
        cursos_data.append([
            curso['nombre'],
            curso['estado'],
            str(curso['inscripciones']),
            f"{curso['asistencia']['porcentaje']}%",
            f"{round(aprobacion_pct, 2)}%",
        ])
    
    cursos_table = Table(cursos_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1.2*inch, 1.3*inch])
    cursos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
    ]))
    
    story.append(cursos_table)
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"<i>Reporte generado el {datetime.now().strftime('%d de %B de %Y')}</i>",
        styles['Normal']
    ))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_cursos_{datetime.now().strftime("%d_%m_%Y_%H%M%S")}.pdf"'
    
    return response


@login_required
@rol_requerido('ADMIN')
def generar_pdf_participantes(request):
    """Genera PDF del reporte de participantes"""
    datos = ReportesService.obtener_reportes_participantes()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("👥 REPORTE DE PARTICIPANTES", titulo_style))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de participantes
    participantes_data = [
        ['Nombre', 'Cursos', 'Asistencia %', 'Aprobados']
    ]
    
    for participante in datos:
        participantes_data.append([
            participante['nombre'][:30],
            str(participante['cursos_inscritos']),
            f"{participante['asistencia']['porcentaje']}%",
            str(participante['resultados']['aprobados']),
        ])
    
    participantes_table = Table(participantes_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch])
    participantes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
    ]))
    
    story.append(participantes_table)
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"<i>Total de participantes: {len(datos)}</i>",
        styles['Normal']
    ))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_participantes_{datetime.now().strftime("%d_%m_%Y_%H%M%S")}.pdf"'
    
    return response
