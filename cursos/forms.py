from django import forms
from django.utils.timezone import now

from .models import Curso, Clase, Inscripcion
from usuarios.models import Perfil
from sacramentos.models import Sacramento

class CursoForm(forms.ModelForm):

    # 🔹 CATEQUISTAS
    catequistas = forms.ModelMultipleChoiceField(

        queryset=Perfil.objects.filter(
            rol='CATEQUISTA'
        ),

        widget=forms.CheckboxSelectMultiple,

        required=False
    )

    # 🔹 DÍAS DE CLASES
    DIAS = (
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo'),
    )

    dias_clase = forms.MultipleChoiceField(

        choices=DIAS,

        widget=forms.CheckboxSelectMultiple,

        required=True,

        label='Días de clases'
    )

    # 🔹 HORARIOS
    hora_inicio_clase = forms.TimeField(

        widget=forms.TimeInput(
            attrs={'type': 'time'}
        ),

        label='Hora inicio'
    )

    hora_fin_clase = forms.TimeField(

        widget=forms.TimeInput(
            attrs={'type': 'time'}
        ),

        label='Hora fin'
    )

    # 🔹 DESCRIPCIÓN GENERAL CLASES
    descripcion_clase = forms.CharField(

        widget=forms.Textarea(
            attrs={'rows': 3}
        ),

        required=False,

        label='Descripción general de clases'
    )

    class Meta:

        model = Curso

        fields = [

            'nombre',
            'imagen',
            'descripcion',
            'sacramento',

            'fecha_inicio',
            'fecha_fin',
            'fecha_limite_inscripcion',

            'estado',

            'catequistas'
        ]

        widgets = {

            'fecha_inicio': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'fecha_fin': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'fecha_limite_inscripcion': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'descripcion': forms.Textarea(
                attrs={'rows': 5}
            ),
            'sacramento': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

        }

    # 🔹 VALIDACIONES
    def clean(self):

        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get(
            'fecha_inicio'
        )

        fecha_fin = cleaned_data.get(
            'fecha_fin'
        )

        fecha_limite = cleaned_data.get(
            'fecha_limite_inscripcion'
        )

        hora_inicio = cleaned_data.get(
            'hora_inicio_clase'
        )

        hora_fin = cleaned_data.get(
            'hora_fin_clase'
        )

        dias = cleaned_data.get(
            'dias_clase'
        )

        hoy = now().date()

        # 🔹 VALIDAR FECHAS PASADAS

        if fecha_inicio and fecha_inicio < hoy:

            self.add_error(

                'fecha_inicio',

                'La fecha de inicio no puede ser anterior a la fecha actual.'

            )

        if fecha_fin and fecha_fin < hoy:

            self.add_error(

                'fecha_fin',

                'La fecha finalización no puede ser anterior a la fecha actual.'

            )

        if fecha_limite and fecha_limite < hoy:

            self.add_error(

                'fecha_limite_inscripcion',

                'La fecha límite de inscripción no puede ser anterior a la fecha actual.'

            )

        # 🔹 VALIDAR ORDEN DE FECHAS

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:

                self.add_error(

                    'fecha_fin',

                    'La fecha finalización debe ser mayor a la fecha inicio.'

                )

        if fecha_limite and fecha_inicio:

            if fecha_limite < fecha_inicio:

                self.add_error(

                    'fecha_limite_inscripcion',

                    'La fecha límite de inscripción debe ser igual o posterior al inicio del curso.'

                )

        # 🔹 VALIDAR HORARIOS

        if hora_inicio and hora_fin:

            if hora_fin <= hora_inicio:

                self.add_error(

                    'hora_fin_clase',

                    'La hora fin debe ser mayor a la hora inicio.'

                )

        # 🔹 VALIDAR DÍAS

        if not dias:

            self.add_error(

                'dias_clase',

                'Debe seleccionar al menos un día de clases.'

            )

        return cleaned_data

class ClaseForm(forms.ModelForm):

    class Meta:

        model = Clase

        fields = [

            'curso',
            'titulo',
            'descripcion',
            'fecha',
            'hora_inicio',
            'hora_fin'

        ]

        widgets = {

            'curso': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'titulo': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5
                }
            ),

            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'hora_inicio': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),

            'hora_fin': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            )

        }

class InscripcionForm(forms.ModelForm):

    class Meta:

        model = Inscripcion

        fields = [

            'participante',
            'curso',
            'estado'

        ]

        widgets = {

            'participante': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'curso': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'estado': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            )

        }

    def clean(self):

        cleaned_data = super().clean()

        participante = cleaned_data.get(
            'participante'
        )

        curso = cleaned_data.get(
            'curso'
        )

        if Inscripcion.objects.filter(
            participante=participante,
            curso=curso
        ).exists():

            raise forms.ValidationError(
                'El participante ya está inscrito en este curso.'
            )

        return cleaned_data