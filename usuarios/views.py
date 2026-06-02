from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import RegistroForm, EditarAdministradorForm
from .models import Perfil
from django.contrib.auth.models import Group
from django.contrib import messages

##entrar y salir
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(redireccion_por_rol(user))
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')

##registro de usuarios
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistroForm
from .models import Perfil

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False  # 🔒 NO puede iniciar sesión aún
            user.save()

            perfil = user.perfil  # 👈 ya existe por el signal

            perfil.genero = form.cleaned_data.get('genero')
            perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
            perfil.telefono = form.cleaned_data.get('telefono')
            perfil.pais = form.cleaned_data.get('pais')
            perfil.departamento = form.cleaned_data.get('departamento')
            perfil.ciudad = form.cleaned_data.get('ciudad')

            perfil.save() # rol PARTICIPANTE automático

            current_site = get_current_site(request)
            subject = 'Activa tu cuenta'
            message = render_to_string('usuarios/activar_cuenta.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                subject,
                message,
                'noreply@parroquia.com',
                [user.email],
            )
           
            return render(request, 'usuarios/registro_exitoso.html')

    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import EditarMiPerfilForm


@login_required
def editar_mi_perfil(request):

    perfil = request.user.perfil

    if request.method == 'POST':

        form = EditarMiPerfilForm(
            request.POST,
            instance=perfil,
            user_instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Perfil actualizado correctamente'
            )

            return redirect('editar_mi_perfil')

    else:

        form = EditarMiPerfilForm(
            instance=perfil,
            user_instance=request.user
        )

    return render(
        request,
        'usuarios/editar_mi_perfil.html',
        {
            'form': form,
            'perfil': perfil
        }
    )

def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'usuarios/activacion_invalida.html')
    

from django.conf import settings

def password_reset_request(request):
    if request.method == "POST":
        dato = request.POST.get("dato")

        try:
            user = User.objects.get(email=dato)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=dato)
            except User.DoesNotExist:
                user = None

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            enlace = request.build_absolute_uri(
                f"/usuarios/reset/{uid}/{token}/"
            )

            mensaje = render_to_string("usuarios/password_reset_email.html", {
                "user": user,
                "enlace": enlace
            })

            send_mail(
                "Recuperación de contraseña",
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

        # 🔒 Mensaje genérico (seguridad)
        messages.success(
            request,
            "Si los datos son correctos, se enviará un correo con instrucciones."
        )
        return redirect("login")

    return render(request, "usuarios/password_reset_form.html")

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 == password2:
                user.password = make_password(password1)
                user.save()
                messages.success(request, "Contraseña actualizada correctamente")
                return redirect("login")
            else:
                messages.error(request, "Las contraseñas no coinciden")

        return render(request, "usuarios/password_reset_confirm.html")

    messages.error(request, "El enlace no es válido o ya fue usado")
    return redirect("login")

# redireccion por roles
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def panel_catequista(request):
    if request.user.perfil.rol != 'CATEQUISTA':
        return redirect('login')
    return redirect('home')

@login_required
def panel_participante(request):
    if request.user.perfil.rol != 'PARTICIPANTE':
        return redirect('login')
    return redirect('home')

def redireccion_por_rol(user):
    # ESTO ES PARA EL  ADMIN PUEDA ENTRAR A LA PAGINA DE FORMA NORMAL SI ES QUE NO PUEDE
    #perfil, creado = Perfil.objects.get_or_create(
    #    user=user,
    #    defaults={'rol': 'ADMIN' if user.is_superuser else 'PARTICIPANTE'}
    #)
    if user.perfil.rol == 'ADMIN':
        return 'panel_admin'
    elif user.perfil.rol == 'CATEQUISTA':
        return 'panel_catequista'
    else:
        return 'panel_participante'

#qr asistencia



##___________________________________________________________________________

from django.contrib.auth.models import User
from .models import Perfil


@login_required
def lista_administradores(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    administradores = Perfil.objects.filter(
        rol='ADMIN'
    ).select_related('user')

    perfiles = Perfil.objects.select_related(
        'user'
    )

    context = {
        'administradores': administradores,
        'perfiles': perfiles
    }

    return render(
        request,
        'usuarios/administradores/lista.html',
        context
    )

@login_required
def crear_administrador(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        perfil_id = request.POST.get('perfil_id')

        try:

            perfil = Perfil.objects.get(id=perfil_id)

            perfil.rol = 'ADMIN'
            perfil.save()

            messages.success(
                request,
                'Administrador agregado correctamente.'
            )

        except Perfil.DoesNotExist:

            messages.error(
                request,
                'Usuario no encontrado.'
            )

    return redirect('lista_administradores')

@login_required
def editar_administrador(request, perfil_id):
    
    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    if request.method == 'POST':

        form = EditarAdministradorForm(
            request.POST,
            instance=perfil,
            user_instance=perfil.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Administrador actualizado correctamente.'
            )

            return redirect(
                'lista_administradores'
            )

    else:

        form = EditarAdministradorForm(
            instance=perfil,
            user_instance=perfil.user
        )

    context = {
        'form': form,
        'perfil': perfil
    }

    return render(
        request,
        'usuarios/administradores/editar.html',
        context
    )

@login_required
def eliminar_administrador(request, perfil_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    # Evitar quitarse a sí mismo
    if perfil.user == request.user:

        messages.error(
            request,
            'No puedes quitarte tu propio rol.'
        )

        return redirect(
            'lista_administradores'
        )

    perfil.rol = 'PARTICIPANTE'
    perfil.save()

    messages.success(
        request,
        'Administrador removido correctamente.'
    )

    return redirect(
        'lista_administradores'
    )

@login_required
def lista_catequistas(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    catequistas = Perfil.objects.filter(
        rol='CATEQUISTA'
    ).select_related('user')

    perfiles = Perfil.objects.select_related(
        'user'
    )

    context = {
        'catequistas': catequistas,
        'perfiles': perfiles
    }

    return render(
        request,
        'usuarios/catequistas/lista.html',
        context
    )

@login_required
def crear_catequista(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        perfil_id = request.POST.get('perfil_id')

        try:

            perfil = Perfil.objects.get(id=perfil_id)

            perfil.rol = 'CATEQUISTA'
            perfil.save()

            messages.success(
                request,
                'Catequista agregado correctamente.'
            )

        except Perfil.DoesNotExist:

            messages.error(
                request,
                'Usuario no encontrado.'
            )

    return redirect('lista_catequistas')

@login_required
def editar_catequista(request, perfil_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    if request.method == 'POST':

        form = EditarAdministradorForm(
            request.POST,
            instance=perfil,
            user_instance=perfil.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Catequista actualizado correctamente.'
            )

            return redirect(
                'lista_catequistas'
            )

    else:

        form = EditarAdministradorForm(
            instance=perfil,
            user_instance=perfil.user
        )

    context = {
        'form': form,
        'perfil': perfil
    }

    return render(
        request,
        'usuarios/catequistas/editar.html',
        context
    )

@login_required
def eliminar_catequista(request, perfil_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    perfil.rol = 'PARTICIPANTE'
    perfil.save()

    messages.success(
        request,
        'Catequista removido correctamente.'
    )

    return redirect(
        'lista_catequistas'
    )

@login_required
def lista_participantes(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    participantes = Perfil.objects.filter(
        rol='PARTICIPANTE'
    ).select_related('user')

    perfiles = Perfil.objects.select_related(
        'user'
    )

    context = {
        'participantes': participantes,
        'perfiles': perfiles
    }

    return render(
        request,
        'usuarios/participantes/lista.html',
        context
    )

@login_required
def editar_participante(request, perfil_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    if request.method == 'POST':

        form = EditarAdministradorForm(
            request.POST,
            instance=perfil,
            user_instance=perfil.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Participante actualizado correctamente.'
            )

            return redirect(
                'lista_participantes'
            )

    else:

        form = EditarAdministradorForm(
            instance=perfil,
            user_instance=perfil.user
        )

    context = {
        'form': form,
        'perfil': perfil
    }

    return render(
        request,
        'usuarios/participantes/editar.html',
        context
    )

@login_required
def toggle_estado_participante(request, perfil_id):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    perfil = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    user = perfil.user

    user.is_active = not user.is_active

    user.save()

    if user.is_active:

        messages.success(
            request,
            'Cuenta activada correctamente.'
        )

    else:

        messages.success(
            request,
            'Cuenta desactivada correctamente.'
        )

    return redirect(
        'lista_participantes'
    )

@login_required
def crear_participante(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':

        form = RegistroForm(request.POST)

        if form.is_valid():

            # CREAR USUARIO
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # ACTUALIZAR PERFIL YA CREADO
            perfil = user.perfil

            perfil.rol = 'PARTICIPANTE'
            perfil.genero = form.cleaned_data['genero']
            perfil.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            perfil.telefono = form.cleaned_data['telefono']
            perfil.pais = form.cleaned_data['pais']
            perfil.departamento = form.cleaned_data['departamento']
            perfil.ciudad = form.cleaned_data['ciudad']

            perfil.save()

            messages.success(
                request,
                'Participante creado correctamente.'
            )

            return redirect(
                'lista_participantes'
            )

    else:

        form = RegistroForm()

    context = {
        'form': form
    }

    return render(
        request,
        'usuarios/participantes/crear.html',
        context
    )


from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

from cursos.models import (
    Curso,
    Inscripcion,
    Asistencia
)

from tareas.models import (
    Tarea,
    EntregaTarea
)

from cuestionario.models import (
    Cuestionario
)

from aprobaciones.models import (
    ResultadoCurso
)

from usuarios.models import Perfil

@login_required
def panel_admin(request):

    if request.user.perfil.rol != 'ADMIN':
        return redirect('login')

    # =====================================
    # CONTADORES
    # =====================================

    total_participantes = Perfil.objects.filter(
        rol='PARTICIPANTE'
    ).count()

    total_catequistas = Perfil.objects.filter(
        rol='CATEQUISTA'
    ).count()

    total_cursos = Curso.objects.count()

    total_tareas = Tarea.objects.count()

    total_cuestionarios = Cuestionario.objects.count()

    total_aprobados = ResultadoCurso.objects.count()

    # =====================================
    # CURSOS ACTIVOS
    # =====================================

    cursos_activos = Curso.objects.filter(
        estado='ACTIVO'
    )[:5]

    # =====================================
    # ÚLTIMOS PARTICIPANTES
    # =====================================

    ultimos_participantes = Perfil.objects.filter(
        rol='PARTICIPANTE'
    ).order_by('-fecha_registro')[:5]

    # =====================================
    # ESTADÍSTICAS MENSUALES
    # =====================================

    meses = [
        'Ene',
        'Feb',
        'Mar',
        'Abr',
        'May',
        'Jun',
        'Jul',
        'Ago',
        'Sep',
        'Oct',
        'Nov',
        'Dic'
    ]

    participantes_por_mes = []

    año_actual = now().year

    for mes in range(1, 13):

        cantidad = Perfil.objects.filter(
            rol='PARTICIPANTE',
            fecha_registro__year=año_actual,
            fecha_registro__month=mes
        ).count()

        participantes_por_mes.append(cantidad)

    # =====================================
    # CURSOS POR SACRAMENTO
    # =====================================

    sacramentos = Curso.objects.values(
        'sacramento__nombre'
    ).annotate(
        total=Count('id')
    )

    labels_sacramentos = []
    datos_sacramentos = []

    for s in sacramentos:

        labels_sacramentos.append(
            s['sacramento__nombre']
            or 'Sin sacramento'
        )

        datos_sacramentos.append(
            s['total']
        )

    # =====================================
    # ACTIVIDAD RECIENTE
    # =====================================

    actividades = []

    nuevos = Perfil.objects.order_by(
        '-fecha_registro'
    )[:5]

    for n in nuevos:

        actividades.append({

            'texto': (
                f'{n.user.first_name} '
                f'{n.user.last_name} '
                f'se registró'
            ),

            'fecha': n.fecha_registro,

            'icono': 'bi-person-plus',

            'color': 'blue-bg'
        })

    # =====================================
    # CONTEXTO
    # =====================================

    context = {

        'total_participantes': total_participantes,

        'total_catequistas': total_catequistas,

        'total_cursos': total_cursos,

        'total_tareas': total_tareas,

        'total_cuestionarios': total_cuestionarios,

        'total_aprobados': total_aprobados,

        'cursos_activos': cursos_activos,

        'ultimos_participantes': ultimos_participantes,

        'meses': meses,

        'participantes_por_mes': participantes_por_mes,

        'labels_sacramentos': labels_sacramentos,

        'datos_sacramentos': datos_sacramentos,

        'actividades': actividades,
    }

    return render(
        request,
        'usuarios/panel_admin.html',
        context
    )

