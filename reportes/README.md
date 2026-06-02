# 📊 Sistema de Reportes - Guía Completa

## 🎯 ¿Qué se ha creado?

Se implementó un **módulo de reportes profesional y completo** con:

### 1. **Dashboard Principal** 📈
- Estadísticas generales del sistema
- Gráficas interactivas (Pie Charts y Bar Charts)
- Métricas de asistencia, tareas y cuestionarios
- Tarjetas de estadísticas con diseño moderno
- Exportación a PDF

### 2. **Reportes Específicos** 📋
- **Cursos**: Análisis detallado de cada curso con participantes, asistencia, tareas y aprobaciones
- **Participantes**: Desempeño individual, asistencia, entregas de tareas
- **Catequistas**: Carga de trabajo, cursos asignados, desempeño de estudiantes
- **Tareas**: Entregas a tiempo/tardías, calificaciones promedio
- **Cuestionarios**: Desempeño en evaluaciones, puntajes mínimo/máximo/promedio
- **Aprobaciones**: Estado final de participantes (Aprobado/Reprobado)

### 3. **Características Principales** ✨
- **Gráficas Interactivas**: Usando Chart.js
- **Exportación a PDF**: Con diseño profesional
- **Filtros y Búsqueda**: Ordenamiento y filtrado de datos
- **Tablas Responsivas**: Se adaptan a dispositivos móviles
- **Diseño Profesional**: Gradientes, colores corporativos, iconos Bootstrap
- **Paginación y Rendimiento**: Optimizado para grandes volúmenes de datos

---

## 🚀 Instalación y Configuración

### Paso 1: Actualizar imports en settings.py ✅
Ya está hecho. Se agregó `'reportes'` a INSTALLED_APPS

### Paso 2: Actualizar URLs principales ✅
Ya está hecho. Se incluyeron las URLs en `sistema_catequesis/urls.py`

### Paso 3: Actualizar base_admin.html ✅
Ya está hecho. Se agregó el menú de Reportes en el sidebar

### Paso 4: Instalar dependencias ✅
```bash
pip install reportlab  # Ya instalado
```

---

## 📁 Estructura de Archivos Creados

```
reportes/
├── migrations/
│   └── __init__.py
├── templates/
│   └── reportes/
│       ├── dashboard.html          # Dashboard principal con gráficas
│       ├── cursos.html             # Reporte de cursos
│       ├── curso_detallado.html    # Reporte detallado por curso
│       ├── participantes.html      # Reporte de participantes
│       ├── catequistas.html        # Reporte de catequistas
│       ├── tareas.html             # Reporte de tareas
│       ├── cuestionarios.html      # Reporte de cuestionarios
│       └── aprobaciones.html       # Reporte de aprobaciones
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── services.py                     # Servicios para obtener datos
├── urls.py                         # Rutas de la app
├── views.py                        # Vistas principales
└── tests.py
```

---

## 🔗 URLs Disponibles

```
/reportes/                          # Dashboard
/reportes/cursos/                   # Reporte de cursos
/reportes/cursos/<id>/              # Reporte detallado de curso
/reportes/participantes/            # Reporte de participantes
/reportes/catequistas/              # Reporte de catequistas
/reportes/tareas/                   # Reporte de tareas
/reportes/cuestionarios/            # Reporte de cuestionarios
/reportes/aprobaciones/             # Reporte de aprobaciones

# APIs para gráficas (JSON)
/reportes/api/graficas/dashboard/
/reportes/api/graficas/cursos/

# Exportación a PDF
/reportes/pdf/dashboard/
/reportes/pdf/cursos/
/reportes/pdf/participantes/
```

---

## 📊 Datos que se Muestran

### Dashboard
- Total de cursos (activos/inactivos)
- Total de participantes y catequistas
- Asistencia (Presente/Ausente/Permiso)
- Entregas de tareas (entregadas/pendientes)
- Cuestionarios (promedio de puntaje)
- Aprobaciones vs Reprobaciones

### Cursos
- Nombre y estado del curso
- Fechas de inicio/fin
- Número de participantes inscritos
- Porcentaje de asistencia
- Entregas de tareas
- Promedio de cuestionarios
- Tasa de aprobación

### Participantes
- Nombre y email
- Cursos inscritos
- Asistencia por curso
- Tareas entregadas
- Promedio de cuestionarios
- Aprobaciones y reprobaciones

### Catequistas
- Especialidad y experiencia
- Cursos asignados
- Clases dictadas
- Total de participantes
- Tareas creadas y entregas
- Promedio de desempeño de estudiantes

### Tareas
- Título y descripción
- Curso y catequista
- Entregas a tiempo y tardia
- Calificaciones promedio

### Cuestionarios
- Título y descripción
- Total de intentos
- Puntaje promedio/máximo/mínimo

### Aprobaciones
- Participante y curso
- Promedio de tareas y cuestionarios
- Faltas registradas
- Estado final (Aprobado/Reprobado)

---

## 🎨 Diseño y Estilos

- **Colores**: Gradientes modernos (azul, verde, rojo, naranja, púrpura)
- **Tipografía**: Poppins (Google Fonts)
- **Framework**: Bootstrap 5.3
- **Iconos**: Bootstrap Icons
- **Gráficas**: Chart.js 4.4
- **Responsivo**: Diseñado para desktop, tablet y móvil

---

## 🔐 Seguridad

- Los reportes requieren estar **logeado**
- Solo **administradores** pueden acceder (`@rol_requerido('ADMIN')`)
- Decoradores personalizados en el sistema

---

## 📈 Gráficas Interactivas

El dashboard incluye:

1. **Gráfica de Asistencia** (Doughnut)
   - Distribución: Presente/Ausente/Permiso

2. **Gráfica de Resultados** (Doughnut)
   - Distribución: Aprobados/Reprobados

3. **Gráfica de Tareas** (Doughnut)
   - Distribución: Entregadas/Pendientes

4. **Gráficas de Cursos** (Bar + Line)
   - Inscripciones por curso
   - Asistencia por curso

---

## 📝 Exportación a PDF

Se pueden descargar reportes en PDF con:

- Formato profesional
- Tablas con bordes y colores
- Estadísticas resumidas
- Fecha de generación
- Logotipo (puedes agregar)

**Ubicaciones de descarga**:
```
/reportes/pdf/dashboard/       → PDF del dashboard
/reportes/pdf/cursos/          → PDF de todos los cursos
/reportes/pdf/participantes/   → PDF de participantes
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Terminal
```bash
cd sistema_catequesis
python manage.py runserver
```

Luego accede a: `http://localhost:8000/reportes/`

### Opción 2: VS Code
- Presiona `F5` o ve a Run → Start Debugging
- Accede a `http://localhost:8000/reportes/`

---

## ✅ Funcionalidades Adicionales

### Búsqueda y Filtros
- Buscar participantes por nombre
- Filtrar cursos por estado (Activo/Inactivo/Finalizado)
- Filtrar aprobaciones por estado

### Ordenamiento
- Ordenar participantes por asistencia
- Ordenar por aprobaciones

### Tabla Responsiva
- Scroll horizontal en móvil
- Columnas adaptables
- Colores de estado (Aprobado=Verde, Reprobado=Rojo)

---

## 🔧 Personalizaciones Futuras

Puedes agregar:

1. **Filtros por rango de fechas**
   ```python
   fecha_inicio = request.GET.get('fecha_inicio')
   fecha_fin = request.GET.get('fecha_fin')
   ```

2. **Exportación a Excel/CSV**
   ```bash
   pip install openpyxl
   ```

3. **Reportes por email**
   ```python
   from django.core.mail import send_mail
   ```

4. **Gráficas adicionales**
   - Evolución de asistencia en el tiempo
   - Comparación entre cursos
   - Análisis por sacramento

5. **Descarga de datos en formato Excel/CSV**

---

## 🐛 Troubleshooting

### Error: "No module named 'reportes'"
- Asegúrate que `'reportes'` esté en INSTALLED_APPS
- Reinicia el servidor

### Las gráficas no aparecen
- Verifica que Chart.js se cargue correctamente
- Abre la consola del navegador (F12) y busca errores

### PDF con caracteres raros
- ReportLab tiene limitaciones con algunos caracteres
- Usa fuentes estándar (Helvetica, Times, Courier)

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa la consola del servidor Django
2. Abre la consola del navegador (F12)
3. Verifica que todos los modelos tengan datos
4. Comprueba permisos de la base de datos

---

## 📄 Licencia

Este sistema de reportes fue creado específicamente para tu sistema de catequesis. Úsalo libremente y personalízalo según necesites.

**¡Espero que te sea útil!** 🎉
