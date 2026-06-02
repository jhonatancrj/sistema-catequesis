from django import forms

from .models import Cuestionario
from .models import Pregunta
from .models import Opcion


class CuestionarioForm(forms.ModelForm):

    class Meta:

        model = Cuestionario

        fields = [

            'titulo',
            'descripcion',
            'clase',

            'tiempo_limite',
            'es_unico',

            'fecha_limite'

        ]

        widgets = {

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

            'clase': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'tiempo_limite': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'es_unico': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'fecha_limite': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            )

        }


class PreguntaForm(forms.ModelForm):

    class Meta:

        model = Pregunta

        fields = [

            'enunciado',
            'tipo',
            'puntaje',
            'retroalimentacion'

        ]

        widgets = {

            'enunciado': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),

            'tipo': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'puntaje': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'retroalimentacion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            )

        }


class OpcionForm(forms.ModelForm):

    class Meta:

        model = Opcion

        fields = [

            'texto',
            'es_correcta'

        ]

        widgets = {

            'texto': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'es_correcta': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            )

        }