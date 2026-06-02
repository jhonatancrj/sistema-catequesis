def verificar_aprobacion(faltas, prom_tareas, prom_cuestionarios):
    if faltas < 3 and prom_tareas >= 51 and prom_cuestionarios >= 51:
        return True
    return False