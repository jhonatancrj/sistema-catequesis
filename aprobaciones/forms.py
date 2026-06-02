from django import forms

from .models import ResultadoCurso

from usuarios.models import Perfil


class AprobadoManualForm(forms.ModelForm):

    class Meta:

        model = ResultadoCurso

        fields = [

            'participante',

            'curso',

            'gestion',

            'sacramento',

            'promedio_tareas',

            'promedio_cuestionarios',

            'faltas',

            'estado_final'
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

            'gestion': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'sacramento': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'promedio_tareas': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'promedio_cuestionarios': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'faltas': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'estado_final': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            'participante'
        ].queryset = Perfil.objects.filter(
            rol='PARTICIPANTE'
        )

        self.fields[
            'participante'
        ].required = False

        self.fields[
            'curso'
        ].required = False

    # ===================================
    # VALIDACIÓN
    # ===================================

    def clean(self):

        cleaned_data = super().clean()

        participante = cleaned_data.get(
            'participante'
        )

        nombre_manual = cleaned_data.get(
            'nombre_manual'
        )

        apellido_manual = cleaned_data.get(
            'apellido_manual'
        )

        # ===============================
        # VALIDAR UNO DE LOS DOS
        # ===============================

        if (

            not participante

            and

            not nombre_manual

        ):

            raise forms.ValidationError(

                'Debe seleccionar un participante '
                'o escribir un nombre manual.'

            )

        # ===============================
        # SI HAY NOMBRE
        # TAMBIÉN APELLIDO
        # ===============================

        if (

            nombre_manual

            and

            not apellido_manual

        ):

            raise forms.ValidationError(

                'Debe ingresar apellido manual.'

            )

        return cleaned_data



from sacramentos.models import RegistroSacramental


class RegistroSacramentalForm(forms.ModelForm):

    class Meta:

        model = RegistroSacramental

        fields = [

            'fecha_sacramento',

            'lugar_sacramento',

            'parroco',

            'fecha_bautizo',

            'nombre_padre',

            'nombre_madre',

            'padrino',

            'madrina',
        ]

        widgets = {

            'fecha_sacramento': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'fecha_bautizo': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }