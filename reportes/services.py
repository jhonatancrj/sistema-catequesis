from django.db.models import Count, Avg, Q, Max, Min, F
from datetime import datetime, timedelta
from cursos.models import Curso, Inscripcion, Clase, Asistencia
from usuarios.models import Perfil
from tareas.models import Tarea, EntregaTarea
from cuestionario.models import Cuestionario, Intento
from aprobaciones.models import ResultadoCurso


class ReportesService:
    """Servicio para generar datos de reportes del sistema"""

    @staticmethod
    def obtener_estadisticas_generales():
        """Obtiene estadísticas generales del sistema"""
        return {
            'total_cursos': Curso.objects.count(),
            'total_cursos_activos': Curso.objects.filter(estado='ACTIVO').count(),
            'total_participantes': Perfil.objects.filter(rol='PARTICIPANTE').count(),
            'total_catequistas': Perfil.objects.filter(rol='CATEQUISTA').count(),
            'total_inscripciones': Inscripcion.objects.count(),
            'total_clases': Clase.objects.count(),
            'total_tareas': Tarea.objects.count(),
            'total_cuestionarios': Cuestionario.objects.count(),
            'total_aprobaciones': ResultadoCurso.objects.filter(estado_final='APROBADO').count(),
            'total_reprobaciones': ResultadoCurso.objects.filter(estado_final='REPROBADO').count(),
        }

    @staticmethod
    def obtener_datos_dashboard():
        """Obtiene datos completos para el dashboard principal"""
        stats = ReportesService.obtener_estadisticas_generales()
        
        # Asistencia promedio
        asistencias = Asistencia.objects.all()
        total_asistencias = asistencias.count()
        presente = asistencias.filter(estado='PRESENTE').count()
        ausente = asistencias.filter(estado='AUSENTE').count()
        permiso = asistencias.filter(estado='PERMISO').count()
        
        # Tareas
        total_tareas = Tarea.objects.count()
        tareas_entregadas = EntregaTarea.objects.exclude(fecha_entrega__isnull=True).count()
        tareas_pendientes = total_tareas - tareas_entregadas
        
        # Cuestionarios
        intentos_cuestionarios = Intento.objects.aggregate(
            promedio=Avg('puntaje'),
            total=Count('id')
        )
        
        return {
            **stats,
            'asistencia': {
                'presente': presente,
                'ausente': ausente,
                'permiso': permiso,
                'total': total_asistencias,
                'porcentaje_asistencia': round((presente / total_asistencias * 100), 2) if total_asistencias > 0 else 0,
            },
            'tareas': {
                'total': total_tareas,
                'entregadas': tareas_entregadas,
                'pendientes': tareas_pendientes,
                'porcentaje_entrega': round((tareas_entregadas / total_tareas * 100), 2) if total_tareas > 0 else 0,
            },
            'cuestionarios': {
                'promedio_puntaje': round(intentos_cuestionarios['promedio'] or 0, 2),
                'total_intentos': intentos_cuestionarios['total'],
            },
            'resultados': {
                'aprobados': stats['total_aprobaciones'],
                'reprobados': stats['total_reprobaciones'],
                'porcentaje_aprobacion': round(
                    (stats['total_aprobaciones'] / (stats['total_aprobaciones'] + stats['total_reprobaciones']) * 100), 2
                ) if (stats['total_aprobaciones'] + stats['total_reprobaciones']) > 0 else 0,
            }
        }

    @staticmethod
    def obtener_reportes_cursos():
        """Obtiene datos de todos los cursos"""
        cursos = Curso.objects.all()
        reportes = []
        
        for curso in cursos:
            inscripciones = Inscripcion.objects.filter(curso=curso)
            clases = Clase.objects.filter(curso=curso)
            
            # Asistencia del curso
            asistencias = Asistencia.objects.filter(clase__curso=curso)
            presente = asistencias.filter(estado='PRESENTE').count()
            total_asistencias = asistencias.count()
            
            # Tareas del curso
            tareas = Tarea.objects.filter(clase__curso=curso)
            entregas = EntregaTarea.objects.filter(tarea__in=tareas)
            
            # Cuestionarios del curso
            cuestionarios = Cuestionario.objects.filter(clase__curso=curso)
            intentos = Intento.objects.filter(cuestionario__in=cuestionarios)
            promedio_cuestionarios = intentos.aggregate(Avg('puntaje'))['puntaje__avg'] or 0
            
            # Resultados finales
            resultados = ResultadoCurso.objects.filter(curso=curso)
            aprobados = resultados.filter(estado_final='APROBADO').count()
            reprobados = resultados.filter(estado_final='REPROBADO').count()
            
            reportes.append({
                'id': curso.id,
                'nombre': curso.nombre,
                'estado': curso.estado,
                'fecha_inicio': curso.fecha_inicio,
                'fecha_fin': curso.fecha_fin,
                'inscripciones': inscripciones.count(),
                'clases': clases.count(),
                'catequistas': curso.catequistas.count(),
                'asistencia': {
                    'presente': presente,
                    'total': total_asistencias,
                    'porcentaje': round((presente / total_asistencias * 100), 2) if total_asistencias > 0 else 0,
                },
                'tareas': {
                    'total': tareas.count(),
                    'entregadas': entregas.count(),
                    'porcentaje': round((entregas.count() / tareas.count() * 100), 2) if tareas.count() > 0 else 0,
                },
                'cuestionarios': {
                    'total': cuestionarios.count(),
                    'promedio': round(promedio_cuestionarios, 2),
                },
                'resultados': {
                    'aprobados': aprobados,
                    'reprobados': reprobados,
                    'total': resultados.count(),
                }
            })
        
        return reportes

    @staticmethod
    def obtener_reporte_curso_detallado(curso_id):
        """Obtiene reporte detallado de un curso específico"""
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return None
        
        clases = Clase.objects.filter(curso=curso).order_by('fecha')
        participantes = Inscripcion.objects.filter(curso=curso).select_related('participante')
        
        datos_participantes = []
        for inscripcion in participantes:
            participante = inscripcion.participante
            
            # Asistencia
            asistencias = Asistencia.objects.filter(
                clase__curso=curso,
                participante=participante
            )
            presente = asistencias.filter(estado='PRESENTE').count()
            total_clases = clases.count()
            
            # Tareas
            entregas = EntregaTarea.objects.filter(
                estudiante=participante.user,
                tarea__clase__curso=curso
            )
            tareas_total = Tarea.objects.filter(clase__curso=curso).count()
            
            # Cuestionarios
            intentos = Intento.objects.filter(
                usuario=participante.user,
                cuestionario__clase__curso=curso
            )
            promedio_cuestionarios = intentos.aggregate(Avg('puntaje'))['puntaje__avg'] or 0
            
            # Resultado final
            resultado = ResultadoCurso.objects.filter(
                participante=participante,
                curso=curso
            ).first()
            
            datos_participantes.append({
                'id': participante.id,
                'nombre': f"{participante.user.first_name} {participante.user.last_name}",
                'email': participante.user.email,
                'asistencia': {
                    'presente': presente,
                    'total': total_clases,
                    'porcentaje': round((presente / total_clases * 100), 2) if total_clases > 0 else 0,
                },
                'tareas': {
                    'entregadas': entregas.count(),
                    'total': tareas_total,
                    'promedio': round((entregas.count() / tareas_total * 100), 2) if tareas_total > 0 else 0,
                },
                'cuestionarios': {
                    'promedio': round(promedio_cuestionarios, 2),
                    'intentos': intentos.count(),
                },
                'estado_final': resultado.estado_final if resultado else 'No definido',
                'promedio_general': resultado.promedio_tareas if resultado else 0,
            })
        
        return {
            'curso': {
                'id': curso.id,
                'nombre': curso.nombre,
                'estado': curso.estado,
                'fecha_inicio': curso.fecha_inicio,
                'fecha_fin': curso.fecha_fin,
                'descripcion': curso.descripcion,
            },
            'catequistas': list(curso.catequistas.values('id', 'user__first_name', 'user__last_name', 'user__email')),
            'clases': [{'id': c.id, 'titulo': c.titulo, 'fecha': c.fecha} for c in clases],
            'participantes': datos_participantes,
            'estadisticas': {
                'total_participantes': len(datos_participantes),
                'asistencia_promedio': round(
                    sum([p['asistencia']['porcentaje'] for p in datos_participantes]) / len(datos_participantes), 2
                ) if datos_participantes else 0,
                'entrega_tareas_promedio': round(
                    sum([p['tareas']['promedio'] for p in datos_participantes]) / len(datos_participantes), 2
                ) if datos_participantes else 0,
            }
        }

    @staticmethod
    def obtener_reportes_participantes():
        """Obtiene datos de desempeño de todos los participantes"""
        participantes = Perfil.objects.filter(rol='PARTICIPANTE')
        reportes = []
        
        for participante in participantes:
            inscripciones = Inscripcion.objects.filter(participante=participante, estado='INSCRITO')
            
            # Cursos inscritos
            cursos_ids = inscripciones.values_list('curso_id', flat=True)
            
            # Asistencia total
            asistencias = Asistencia.objects.filter(
                participante=participante,
                clase__curso_id__in=cursos_ids
            )
            presente = asistencias.filter(estado='PRESENTE').count()
            total_asistencias = asistencias.count()
            
            # Entregas de tareas
            entregas = EntregaTarea.objects.filter(estudiante=participante.user)
            
            # Cuestionarios
            intentos = Intento.objects.filter(usuario=participante.user)
            promedio_cuestionarios = intentos.aggregate(Avg('puntaje'))['puntaje__avg'] or 0
            
            # Resultados
            resultados = ResultadoCurso.objects.filter(participante=participante)
            aprobados = resultados.filter(estado_final='APROBADO').count()
            reprobados = resultados.filter(estado_final='REPROBADO').count()
            
            reportes.append({
                'id': participante.id,
                'nombre': f"{participante.user.first_name} {participante.user.last_name}",
                'email': participante.user.email,
                'cursos_inscritos': inscripciones.count(),
                'asistencia': {
                    'presente': presente,
                    'total': total_asistencias,
                    'porcentaje': round((presente / total_asistencias * 100), 2) if total_asistencias > 0 else 0,
                },
                'tareas': {
                    'entregadas': entregas.count(),
                },
                'cuestionarios': {
                    'promedio': round(promedio_cuestionarios, 2),
                    'total_intentos': intentos.count(),
                },
                'resultados': {
                    'aprobados': aprobados,
                    'reprobados': reprobados,
                }
            })
        
        return reportes

    @staticmethod
    def obtener_reportes_catequistas():
        """Obtiene datos de desempeño de catequistas"""
        catequistas = Perfil.objects.filter(rol='CATEQUISTA')
        reportes = []
        
        for catequista in catequistas:
            cursos = catequista.cursos.all()
            
            # Clases dictadas
            clases = Clase.objects.filter(curso__in=cursos)
            
            # Tareas creadas
            tareas = Tarea.objects.filter(catequista=catequista.user)
            entregas = EntregaTarea.objects.filter(tarea__in=tareas)
            
            # Cuestionarios creados
            cuestionarios = Cuestionario.objects.filter(catequista=catequista.user)
            intentos = Intento.objects.filter(cuestionario__in=cuestionarios)
            promedio_estudiantes = intentos.aggregate(Avg('puntaje'))['puntaje__avg'] or 0
            
            # Total de participantes
            participantes = set()
            for curso in cursos:
                participantes.update(
                    Inscripcion.objects.filter(curso=curso).values_list('participante_id', flat=True)
                )
            
            reportes.append({
                'id': catequista.id,
                'nombre': f"{catequista.user.first_name} {catequista.user.last_name}",
                'email': catequista.user.email,
                'especialidad': catequista.catequista.especialidad if hasattr(catequista, 'catequista') else 'N/A',
                'cursos_asignados': cursos.count(),
                'clases_dictadas': clases.count(),
                'participantes_totales': len(participantes),
                'tareas': {
                    'creadas': tareas.count(),
                    'entregadas': entregas.count(),
                },
                'cuestionarios': {
                    'creados': cuestionarios.count(),
                    'intentos': intentos.count(),
                    'promedio_estudiantes': round(promedio_estudiantes, 2),
                }
            })
        
        return reportes

    @staticmethod
    def obtener_reportes_tareas():
        """Obtiene datos de tareas"""
        tareas = Tarea.objects.all().select_related('clase', 'catequista')
        reportes = []
        
        for tarea in tareas:
            entregas = EntregaTarea.objects.filter(tarea=tarea)
            calificadas = entregas.exclude(calificacion__isnull=True)
            
            reportes.append({
                'id': tarea.id,
                'titulo': tarea.titulo,
                'curso': tarea.clase.curso.nombre,
                'catequista': f"{tarea.catequista.first_name} {tarea.catequista.last_name}",
                'fecha_entrega': tarea.fecha_entrega,
                'permitir_tardia': tarea.permitir_tardia,
                'entregas_totales': entregas.count(),
                'entregas_a_tiempo': entregas.filter(fecha_entrega__lte=tarea.fecha_entrega).count(),
                'entregas_tardia': entregas.filter(fecha_entrega__gt=tarea.fecha_entrega).count(),
                'calificadas': calificadas.count(),
                'promedio_calificacion': round(
                    calificadas.aggregate(Avg('calificacion'))['calificacion__avg'] or 0, 2
                ),
            })
        
        return reportes

    @staticmethod
    def obtener_reportes_cuestionarios():
        """Obtiene datos de cuestionarios"""
        cuestionarios = Cuestionario.objects.all().select_related('clase', 'catequista')
        reportes = []
        
        for cuestionario in cuestionarios:
            intentos = Intento.objects.filter(cuestionario=cuestionario)
            
            reportes.append({
                'id': cuestionario.id,
                'titulo': cuestionario.titulo,
                'curso': cuestionario.clase.curso.nombre,
                'catequista': f"{cuestionario.catequista.first_name} {cuestionario.catequista.last_name}",
                'fecha_limite': cuestionario.fecha_limite,
                'total_intentos': intentos.count(),
                'promedio_puntaje': round(intentos.aggregate(Avg('puntaje'))['puntaje__avg'] or 0, 2),
                'puntaje_maximo': intentos.aggregate(Max('puntaje'))['puntaje__max'] or 0,
                'puntaje_minimo': intentos.aggregate(Min('puntaje'))['puntaje__min'] or 0,
            })
        
        return reportes

    @staticmethod
    def obtener_reportes_aprobaciones():
        """Obtiene datos de aprobaciones"""
        resultados = ResultadoCurso.objects.all().select_related('participante', 'curso', 'sacramento')
        reportes = []
        
        for resultado in resultados:
            reportes.append({
                'id': resultado.id,
                'participante': f"{resultado.participante.user.first_name} {resultado.participante.user.last_name}",
                'curso': resultado.curso.nombre,
                'sacramento': resultado.sacramento.nombre if resultado.sacramento else 'N/A',
                'gestion': resultado.gestion,
                'promedio_tareas': round(resultado.promedio_tareas, 2),
                'promedio_cuestionarios': round(resultado.promedio_cuestionarios, 2),
                'faltas': resultado.faltas,
                'estado_final': resultado.estado_final,
                'fecha_resultado': resultado.fecha_resultado,
            })
        
        return reportes

    @staticmethod
    def obtener_datos_graficas():
        """Obtiene datos para las gráficas"""
        from django.db.models import Max, Min
        
        # Asistencia por estado
        asistencias_por_estado = Asistencia.objects.values('estado').annotate(count=Count('id'))
        
        # Cursos por estado
        cursos_por_estado = Curso.objects.values('estado').annotate(count=Count('id'))
        
        # Resultados finales
        resultados = ResultadoCurso.objects.values('estado_final').annotate(count=Count('id'))
        
        # Entregas de tareas (a tiempo vs tardia)
        entregas_a_tiempo = EntregaTarea.objects.filter(
            fecha_entrega__lte=F('tarea__fecha_entrega')
        ).count()
        entregas_tardia = EntregaTarea.objects.filter(
            fecha_entrega__gt=F('tarea__fecha_entrega')
        ).count()
        
        # Promedio de cuestionarios por curso
        intentos_por_curso = Intento.objects.values(
            'cuestionario__clase__curso__nombre'
        ).annotate(
            promedio=Avg('puntaje'),
            count=Count('id')
        )
        
        return {
            'asistencia_por_estado': list(asistencias_por_estado),
            'cursos_por_estado': list(cursos_por_estado),
            'resultados_finales': list(resultados),
            'entregas_tareas': {
                'a_tiempo': entregas_a_tiempo,
                'tardia': entregas_tardia,
            },
            'promedio_cuestionarios_por_curso': list(intentos_por_curso),
        }
